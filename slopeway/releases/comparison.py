from .preview import overview
from ..errors import bad


def _semantic(row):
    if row is None:
        return None
    return {
        'endpoints': [row['start'], row['end']],
        'length_m': row['length_m'],
        'status': row['status'],
        'measurement': row['evidence'].get('measurement'),
        'selected': row['evidence']['selected'],
        'closures': row['closures'],
    }


def compare(before, after, at, profile):
    if before['body']['meta']['district'] != after['body']['meta']['district']:
        raise bad('只能比较同一片区的两个发布件。')
    left_view = overview(before, at, profile)
    right_view = overview(after, at, profile)
    left = {row['id']: _semantic(row) for row in left_view['sections']}
    right = {row['id']: _semantic(row) for row in right_view['sections']}
    changes = []
    for arc in sorted(left.keys() | right.keys()):
        old, new = left.get(arc), right.get(arc)
        if old == new:
            continue
        kind = 'added' if old is None else 'removed' if new is None else 'changed'
        changes.append({'arc': arc, 'kind': kind, 'before': old, 'after': new})
    return {'before': before['id'], 'after': after['id'], 'at': left_view['at'],
            'profile': profile, 'changes': changes}
