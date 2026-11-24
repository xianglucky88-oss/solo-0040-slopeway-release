from pathlib import Path

from ..errors import missing
from .response import write

MEDIA_TYPES = {'.html': 'text/html', '.css': 'text/css', '.mjs': 'text/javascript'}


class Assets:
    def __init__(self, root):
        self.paths = {'/': root / 'index.html'}
        for folder, pattern in (('styles', '*.css'), ('js', '*.mjs')):
            self.paths.update({f'/{folder}/{path.name}': path for path in (root / folder).glob(pattern)})

    def serve(self, handler, path):
        asset = self.paths.get(path)
        if asset is None:
            raise missing('页面不存在。')
        data = Path(asset).read_bytes()
        write(handler, 200, data, f'{MEDIA_TYPES[asset.suffix]}; charset=utf-8')
