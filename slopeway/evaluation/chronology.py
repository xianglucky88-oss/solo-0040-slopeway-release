from ..errors import bad
from ..fields import instant


def contains(start, end, when):
    return start <= when < end


def intersects(start, end, other_start, other_end):
    return start < other_end and other_start < end


def release_window(start, end, cutoff):
    start = instant(start, '服务起点')
    end = instant(end, '服务终点')
    cutoff = instant(cutoff, '知识截点')
    if start >= end or cutoff > start:
        raise bad('发布件须有正长度服务窗口，且知识截点不得晚于服务起点。')
    return start, end, cutoff


def in_service(meta, when):
    if not contains(meta['start'], meta['end'], when):
        raise bad('查询时点不在发布件的服务窗口内。', start=meta['start'], end=meta['end'], at=when)
