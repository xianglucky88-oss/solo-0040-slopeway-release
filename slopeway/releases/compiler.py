from .envelope import seal
from ..errors import bad
from ..evaluation.chronology import release_window
from ..evaluation.index import compile_index
from ..evaluation.profiles import PROFILES
from ..fields import integer, key, shape
from ..storage import feed_store, release_store, topology_store

RECORD_LIMIT = 20000


def compile_release(connection, payload):
    shape(payload, '编译请求', ('district', 'revision', 'start', 'end', 'cutoff'))
    district = key(payload['district'], '片区编号')
    revision = integer(payload['revision'], '拓扑修订号', 1, 2**31 - 1)
    start, end, cutoff = release_window(payload['start'], payload['end'], payload['cutoff'])
    topology = topology_store.read(connection, district, revision)
    feeds = feed_store.at_cutoff(connection, district, revision, cutoff)
    if sum(len(feed['records']) for feed in feeds) > RECORD_LIMIT:
        raise bad('该修订的入选证据超出单件容量，请使用较早截点或整理分区拓扑。', maximum=RECORD_LIMIT)
    body = {
        'meta': {'district': district, 'revision': revision, 'start': start, 'end': end, 'cutoff': cutoff},
        'topology': topology,
        'policy': PROFILES,
        'feeds': feeds,
        'index': compile_index(feeds, start, end),
    }
    release = seal(body)
    created = release_store.save(connection, release)
    return {'id': release['id'], 'sha256': release['sha256'], 'created': created,
            'meta': body['meta'], 'feed_count': len(feeds)}
