from ..errors import conflict
from ..fields import shape
from ..releases import comparison, compiler, envelope, preview
from ..releases.channels import key_for_release
from ..storage import release_store
from .response import Download


def catalog(connection, params, *_):
    return {'releases': release_store.catalog(connection, params['district'])}


def create(connection, params, query, payload):
    release = compiler.compile_release(connection, payload)
    return (201 if release['created'] else 200), release


def _read(connection, params):
    return release_store.read(connection, params['release'])


def meta(connection, params, *_):
    release = _read(connection, params)
    body = release['body']
    return {'id': release['id'], 'sha256': release['sha256'], 'meta': body['meta'],
            'profiles': body['policy'], 'feed_count': len(body['feeds']), 'label': body['topology']['label']}


def overview(connection, params, query, _):
    shape(query, '预览参数', ('at', 'profile'))
    return preview.overview(_read(connection, params), query['at'], query['profile'])


def detail(connection, params, query, _):
    shape(query, '证据查询参数', ('at', 'profile'))
    return preview.trace(_read(connection, params), query['at'], query['profile'], params['arc'])


def route(connection, params, query, _):
    shape(query, '路线参数', ('at', 'profile', 'origin', 'target'))
    return preview.route(_read(connection, params), **query)


def compare(connection, params, query, _):
    shape(query, '比较参数', ('before', 'at', 'profile'))
    before = release_store.read(connection, key_for_release(query['before']))
    return comparison.compare(before, _read(connection, params), query['at'], query['profile'])


def verify(connection, params, *_):
    return envelope.verify(_read(connection, params))


def export(connection, params, *_):
    release = _read(connection, params)
    if not envelope.verify(release)['verified']:
        raise conflict('发布件未通过完整性复核。')
    return Download(release, f"slopeway-{release['sha256'][:16]}.json")
