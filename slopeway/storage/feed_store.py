import json

from ..encoding import canonical, digest
from ..errors import conflict


def save(connection, batch):
    fingerprint = digest(batch)
    identity = (batch['district'], batch['revision'], batch['source'], batch['batch'])
    existing = connection.execute('''
        SELECT digest FROM feeds WHERE district = ? AND revision = ? AND source = ? AND batch = ?
    ''', identity).fetchone()
    if existing is not None and existing['digest'] != fingerprint:
        raise conflict('批次编号已登记不同内容。', batch=batch['batch'], source=batch['source'])
    if existing is None:
        connection.execute('INSERT INTO feeds VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
            *identity, batch['kind'], batch['reported_at'], canonical(batch), fingerprint,
        ))
    return {'batch': batch['batch'], 'kind': batch['kind'], 'count': len(batch['records']),
            'digest': fingerprint, 'replayed': existing is not None}


def _feed(row):
    return {**json.loads(row['payload']), 'digest': row['digest']}


def at_cutoff(connection, district, revision, cutoff):
    return [_feed(row) for row in connection.execute('''
        SELECT payload, digest FROM feeds WHERE district = ? AND revision = ? AND reported_at <= ?
        ORDER BY source, batch
    ''', (district, revision, cutoff))]


def catalog(connection, district, revision):
    rows = connection.execute('''
        SELECT payload, digest FROM feeds WHERE district = ? AND revision = ?
        ORDER BY reported_at DESC, source, batch
    ''', (district, revision))
    return [
        {name: feed[name] for name in ('batch', 'kind', 'source', 'reported_at', 'digest')}
        | {'count': len(feed['records'])} for feed in map(_feed, rows)
    ]
