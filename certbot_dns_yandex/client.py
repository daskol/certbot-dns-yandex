#   encoding: utf8
#   filename: client.py

from dataclasses import dataclass
from http import HTTPStatus
from http.client import HTTPResponse
from json import load
from os import getenv
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


@dataclass
class Record:

    # Field record_id used by API for domain identification.
    record_id: int

    type: str
    domain: str
    fqdn: str
    content: str
    priority: int

    ttl: Optional[int] = None
    subdomain: Optional[str] = None


class Client:
    """Class Client provides bindings to Yandex DSN Manager (PDD).
    See https://yandex.ru/dev/pdd/doc/concepts/api-dns.html for details.

    :param token: Access token (related envvar is YANDEX_PDD_TOKEN).
    """

    ENDPOINT = 'https://pddimp.yandex.ru/api2/admin/dns/{method}'

    def __init__(self, token: Optional[str] = None):
        self.token = getenv('YANDEX_PDD_TOKEN') or token
        self.headers = {'PddToken': self.token}

    @staticmethod
    def _append_params(url: str, params: Dict[str, str]) -> str:
        scheme, netloc, path, query, fragment = urlsplit(url)
        values = parse_qs(query)
        values.update(params)
        query = urlencode(values)
        return urlunsplit((scheme, netloc, path, query, fragment))

    @staticmethod
    def _make_query(params: Dict[str, Any]) -> bytes:
        # Assume callee collect params with locals() built-in function.
        params.pop('self')
        # Also, we ignore None values since thay are optional for the API.
        query = urlencode({k: v for k, v in params.items() if v is not None})
        return query.encode()

    @staticmethod
    def _validate_response(res: HTTPResponse) -> Dict[str, Any]:
        if (code := res.getcode()) != HTTPStatus.OK:
            raise RuntimeError(f'Requets failed with status code {code}.')

        json = load(res)

        if (status := json.get('success')) == 'error':
            raise RuntimeError(f'Request failed: {json.get("error")}.')
        elif status != 'ok':
            raise RuntimeError(f'Unknown request status: {status}.')

        return json

    def _request(self, verb: str, method: str,
                 params: Dict[str, Any]) -> Dict[str, Any]:
        """Method _request is a common routine which actually performs requests
        to Yandex DNS manager (PDD) API.

        :param verb: HTTP request verb.
        :param method: API method.
        :param params: Request params (either query string or form data).

        :return: Deserialized into dictionary JSON object.
        """
        url = Client.ENDPOINT.format(method=method)
        if verb == 'GET':
            url = Client._append_params(url, params)
            data = None
        else:
            data = Client._make_query(params)
        req = Request(method=verb, url=url, headers=self.headers, data=data)
        res = urlopen(req)
        json = Client._validate_response(res)
        return json

    def add(self, domain: str, type: str, content: str,
            priority: Optional[int] = None, ttl: Optional[int] = None,
            subdomain: Optional[str] = None, admin_mail: Optional[str] = None,
            weight: Optional[int] = None, port: Optional[int] = None,
            target: Optional[str] = None,) -> Record:
        json = self._request('POST', 'add', locals())
        return Record(**json.get('record', {}))

    def delete(self, domain: str, record_id: int) -> int:
        json = self._request('POST', 'del', locals())
        return json.get('record_id')

    def edit(self, domain: str, record_id: int,
             admin_mail: Optional[str] = None, content: Optional[str] = None,
             expire: Optional[int] = None, neg_cache: Optional[int] = None,
             port: Optional[int] = None, priority: Optional[int] = None,
             refresh: Optional[int] = None, retry: Optional[int] = None,
             subdomain: Optional[str] = None, target: Optional[str] = None,
             ttl: Optional[int] = None,
             weight: Optional[int] = None) -> Record:
        json = self._request('POST', 'edit', locals())
        return Record(**json.get('record', {}))

    def list(self, domain: str) -> List[Record]:
        json = self._request('GET', 'list', {'domain': domain})
        return [Record(**entry) for entry in json.get('records', [])]


__all__ = (Client, Record)
