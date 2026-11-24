from ..errors import bad
from ..fields import instant, shape, text


def normalize(row, base):
    shape(row, '封闭通告', ('id', 'segment', 'direction', 'from', 'until', 'reason'))
    start = instant(row['from'], '封闭开始')
    end = instant(row['until'], '封闭结束')
    if end <= start:
        raise bad('封闭结束须晚于开始。', row=base['id'])
    return {**base, 'start': start, 'end': end, 'reason': text(row['reason'], '封闭原因')}
