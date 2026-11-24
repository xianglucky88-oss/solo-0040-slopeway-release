from collections import Counter


def summarize(sections):
    operating = ('passable', 'restricted', 'closed', 'unknown', 'conflict')
    statuses = Counter(row['status'] for row in sections)
    evidence = Counter(row['evidence']['status'] for row in sections)
    gaps = [
        {'id': row['id'], 'segment': row['segment'], 'direction': row['direction'],
         'effective_status': row['status'], 'evidence_status': row['evidence']['status'],
         'references': row['evidence']['selected']}
        for row in sections if row['evidence']['status'] != 'resolved'
    ]
    return {
        'direction_count': len(sections),
        'statuses': {state: statuses[state] for state in operating},
        'evidence': {state: evidence[state] for state in ('resolved', 'unknown', 'conflict')},
        'gaps': gaps,
    }
