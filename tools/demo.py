import argparse
import json
from pathlib import Path

from .client import Api

ROOT = Path(__file__).resolve().parents[1]
DISTRICT = '/districts/reedbank'
PUBLIC = DISTRICT + '/channels/public'
BEFORE = '2026-09-18T07:00:00Z'
WORK = '2026-09-18T09:20:00Z'
AFTER = '2026-09-18T10:00:00Z'
PROFILE = 'wheel'
EXAMPLES = ('field-survey', 'community-survey', 'closure-notice')


def example(name):
    return json.loads((ROOT / 'examples' / f'{name}.json').read_text(encoding='utf-8'))


def load(api, *, publish):
    catalog = api('/catalog')
    if any(row['id'] == 'reedbank' for row in catalog['districts']):
        raise RuntimeError('示例片区已经存在，请使用新的 --db 路径加载。')
    api('/topologies', submit=example('reedbank-topology'), expect=201)
    for name in EXAMPLES:
        api('/feeds', submit=example(name), expect=201)
    window = example('release-window')
    early = api('/releases', submit={**window, 'cutoff': BEFORE}, expect=201)['id']
    latest = api('/releases', submit=window, expect=201)['id']
    if publish:
        api(PUBLIC, submit={'release': latest, 'generation': 0, 'action': 'publish', 'note': '苇汀示例交付'}, expect=201)
    return early, latest


def main():
    parser = argparse.ArgumentParser(description='把苇汀片区的示例资料交给正在运行的数据 API。')
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    args = parser.parse_args()
    early, latest = load(Api(args.url), publish=True)
    print(f'苇汀片区已入库。\n截点较早的发布件 {early}\n公开分发的发布件 {latest}')


if __name__ == '__main__':
    main()
