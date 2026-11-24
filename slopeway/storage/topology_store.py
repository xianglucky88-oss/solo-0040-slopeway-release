import json

from ..encoding import canonical, digest
from ..errors import conflict, missing


def save(connection, district, expected, topology):
    current = connection.execute(
        'SELECT MAX(revision) FROM topologies WHERE district = ?', (district,),
    ).fetchone()[0] or 0
    if expected != current:
        raise conflict('拓扑已变更，请重新加载当前修订。', expected=expected, current=current)
    revision = current + 1
    fingerprint = digest(topology)
    connection.execute(
        'INSERT INTO topologies VALUES (?, ?, ?, ?)',
        (district, revision, canonical(topology), fingerprint),
    )
    return {'district': district, 'revision': revision, 'digest': fingerprint, **topology}


def _view(row):
    return {
        'district': row['district'], 'revision': row['revision'],
        'digest': row['digest'], **json.loads(row['payload']),
    }


def read(connection, district, revision):
    row = connection.execute(
        'SELECT * FROM topologies WHERE district = ? AND revision = ?', (district, revision),
    ).fetchone()
    if row is None:
        raise missing('指定片区的拓扑修订不存在。')
    return _view(row)


def revisions(connection, district):
    result = connection.execute(
        'SELECT * FROM topologies WHERE district = ? ORDER BY revision DESC', (district,),
    )
    return [
        {'district': row['district'], 'revision': row['revision'], 'digest': row['digest'],
         'label': json.loads(row['payload'])['label']}
        for row in result
    ]


def districts(connection):
    latest = connection.execute('''
        SELECT district, revision, payload FROM topologies AS t
        WHERE revision = (SELECT MAX(revision) FROM topologies WHERE district = t.district)
        ORDER BY district
    ''')
    return [
        {'id': row['district'], 'revision': row['revision'], 'label': json.loads(row['payload'])['label']}
        for row in latest
    ]
