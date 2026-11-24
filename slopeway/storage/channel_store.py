from ..errors import conflict


def head(connection, district, channel):
    row = connection.execute('''
        SELECT generation, release_id, action, note, changed_at FROM channel_events
        WHERE district = ? AND channel = ? ORDER BY generation DESC LIMIT 1
    ''', (district, channel)).fetchone()
    return dict(row) if row else {'generation': 0, 'release_id': None}


def history(connection, district, channel):
    rows = connection.execute('''
        SELECT generation, release_id, action, note, changed_at FROM channel_events
        WHERE district = ? AND channel = ? ORDER BY generation DESC
    ''', (district, channel))
    return [dict(row) for row in rows]


def append(connection, district, channel, expected, release_id, action, note, changed_at):
    current = head(connection, district, channel)
    if expected != current['generation']:
        raise conflict('渠道代次已变更，请重新加载渠道。', expected=expected, current=current['generation'])
    if release_id == current['release_id']:
        raise conflict('目标发布件已在该渠道。', current=current['generation'])
    generation = expected + 1
    connection.execute('INSERT INTO channel_events VALUES (?, ?, ?, ?, ?, ?, ?)', (
        district, channel, generation, release_id, action, note, changed_at,
    ))
    return head(connection, district, channel)
