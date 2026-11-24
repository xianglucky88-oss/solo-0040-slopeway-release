from ..errors import bad

SOURCES = {
    'field-team': {'label': '片区复核组', 'rank': 30, 'kinds': ('survey',)},
    'access-walk': {'label': '通行踏勘组', 'rank': 20, 'kinds': ('survey',)},
    'community': {'label': '共巡采集点', 'rank': 10, 'kinds': ('survey',)},
    'streetworks': {'label': '道路施工作业台', 'rank': 0, 'kinds': ('notice',)},
    'venue-desk': {'label': '场地值守台', 'rank': 0, 'kinds': ('notice',)},
}


def lookup(source, kind):
    info = SOURCES.get(source)
    if info is None or kind not in info['kinds']:
        raise bad('该来源未登记提交此类证据。', source=source, kind=kind)
    return info


def catalog():
    return [{'id': key, **source} for key, source in SOURCES.items()]
