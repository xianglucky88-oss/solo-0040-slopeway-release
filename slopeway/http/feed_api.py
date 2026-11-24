from ..fields import integer
from ..intake import batch
from ..storage import feed_store, topology_store


def catalog(connection, params, *_):
    district = params['district']
    revision = integer(int(params['revision']), '拓扑修订号', 1, 2**31 - 1)
    topology_store.read(connection, district, revision)
    return {'feeds': feed_store.catalog(connection, district, revision)}


def create(connection, params, query, payload):
    district, revision = batch.identity(payload)
    topology = topology_store.read(connection, district, revision)
    result = feed_store.save(connection, batch.normalize(payload, topology))
    return (200 if result['replayed'] else 201), result
