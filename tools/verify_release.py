from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from .demo import PROFILE, PUBLIC, WORK, example
from .verify_route import TRAVEL
from slopeway.encoding import digest


def compile_release(api, early, latest):
    payload = example('release-window')
    replay = api('/releases', submit=payload)
    assert replay['id'] == latest and not replay['created']
    api('/releases', submit={**payload, 'cutoff': '2026-09-18T08:00:01Z'}, expect=422)
    early_meta, late_meta = (api(f'/releases/{id}') for id in (early, latest))
    assert early_meta['feed_count'] == 2 and late_meta['feed_count'] == 3
    incoming = example('closure-notice')
    api('/feeds', submit={**incoming, 'batch': 'follow-up', 'reported_at': '2026-09-18T07:58:00Z'}, expect=201)
    assert api('/releases', submit=payload)['id'] == latest
    assert api('/releases', submit={**payload, 'cutoff': '2026-09-18T08:00:00Z'}, expect=201)['feed_count'] == 4


def verify(api, early, latest):
    report = api(f'/releases/{latest}/verify')
    assert report['verified'] and all(report['checks'].values())
    content = api(f'/releases/{latest}/export')
    assert digest(content['body']) == content['sha256'] == report['sha256']
    assert all(row['reported_at'] <= content['body']['meta']['cutoff'] for row in content['body']['feeds'])
    assert all(row['digest'] == digest({k: v for k, v in row.items() if k != 'digest'}) for row in content['body']['feeds'])
    early_package = api(f'/releases/{early}/export')
    assert len(early_package['body']['feeds']) + 1 == len(content['body']['feeds'])


def _move(api, target, generation, action='publish', expect=201):
    payload = {'release': target, 'generation': generation, 'action': action, 'note': '工作流核验交接'}
    return api(PUBLIC, submit=payload, expect=expect)


def publish(api, early, latest):
    gate = Barrier(2, timeout=5)

    def submit(target):
        gate.wait()
        payload = {'release': target, 'generation': 0, 'action': 'publish', 'note': '并行发送的渠道交接'}
        try:
            return api(PUBLIC, submit=payload, expect=201)['release_id']
        except RuntimeError as error:
            if '返回 409' not in str(error):
                raise
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        winners = [item for item in pool.map(submit, (early, latest)) if item]
    assert len(winners) == 1
    head = api(PUBLIC)['head']
    assert head['generation'] == 1 and head['release_id'] == winners[0]
    export = api(PUBLIC + '/export')
    assert export['head'] == head and export['release']['id'] == head['release_id']
    routed = api(PUBLIC + '/route', query={**TRAVEL, 'at': WORK, 'profile': PROFILE})
    assert routed['head'] == head and routed['id'] == head['release_id']


def restore(api, early, latest):
    _move(api, early, 0, 'restore', 409)
    _move(api, early, 0)
    _move(api, latest, 1)
    assert _move(api, early, 2, 'restore')['generation'] == 3
    _move(api, latest, 2, expect=409)
    data = api(PUBLIC)
    assert [(row['generation'], row['action']) for row in data['events']] == [(3, 'restore'), (2, 'publish'), (1, 'publish')]
    result = api(PUBLIC + '/route', query={**TRAVEL, 'at': WORK, 'profile': PROFILE})
    assert result['distance_m'] == 410 and result['id'] == early
