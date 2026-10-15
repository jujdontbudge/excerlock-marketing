"""Small Platform API transport; exceptions never contain remote bodies or credentials."""
import os
import time
import uuid
from pathlib import Path

import requests
from dotenv import dotenv_values

BASE = 'https://app.sideshift.app/api/oauth/v1'


class APIError(RuntimeError):
    pass


class RateLimited(APIError):
    pass


class ProtocolError(APIError):
    pass


class MissingKey(APIError):
    pass


def api_key():
    key = os.environ.get('SIDESHIFT_API_KEY')
    if not key:
        source = Path('/Users/johansardar/contacts-mcp/.env')
        if source.exists():
            key = dotenv_values(source).get('SIDESHIFT_API_KEY')
    return key


class Client:
    def __init__(self, key=None, http=None):
        self.key = key or api_key()
        if not self.key:
            raise MissingKey('MissingKey')
        self.http = http or requests.Session()
        self.not_before = 0

    def request(self, method, path, params=None, payload=None, request_id=None):
        if time.time() < self.not_before:
            raise RateLimited('RateLimited')
        headers = {'x-api-key': self.key}
        if method != 'GET':
            headers['Idempotency-Key'] = request_id or str(uuid.uuid4())
        try:
            response = self.http.request(method, BASE + path, headers=headers,
                                         params=params, json=payload, timeout=30, allow_redirects=False)
        except Exception:
            raise APIError('TransportError; sync before retrying') from None
        if response.status_code == 429:
            try:
                delay = max(1, float(response.headers.get('Retry-After', 60)))
            except (ValueError, TypeError):
                delay = 60
            self.not_before = time.time() + delay
            raise RateLimited('RateLimited')
        if not 200 <= response.status_code < 300:
            raise APIError(f'HTTP{response.status_code}')
        try:
            document = response.json()
            if not isinstance(document, dict) or 'data' not in document:
                raise ValueError()
            return document
        except Exception:
            raise ProtocolError('ProtocolError') from None

    def pages(self, path, **params):
        seen = set()
        for _ in range(1000):
            # Live advanced-applicants validation caps the page at 25 despite
            # the common documentation's 100 maximum. Use the smaller page.
            page = self.request('GET', path, params={**params, 'limit': 25})
            if not isinstance(page['data'], list):
                raise ProtocolError('ProtocolError')
            yield from page['data']
            if not page.get('hasMore'):
                return
            cursor = page.get('nextCursor')
            if not cursor or cursor in seen:
                raise ProtocolError('PaginationError')
            seen.add(cursor)
            params['cursor'] = cursor
        raise ProtocolError('PaginationLimit')
