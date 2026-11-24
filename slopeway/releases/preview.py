from ..errors import bad
from ..evaluation import chronology, coverage, profiles, section
from ..fields import instant, key
from ..network import router


def _parameters(body, at, profile):
    at = instant(at, '查询时点')
    chronology.in_service(body['meta'], at)
    return at, profiles.lookup(body['policy'], profile)


def overview(release, at, profile):
    body = release['body']
    at, constraints = _parameters(body, at, profile)
    sections = section.district_view(body, at, constraints)
    return {'id': release['id'], 'at': at, 'profile': profile,
            'topology': body['topology'], 'sections': sections, 'coverage': coverage.summarize(sections)}


def trace(release, at, profile, arc):
    at, constraints = _parameters(release['body'], at, profile)
    return section.detail(release['body'], at, constraints, arc)


def route(release, at, profile, origin, target):
    body = release['body']
    at, constraints = _parameters(body, at, profile)
    origin, target = key(origin, '起点编号'), key(target, '终点编号')
    nodes = {node['id'] for node in body['topology']['nodes']}
    if origin not in nodes or target not in nodes:
        raise bad('路线端点必须来自当前发布件。', origin=origin, target=target)
    result = router.solve(section.district_view(body, at, constraints), origin, target)
    return {'id': release['id'], 'at': at, 'profile': profile, **result}
