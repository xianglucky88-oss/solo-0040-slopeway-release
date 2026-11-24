import json
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class Api:
    def __init__(self, origin):
        self.origin = origin.rstrip('/')

    def __call__(self, path, *, submit=None, query=None, expect=200):
        url = self.origin + '/api/slopeway' + path
        if query:
            url += '?' + urlencode(query)
        data = None if submit is None else json.dumps(submit, ensure_ascii=False).encode()
        headers = {} if data is None else {'Content-Type': 'application/json'}
        request = Request(url, data=data, headers=headers)
        try:
            response = urlopen(request, timeout=8)
        except HTTPError as error:
            response = error
        with response:
            received = json.load(response)
            if response.code != expect:
                raise RuntimeError(f'{path} 返回 {response.code}，预期 {expect}：{received}')
            return received
