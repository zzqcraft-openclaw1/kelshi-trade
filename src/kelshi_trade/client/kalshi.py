from __future__ import annotations

import base64
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


@dataclass(slots=True)
class KalshiMarketRecord:
    market_id: str
    title: str
    subtitle: str | None
    yes_bid: int | None
    yes_ask: int | None
    last_price: int | None
    volume: int | None
    open_interest: int | None
    category: str
    raw: dict


class KalshiReadOnlyClient:
    def __init__(self, base_url: str, api_key_id: str, private_key_path: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key_id = api_key_id
        self.private_key_path = private_key_path
        self.private_key = self._load_private_key(private_key_path)

    def _load_private_key(self, key_path: str):
        with Path(key_path).expanduser().open("rb") as handle:
            return serialization.load_pem_private_key(
                handle.read(), password=None, backend=default_backend()
            )

    def _timestamp_ms(self) -> str:
        return str(int(dt.datetime.now().timestamp() * 1000))

    def _sign(self, timestamp: str, method: str, path: str) -> str:
        path_without_query = path.split("?")[0]
        message = f"{timestamp}{method.upper()}{path_without_query}".encode("utf-8")
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.DIGEST_LENGTH,
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def _headers(self, method: str, path: str) -> dict[str, str]:
        timestamp = self._timestamp_ms()
        sign_path = urlparse(urljoin(self.base_url + "/", path.lstrip("/"))).path
        signature = self._sign(timestamp, method, sign_path)
        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-TIMESTAMP": timestamp,
            "KALSHI-ACCESS-SIGNATURE": signature,
        }

    def get_json(self, path: str, params: dict | None = None) -> dict:
        headers = self._headers("GET", path)
        response = requests.get(urljoin(self.base_url + "/", path.lstrip("/")), headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_markets(self, limit: int = 100, cursor: str | None = None) -> dict:
        params = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self.get_json("/markets", params=params)

    def list_markets_paginated(self, limit: int = 100, max_pages: int = 10) -> dict:
        all_markets: list[dict] = []
        cursor: str | None = None
        pages = 0
        while pages < max_pages:
            payload = self.list_markets(limit=limit, cursor=cursor)
            markets = payload.get("markets", [])
            all_markets.extend(markets)
            cursor = payload.get("cursor")
            pages += 1
            if not cursor or not markets:
                break
        return {"markets": all_markets, "cursor": cursor, "pages_fetched": pages}

    @staticmethod
    def dump_raw_snapshot(payload: dict, output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
