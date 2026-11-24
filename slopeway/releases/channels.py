from datetime import UTC, datetime

from ..errors import bad, conflict
from ..fields import choice, integer, shape, text
from ..storage import channel_store, release_store
from .envelope import verify

CHANNELS = ('field', 'public')


def state(connection, district):
    return {channel: channel_store.head(connection, district, channel) for channel in CHANNELS}


def move(connection, district, channel, payload):
    shape(payload, '渠道切换', ('release', 'generation', 'action', 'note'))
    release_id = key_for_release(payload['release'])
    expected = integer(payload['generation'], '渠道代次', 0, 2**31 - 1)
    action = choice(payload['action'], '切换操作', ('publish', 'restore'))
    note = text(payload['note'], '交接说明')
    envelope = release_store.read(connection, release_id)
    if envelope['body']['meta']['district'] != district:
        raise bad('目标发布件属于另一片区。')
    if not verify(envelope)['verified']:
        raise conflict('目标发布件未通过完整性复核。', release=release_id)
    if action == 'restore':
        published = {row['release_id'] for row in channel_store.history(connection, district, channel)}
        if release_id not in published:
            raise conflict('该发布件没有出现在当前渠道的交接历史。', release=release_id)
    changed_at = datetime.now(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return channel_store.append(connection, district, channel, expected, release_id, action, note, changed_at)


def key_for_release(value):
    if not isinstance(value, str) or not value.startswith('sw-') or len(value) != 67:
        raise bad('发布件编号须包含完整指纹。')
    if any(character not in '0123456789abcdef' for character in value[3:]):
        raise bad('发布件编号包含无效指纹。')
    return value
