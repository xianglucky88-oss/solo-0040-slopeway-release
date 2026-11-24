from . import profiles, risks, selection
from .index import entries
from ..errors import missing
from ..network.arcs import expand


def evaluate(arc, indexed, profile, when):
    survey = indexed.get('survey', ())
    notices = indexed.get('notice', ())
    evidence = selection.resolve(survey, when)
    closures = risks.active_closures(notices, when)
    violations = profiles.violations(evidence['measurement'], profile) if evidence['status'] == 'resolved' else []
    if closures:
        status = 'closed'
    elif evidence['status'] != 'resolved':
        status = evidence['status']
    else:
        status = 'restricted' if violations else 'passable'
    return {
        'id': arc.id, 'segment': arc.segment, 'direction': arc.direction,
        'start': arc.start, 'end': arc.end, 'length_m': arc.length_m,
        'status': status, 'evidence': evidence, 'closures': closures, 'violations': violations,
    }


def district_view(body, when, profile):
    evidence = body['index']
    return [evaluate(arc, evidence.get(arc.id, {}), profile, when) for arc in expand(body['topology']['segments'])]


def detail(body, when, profile, arc_id):
    arc = next((item for item in expand(body['topology']['segments']) if item.id == arc_id), None)
    if arc is None:
        raise missing('发布件中没有此方向的街段。')
    indexed = body['index'].get(arc.id, {})
    return {
        **evaluate(arc, indexed, profile, when),
        'reports': {kind: list(entries(indexed.get(kind, ()), when)) for kind in ('survey', 'notice')},
    }
