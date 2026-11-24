from collections import defaultdict
from heapq import heappop, heappush


def _frontier(origin, target, neighbors):
    queue = [(0, (), origin)]
    best = {origin: (0, ())}
    while queue:
        distance, path, node = heappop(queue)
        if (distance, path) != best[node]:
            continue
        if node == target:
            return distance, path, set(best)
        for section in neighbors[node]:
            endpoint = section['end']
            candidate = (distance + section['length_m'], (*path, section['id']))
            if endpoint not in best or candidate < best[endpoint]:
                best[endpoint] = candidate
                heappush(queue, (*candidate, endpoint))
    return None, (), set(best)


def solve(sections, origin, target):
    neighbors = defaultdict(list)
    indexed = {}
    for section in sections:
        indexed[section['id']] = section
        if section['status'] == 'passable':
            neighbors[section['start']].append(section)
    distance, path, reached = _frontier(origin, target, neighbors)
    if distance is None:
        boundary = [row for row in sections if row['start'] in reached and row['end'] not in reached]
        return {'status': 'unreachable', 'origin': origin, 'target': target,
                'reachable': sorted(reached), 'boundary': boundary}
    return {'status': 'found', 'origin': origin, 'target': target,
            'distance_m': distance, 'steps': [indexed[arc] for arc in path]}
