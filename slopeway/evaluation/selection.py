from .chronology import contains
from ..intake.survey import MEASURE_FIELDS


def _rank(item):
    return item['rank'], item['start']


def resolve(records, when):
    active = [entry for entry in records if contains(entry['start'], entry['end'], when)]
    if not active:
        return {'status': 'unknown', 'selected': [], 'superseded': []}
    winning_rank = max(map(_rank, active))
    best = [record for record in active if _rank(record) == winning_rank]
    superseded = [record['ref'] for record in active if _rank(record) < winning_rank]
    values = {tuple(record[field] for field in MEASURE_FIELDS) for record in best}
    refs = [record['ref'] for record in best]
    if len(values) > 1:
        return {'status': 'conflict', 'selected': refs, 'superseded': superseded}
    return {'status': 'resolved', 'selected': refs, 'superseded': superseded,
            'measurement': dict(zip(MEASURE_FIELDS, values.pop(), strict=True))}
