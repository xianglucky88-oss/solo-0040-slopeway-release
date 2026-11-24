import argparse
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from selectors import EVENT_READ, DefaultSelector
from tempfile import TemporaryDirectory

from . import verify_intake, verify_release, verify_route
from .client import Api
from .demo import load

CHECKS = {
    'topology': verify_intake.topology,
    'survey': verify_intake.survey,
    'notice': verify_intake.notice,
    'compile': verify_release.compile_release,
    'directions': verify_route.directions,
    'route': verify_route.route,
    'coverage': verify_route.coverage,
    'compare': verify_route.compare,
    'verify': verify_release.verify,
    'publish': verify_release.publish,
    'restore': verify_release.restore,
}


@contextmanager
def local_api():
    with TemporaryDirectory(prefix='slopeway-workflow-') as root:
        db = Path(root) / 'workflow.sqlite3'
        command = [sys.executable, '-m', 'slopeway', '--db', str(db), '--port', '0']
        with subprocess.Popen(command, stdout=subprocess.PIPE, text=True) as server:
            try:
                with DefaultSelector() as events:
                    events.register(server.stdout, EVENT_READ)
                    if not events.select(timeout=8):
                        raise RuntimeError('本地服务未在限定时间内启动。')
                    origin = server.stdout.readline().strip()
                if not origin.startswith('http://127.0.0.1:'):
                    raise RuntimeError('本地服务未返回监听地址。')
                yield Api(origin)
            finally:
                if server.poll() is None:
                    server.terminate()
                    try:
                        server.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        server.kill()


def main():
    parser = argparse.ArgumentParser(description='用隔离数据库回放坡径生产 HTTP 工作流。')
    parser.add_argument('workflow', choices=('all', *CHECKS))
    args = parser.parse_args()
    selected = CHECKS if args.workflow == 'all' else (args.workflow,)
    for name in selected:
        with local_api() as api:
            early, latest = load(api, publish=False)
            CHECKS[name](api, early, latest)
        print(f'{name}: OK')


if __name__ == '__main__':
    main()
