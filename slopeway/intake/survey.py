from ..errors import bad
from ..fields import instant, integer, shape

MEASURE_FIELDS = ('width_mm', 'grade_permille', 'step_mm')


def normalize(row, reported, base):
    shape(row, '方向量测', ('id', 'segment', 'direction', 'observed_at', 'expires_at', *MEASURE_FIELDS))
    observed = instant(row['observed_at'], '量测时间')
    expires = instant(row['expires_at'], '量测失效时间')
    if observed > reported or expires <= observed:
        raise bad('量测须在报送前发生，失效时间须晚于量测时间。', row=base['id'])
    return {
        **base,
        'start': observed,
        'end': expires,
        'width_mm': integer(row['width_mm'], '净宽（毫米）', 1, 10000),
        'grade_permille': integer(row['grade_permille'], '有符号坡度（千分比）', -1000, 1000),
        'step_mm': integer(row['step_mm'], '台阶高度（毫米）', 0, 1000),
    }
