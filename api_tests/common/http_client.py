from typing import Any, Dict, Optional

import requests


class HttpClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(
        self,
        method: str,
        path: Optional[str] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        form: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        request_url = url or f"{self.base_url}{path or ''}"
        return self.session.request(
            method=method.upper(),
            url=request_url,
            headers=headers,
            params=params,
            json=json_body,
            data=form,
            timeout=self.timeout,
        )
