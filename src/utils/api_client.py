from __future__ import annotations

from typing import Any, Dict, Optional

import requests


class ApiClient:
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def _url(self, path: str) -> str:
        path = path if path.startswith("/") else "/" + path
        return self.base_url + path

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(self._url(path), **kwargs)

    def post(self, path: str, json: Any | None = None, **kwargs) -> requests.Response:
        return self.session.post(self._url(path), json=json, **kwargs)

    def put(self, path: str, json: Any | None = None, **kwargs) -> requests.Response:
        return self.session.put(self._url(path), json=json, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.session.delete(self._url(path), **kwargs)
