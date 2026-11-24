from ..errors import bad

PROFILES = {
    'wheel': {'label': '手动轮椅', 'min_width': 1000, 'max_up': 80, 'max_down': 100, 'max_step': 15},
    'walker': {'label': '助行器', 'min_width': 850, 'max_up': 100, 'max_down': 110, 'max_step': 25},
    'pram': {'label': '推车通行', 'min_width': 750, 'max_up': 130, 'max_down': 140, 'max_step': 45},
}


def lookup(policy, key):
    if key not in policy:
        raise bad('请选择已登记的通行条件。', accepted=sorted(policy))
    return policy[key]


def violations(measure, profile):
    grades = measure['grade_permille']
    checks = (
        ('width', measure['width_mm'], profile['min_width'], measure['width_mm'] < profile['min_width']),
        ('uphill', grades, profile['max_up'], grades > profile['max_up']),
        ('downhill', -grades, profile['max_down'], -grades > profile['max_down']),
        ('step', measure['step_mm'], profile['max_step'], measure['step_mm'] > profile['max_step']),
    )
    return [{'rule': name, 'actual': actual, 'limit': limit} for name, actual, limit, fails in checks if fails]
