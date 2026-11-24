from ..errors import missing
from ..releases import channels, preview
from ..storage import channel_store, release_store
from ..fields import shape
from .response import Download
from ..releases.envelope import verify
from ..errors import conflict


def history(connection, params, *_):
    params = (params['district'], params['channel'])
    return {'head': channel_store.head(connection, *params), 'events': channel_store.history(connection, *params)}


def move(connection, params, query, payload):
    return 201, channels.move(connection, params['district'], params['channel'], payload)


def _current(connection, params):
    head = channel_store.head(connection, params['district'], params['channel'])
    if head['release_id'] is None:
        raise missing('此渠道尚未发布。')
    return head, release_store.read(connection, head['release_id'])


def route(connection, params, query, _):
    shape(query, '渠道路线参数', ('at', 'profile', 'origin', 'target'))
    head, release = _current(connection, params)
    return {'head': head, **preview.route(release, **query)}


def export(connection, params, *_):
    head, release = _current(connection, params)
    if not verify(release)['verified']:
        raise conflict('渠道发布件未通过完整性复核。')
    return Download({'head': head, 'release': release}, f"slopeway-{params['channel']}-{head['generation']}.json")
