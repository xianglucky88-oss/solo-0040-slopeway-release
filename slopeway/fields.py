import re
from datetime import UTC, datetime

from .errors import bad

KEY = re.compile(r'[a-z0-9][a-z0-9_-]{0,47}\Z')
TIMESTAMP = re.compile(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:Z|[+-]\d\d:\d\d)\Z')


def shape(value, field, required, optional=()):
    if not isinstance(value, dict):
        raise bad(f'{field} 必须是对象。', field=field)
    absent = sorted(set(required) - value.keys())
    extra = sorted(value.keys() - set(required) - set(optional))
    if absent or extra:
        raise bad(f'{field} 字段不符合输入契约。', field=field, missing=absent, unknown=extra)
    return value


def key(value, field):
    if not isinstance(value, str) or not KEY.fullmatch(value):
        raise bad(f'{field} 必须是小写标识符。', field=field)
    return value


def text(value, field, limit=140):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise bad(f'{field} 必须包含 1 到 {limit} 个字符。', field=field)
    return value.strip()


def integer(value, field, low, high):
    if type(value) is not int or not low <= value <= high:
        raise bad(f'{field} 必须是 {low} 到 {high} 之间的整数。', field=field)
    return value


def rows(value, field, minimum, maximum):
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise bad(f'{field} 必须包含 {minimum} 到 {maximum} 条记录。', field=field)
    return value


def choice(value, field, choices):
    if not isinstance(value, str) or value not in choices:
        raise bad(f'{field} 包含未登记的值。', field=field, accepted=list(choices))
    return value


def instant(value, field):
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise bad(f'{field} 必须是带时区的整秒时间。', field=field)
    try:
        dt = datetime.fromisoformat(value).astimezone(UTC)
    except (ValueError, OverflowError) as exc:
        raise bad(f'{field} 不是有效时间。', field=field) from exc
    return dt.isoformat(timespec='seconds').replace('+00:00', 'Z')


def unique(items, field):
    seen = set()
    for item in items:
        value = item[field]
        if value in seen:
            raise bad(f'{field} 重复。', field=field, value=value)
        seen.add(value)
