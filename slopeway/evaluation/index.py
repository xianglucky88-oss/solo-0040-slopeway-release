from collections import defaultdict

from .chronology import intersects
from ..network.arcs import directions


def compile_index(feeds, start, end):
    evidence = defaultdict(lambda: {'survey': [], 'notice': []})
    for feed in feeds:
        kind = feed['kind']
        for row in feed['records']:
            if not intersects(row['start'], row['end'], start, end):
                continue
            for direction in directions(row['direction']):
                entry = {
                    **row,
                    'direction': direction,
                    'rank': feed['rank'],
                    'reported_at': feed['reported_at'],
                    'ref': f"{feed['source']}/{feed['batch']}/{row['id']}",
                }
                evidence[f"{row['segment']}:{direction}"][kind].append(entry)
    return dict(evidence)


def entries(evidence, when):
    for entry in evidence:
        phase = 'future' if when < entry['start'] else 'expired' if when >= entry['end'] else 'effective'
        yield {**entry, 'phase': phase}
