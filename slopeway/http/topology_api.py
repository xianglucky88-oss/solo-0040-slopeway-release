from ..catalog import available, district_channels
from ..fields import integer
from ..network import topology
from ..storage import topology_store


def catalog(connection, *_):
    return available(connection)


def revisions(connection, params, *_):
    return {'revisions': topology_store.revisions(connection, params['district'])}


def read(connection, params, *_):
    revision = integer(int(params['revision']), '拓扑修订号', 1, 2**31 - 1)
    return topology_store.read(connection, params['district'], revision)


def create(connection, params, query, payload):
    district, expected, value = topology.normalize(payload)
    return 201, topology_store.save(connection, district, expected, value)


def channels(connection, params, *_):
    return district_channels(connection, params['district'])
