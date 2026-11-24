from .demo import DISTRICT, example

REVISION = DISTRICT + '/revisions/1'


def topology(api, *_):
    original = example('reedbank-topology')
    saved = api(REVISION)
    assert len(saved['nodes']) == 8 and len(saved['segments']) == 11
    api('/topologies', submit=original, expect=409)
    invalid = {**original, 'expected_revision': 1,
               'segments': [{**original['segments'][0], 'a': 'missing'}]}
    api('/topologies', submit=invalid, expect=422)
    changed = {**original, 'expected_revision': 1, 'label': '苇汀北岸'}
    assert api('/topologies', submit=changed, expect=201)['revision'] == 2
    assert api(REVISION)['digest'] == saved['digest']
    assert api(DISTRICT + '/revisions/2/feeds')['feeds'] == []


def survey(api, *_):
    sample = example('field-survey')
    records = api(REVISION + '/feeds')['feeds']
    feed = next(feed for feed in records if feed['batch'] == sample['batch'])
    shuffled = {**sample, 'records': list(reversed(sample['records']))}
    replay = api('/feeds', submit=shuffled)
    assert replay['replayed'] and replay['count'] == 20 and feed['digest'] == replay['digest']
    different = [{**sample['records'][0], 'width_mm': 1111}, *sample['records'][1:]]
    api('/feeds', submit={**sample, 'records': different}, expect=409)
    invalid_record = {**sample['records'][0], 'segment': 'unknown'}
    rejected = {**sample, 'batch': 'bad-survey', 'records': [sample['records'][1], invalid_record]}
    api('/feeds', submit=rejected, expect=422)
    assert api(REVISION + '/feeds')['feeds'] == records


def notice(api, *_):
    sample = example('closure-notice')
    records = api(REVISION + '/feeds')['feeds']
    assert any(row['batch'] == sample['batch'] and row['kind'] == 'notice' for row in records)
    row = sample['records'][0]
    api('/feeds', submit={**sample, 'source': 'community'}, expect=422)
    api('/feeds', submit={**sample, 'records': [{**row, 'until': row['from']}]}, expect=422)
    api('/feeds', submit={**sample, 'records': [{**row, 'segment': 'pier-bay', 'direction': 'both'}]}, expect=422)
    assert api(REVISION + '/feeds')['feeds'] == records
