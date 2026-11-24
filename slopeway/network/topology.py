from .arcs import DIRECTIONS
from ..errors import bad
from ..fields import choice, integer, key, rows, shape, text, unique


def _node(row):
    shape(row, '节点', ('id', 'label', 'x', 'y'))
    return {
        'id': key(row['id'], '节点编号'),
        'label': text(row['label'], '节点名称'),
        'x': integer(row['x'], '节点横坐标', 0, 10000),
        'y': integer(row['y'], '节点纵坐标', 0, 10000),
    }


def _segment(row, node_ids):
    shape(row, '街段', ('id', 'label', 'a', 'b', 'length_m', 'direction'))
    a, b = key(row['a'], 'A 端'), key(row['b'], 'B 端')
    if a == b or a not in node_ids or b not in node_ids:
        raise bad('街段须连接两个已登记的不同节点。', segment=row['id'])
    return {
        'id': key(row['id'], '街段编号'),
        'label': text(row['label'], '街段名称'),
        'a': a,
        'b': b,
        'length_m': integer(row['length_m'], '街段距离（米）', 1, 50000),
        'direction': choice(row['direction'], '街段方向', DIRECTIONS),
    }


def _assert_connected(nodes, segments):
    neighbors = {node['id']: set() for node in nodes}
    for segment in segments:
        a, b = segment['a'], segment['b']
        neighbors[a].add(b)
        neighbors[b].add(a)
    pending = [nodes[0]['id']]
    seen = set(pending)
    while pending:
        current = pending.pop()
        unseen = neighbors[current] - seen
        seen.update(unseen)
        pending.extend(unseen)
    if len(seen) < len(nodes):
        raise bad('同一片区的节点须在同一个连通分量中。', disconnected=sorted(neighbors.keys() - seen))


def normalize(payload):
    shape(payload, '拓扑修订', ('district', 'label', 'expected_revision', 'nodes', 'segments'))
    district = key(payload['district'], '片区编号')
    label = text(payload['label'], '片区名称')
    expected = integer(payload['expected_revision'], '当前修订号', 0, 2**31 - 1)
    nodes = [_node(row) for row in rows(payload['nodes'], '节点', 2, 400)]
    unique(nodes, 'id')
    node_ids = {row['id'] for row in nodes}
    segments = [_segment(row, node_ids) for row in rows(payload['segments'], '街段', 1, 1200)]
    unique(segments, 'id')
    _assert_connected(nodes, segments)
    return district, expected, {
        'label': label,
        'nodes': sorted(nodes, key=lambda row: row['id']),
        'segments': sorted(segments, key=lambda row: row['id']),
    }
