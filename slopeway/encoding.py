import hashlib
import json

from .errors import bad


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate field')
        result[key] = value
    return result


def _constant(value):
    raise ValueError(f'unsupported constant: {value}')


def decode(data):
    try:
        result = json.loads(data.decode('utf-8'), object_pairs_hook=_object, parse_constant=_constant)
        canonical(result)
        return result
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise bad('输入须是 UTF-8 JSON，且字段名不能重复。') from exc
