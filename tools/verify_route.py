from .demo import AFTER, PROFILE, WORK, example

START = '2026-09-18T08:00:00Z'
TRAVEL = {'origin': 'arch', 'target': 'garden'}


def read(api, release, operation, when=WORK, profile=PROFILE, **extra):
    return api(f'/releases/{release}/{operation}', query={'at': when, 'profile': profile, **extra})


def directions(api, early, latest):
    forward = read(api, latest, 'arcs/arch-deck:ab')
    reverse = read(api, latest, 'arcs/arch-deck:ba')
    assert forward['status'] == 'passable' and forward['evidence']['measurement']['grade_permille'] == -92
    assert forward['evidence']['superseded'] == ['community/check-917/arch-deck-ab']
    assert reverse['violations'] == [{'rule': 'uphill', 'actual': 92, 'limit': 80}]
    assert read(api, latest, 'arcs/arch-deck:ba', profile='walker')['status'] == 'passable'
    assert read(api, latest, 'arcs/deck-lookout:ab')['status'] == 'closed'
    assert read(api, latest, 'arcs/deck-lookout:ba')['status'] == 'passable'
    assert read(api, latest, 'arcs/deck-lookout:ab', when=AFTER)['status'] == 'passable'
    assert read(api, early, 'arcs/deck-lookout:ab')['status'] == 'passable'


def route(api, early, latest):
    assert read(api, latest, 'route', when=START, **TRAVEL)['distance_m'] == 410
    detour = read(api, latest, 'route', **TRAVEL)
    assert detour['distance_m'] == 480
    assert [step['id'] for step in detour['steps']] == ['arch-bay:ab', 'bay-court:ab', 'court-garden:ab']
    assert read(api, early, 'route', **TRAVEL)['distance_m'] == 410
    assert read(api, latest, 'route', when=AFTER, **TRAVEL)['distance_m'] == 410
    blocked = read(api, latest, 'route', origin='garden', target='pier')
    assert blocked['status'] == 'unreachable' and 'pier' not in blocked['reachable']
    assert not any(item['id'] == 'pier-bay:ba' for item in blocked['boundary'])
    assert read(api, latest, 'route', origin='garden', target='garden')['distance_m'] == 0


def coverage(api, early, latest):
    first = read(api, latest, 'overview')['coverage']
    assert first['direction_count'] == 21 and first['evidence']['unknown'] == 1
    assert first['gaps'][0]['id'] == 'quay-garden:ba'
    sample = example('field-survey')
    row = next(row for row in sample['records'] if row['id'] == 'arch-deck-ab')
    changed = {**sample, 'batch': 'walk-review', 'records': [{**row, 'grade_permille': -127}]}
    api('/feeds', submit=changed, expect=201)
    newer = api('/releases', submit=example('release-window'), expect=201)['id']
    health = read(api, newer, 'overview')['coverage']
    assert health['evidence']['conflict'] == 1 and health['evidence']['unknown'] == 1
    assert len(read(api, newer, 'arcs/arch-deck:ab')['evidence']['selected']) == 2
    assert read(api, latest, 'overview')['coverage'] == first


def compare(api, early, latest):
    result = read(api, latest, 'compare', before=early)
    assert [row['arc'] for row in result['changes']] == ['deck-lookout:ab']
    assert result['changes'][0]['after']['closures'][0]['ref'] == 'streetworks/join-918/stone-joint'
    assert read(api, latest, 'compare', when=AFTER, before=early)['changes'] == []
    api(f'/releases/{latest}/compare', query={'at': example('release-window')['end'], 'profile': PROFILE, 'before': early}, expect=422)
