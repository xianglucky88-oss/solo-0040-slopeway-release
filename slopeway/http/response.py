from dataclasses import dataclass

from ..encoding import canonical


@dataclass(frozen=True)
class Download:
    value: dict
    filename: str


def write(handler, status, body, content_type, *, download=None):
    handler.send_response(status)
    handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    handler.send_header('X-Content-Type-Options', 'nosniff')
    if download:
        handler.send_header('Content-Disposition', f'attachment; filename="{download}"')
    handler.end_headers()
    handler.wfile.write(body)


def json_response(handler, result):
    mime = 'application/json; charset=utf-8'
    if isinstance(result, Download):
        write(handler, 200, canonical(result.value), mime, download=result.filename)
        return
    status, body = result if isinstance(result, tuple) else (200, result)
    write(handler, status, canonical(body), mime)
