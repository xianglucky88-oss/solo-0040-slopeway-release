from . import notice, sources, survey
from ..errors import bad
from ..fields import choice, instant, integer, key, rows, shape, unique
from ..network.arcs import DIRECTIONS, directions


def identity(payload):
    shape(payload, '证据批次', ('district', 'revision', 'batch', 'kind', 'source', 'reported_at', 'records'))
    return key(payload['district'], '片区编号'), integer(payload['revision'], '修订号', 1, 2**31 - 1)


def _row_identity(row, segments):
    if not isinstance(row, dict):
        raise bad('证据记录须是对象。')
    row_id = key(row.get('id'), '记录编号')
    section = key(row.get('segment'), '街段编号')
    if section not in segments:
        raise bad('证据引用的街段不在该拓扑修订内。', row=row_id, segment=section)
    direction = choice(row.get('direction'), '取证方向', DIRECTIONS)
    if not set(directions(direction)).issubset(directions(segments[section])):
        raise bad('取证方向超出街段允许通行方向。', row=row_id, segment=section)
    return {'id': row_id, 'segment': section, 'direction': direction}


def normalize(payload, topology):
    district, revision = identity(payload)
    batch = key(payload['batch'], '批次编号')
    kind = choice(payload['kind'], '证据类型', ('survey', 'notice'))
    source = key(payload['source'], '来源编号')
    info = sources.lookup(source, kind)
    reported = instant(payload['reported_at'], '报送时间')
    segments = {segment['id']: segment['direction'] for segment in topology['segments']}
    records = []
    for row in rows(payload['records'], '证据记录', 1, 1500):
        base = _row_identity(row, segments)
        if kind == 'survey':
            if base['direction'] == 'both':
                raise bad('量测按单方向提交，以保留有符号坡度。', row=base['id'])
            record = survey.normalize(row, reported, base)
        else:
            record = notice.normalize(row, base)
        records.append(record)
    unique(records, 'id')
    return {
        'district': district, 'revision': revision, 'batch': batch,
        'kind': kind, 'source': source, 'rank': info['rank'],
        'reported_at': reported, 'records': sorted(records, key=lambda record: record['id']),
    }
