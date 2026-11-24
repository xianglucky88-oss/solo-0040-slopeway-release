import ast
import shutil
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    python_sources = sorted((*ROOT.joinpath('slopeway').rglob('*.py'), *ROOT.joinpath('tools').glob('*.py')))
    for path in python_sources:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path.relative_to(ROOT)))
    modules = sorted(ROOT.joinpath('web', 'js').glob('*.mjs'))
    node = shutil.which('node')
    if node is None:
        raise SystemExit('构建检查需要 Node.js，以验证浏览器模块语法。')
    for path in modules:
        subprocess.run([node, '--check', str(path)], check=True)
    with sqlite3.connect(':memory:') as connection:
        connection.executescript(ROOT.joinpath('slopeway', 'storage', 'schema.sql').read_text(encoding='utf-8'))
    from slopeway.http.routes import ROUTES
    print(f'语法与导入通过：{len(python_sources)} 个 Python 文件，{len(modules)} 个浏览器模块，{len(ROUTES)} 条 API 路由。')


if __name__ == '__main__':
    main()
