from typing import Any, Dict, List

import requests

API_BASE = "http://localhost:8000"


def get(path: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]] | Dict[str, Any]:
    return requests.get(f"{API_BASE}{path}", params=params, timeout=15).json()


def post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return requests.post(f"{API_BASE}{path}", json=payload, timeout=15).json()


def patch(path: str) -> Dict[str, Any]:
    return requests.patch(f"{API_BASE}{path}", timeout=15).json()


def get_binary(path: str, params: Dict[str, Any] | None = None) -> bytes:
    return requests.get(f"{API_BASE}{path}", params=params, timeout=30).content
