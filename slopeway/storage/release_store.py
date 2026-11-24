import json

from ..encoding import canonical
from ..errors import missing


def save(connection, envelope):
    meta = envelope['body']['meta']
    cursor = connection.execute('''
        INSERT INTO releases(id, district, revision, start, end, cutoff, envelope)
        VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING
    ''', (envelope['id'], meta['district'], meta['revision'], meta['start'], meta['end'],
          meta['cutoff'], canonical(envelope)))
    return cursor.rowcount == 1


def read(connection, release_id):
    row = connection.execute('SELECT envelope FROM releases WHERE id = ?', (release_id,)).fetchone()
    if row is None:
        raise missing('没有找到指定的发布件。')
    return json.loads(row['envelope'])


def catalog(connection, district):
    return [dict(row) for row in connection.execute('''
        SELECT id, revision, start, end, cutoff FROM releases WHERE district = ?
        ORDER BY cutoff DESC, id
    ''', (district,))]
