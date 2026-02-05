from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from utils.config import get_api_base_url
from utils.state import get_access_token, logout


class ApiError(Exception):
    pass


@dataclass
class ApiResponse:
    status_code: int
    data: Any


class APIClient:
    def __init__(self) -> None:
        self.base_url = get_api_base_url()

    def _headers(self) -> dict[str, str]:
        token = get_access_token()
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: httpx.Response) -> ApiResponse:
        if response.status_code == 401:
            logout()
            raise ApiError("Session expired. Please log in again.")
        if response.status_code >= 400:
            detail = None
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise ApiError(detail)
        data = response.json() if response.content else None
        return ApiResponse(status_code=response.status_code, data=data)

    def get(self, path: str, params: dict | None = None) -> ApiResponse:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url, headers=self._headers(), params=params)
        return self._handle_response(response)

    def post(
        self,
        path: str,
        json: dict | None = None,
        data: dict | None = None,
        params: dict | None = None,
    ) -> ApiResponse:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.post(
                url, headers=self._headers(), json=json, data=data, params=params
            )
        return self._handle_response(response)

    def patch(
        self, path: str, json: dict | None = None, params: dict | None = None
    ) -> ApiResponse:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.patch(url, headers=self._headers(), json=json, params=params)
        return self._handle_response(response)

    def delete(self, path: str, params: dict | None = None) -> ApiResponse:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.delete(url, headers=self._headers(), params=params)
        return self._handle_response(response)
