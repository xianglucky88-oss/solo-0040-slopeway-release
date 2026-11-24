import logging
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from .assets import Assets
from .response import json_response
from .routes import PREFIX, locate, parameters
from ..encoding import decode
from ..errors import Problem, bad

MAX_INPUT = 1_048_576
LOG = logging.getLogger('slopeway')


class Handler(BaseHTTPRequestHandler):
    server_version = 'Slopeway/1'

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def log_message(self, format, *args):
        LOG.info(format, *args)

    def _body(self):
        if self.headers.get_content_type() != 'application/json':
            raise Problem(415, 'unsupported_media_type', '请使用 JSON 请求。')
        sizes = self.headers.get_all('Content-Length') or []
        if len(sizes) != 1 or not sizes[0].isascii() or not sizes[0].isdecimal() or len(sizes[0]) > 10:
            raise bad('请求长度无效。')
        size = int(sizes[0])
        if size > MAX_INPUT:
            raise Problem(413, 'payload_too_large', '请求超过 1 MiB。')
        data = self.rfile.read(size)
        if len(data) != size:
            raise bad('请求内容未完整传输。')
        return decode(data)

    def _handle(self):
        self.connection.settimeout(10)
        try:
            self._dispatch()
        except Problem as exc:
            json_response(self, (exc.status, exc.payload()))
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            LOG.debug('request disconnected')
        except sqlite3.OperationalError as exc:
            if exc.sqlite_errorcode in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                json_response(self, (503, {'code': 'busy', 'message': '证据库繁忙，请重试。'}))
            else:
                self._internal_error()
        except Exception:
            self._internal_error()

    def _internal_error(self):
        LOG.exception('request failed')
        json_response(self, (500, {'code': 'internal_error', 'message': '处理请求时发生错误。'}))

    def _dispatch(self):
        try:
            request = urlsplit(self.path)
        except ValueError as exc:
            raise bad('请求地址无效。') from exc
        if self.command == 'GET' and not request.path.startswith(PREFIX):
            self.server.assets.serve(self, request.path)
            return
        action, matches = locate(self.command, request.path)
        query = parameters(request.query)
        body = self._body() if self.command == 'POST' else None
        with self.server.database.transaction(write=self.command == 'POST') as connection:
            result = action(connection, matches, query, body)
        json_response(self, result)


class Server(ThreadingHTTPServer):
    def __init__(self, address, database, web):
        self.database = database
        self.assets = Assets(web)
        super().__init__(address, Handler)
