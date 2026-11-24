import re
from collections import namedtuple
from urllib.parse import parse_qs

from . import channel_api, feed_api, release_api, topology_api
from ..errors import Problem, bad, missing

PREFIX = '/api/slopeway'
DISTRICT = r'/districts/(?P<district>[a-z0-9][a-z0-9_-]{0,47})'
REVISIONS = DISTRICT + r'/revisions'
REVISION = REVISIONS + r'/(?P<revision>[1-9][0-9]{0,9})'
RELEASE = r'/releases/(?P<release>sw-[a-f0-9]{64})'
CHANNEL = DISTRICT + r'/channels/(?P<channel>field|public)'
ARC = r'/arcs/(?P<arc>[a-z0-9][a-z0-9_-]{0,47}:(?:ab|ba))'
Route = namedtuple('Route', 'method pattern action')

ROUTES = tuple(Route(method, re.compile(PREFIX + path), action) for method, path, action in (
    ('GET', '/catalog', topology_api.catalog),
    ('GET', REVISIONS, topology_api.revisions),
    ('GET', REVISION, topology_api.read),
    ('POST', '/topologies', topology_api.create),
    ('GET', REVISION + '/feeds', feed_api.catalog),
    ('POST', '/feeds', feed_api.create),
    ('GET', DISTRICT + '/releases', release_api.catalog),
    ('GET', DISTRICT + '/channels', topology_api.channels),
    ('POST', '/releases', release_api.create),
    ('GET', RELEASE, release_api.meta),
    ('GET', RELEASE + '/overview', release_api.overview),
    ('GET', RELEASE + ARC, release_api.detail),
    ('GET', RELEASE + '/route', release_api.route),
    ('GET', RELEASE + '/compare', release_api.compare),
    ('GET', RELEASE + '/verify', release_api.verify),
    ('GET', RELEASE + '/export', release_api.export),
    ('GET', CHANNEL, channel_api.history),
    ('POST', CHANNEL, channel_api.move),
    ('GET', CHANNEL + '/route', channel_api.route),
    ('GET', CHANNEL + '/export', channel_api.export),
))


def locate(method, path):
    other_methods = []
    for route in ROUTES:
        match = route.pattern.fullmatch(path)
        if match and route.method == method:
            return route.action, match.groupdict()
        if match:
            other_methods.append(route.method)
    if other_methods:
        raise Problem(405, 'method_not_allowed', '该接口不支持此请求方法。', allowed=other_methods)
    raise missing('没有找到该数据入口。')


def parameters(source):
    try:
        pairs = parse_qs(source, keep_blank_values=True, max_num_fields=12, errors='strict')
    except ValueError as exc:
        raise bad('查询参数无法读取。') from exc
    if any(len(values) != 1 for values in pairs.values()):
        raise bad('查询参数不能重复。')
    return {key: values[0] for key, values in pairs.items()}
