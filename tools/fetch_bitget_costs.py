"""
SULTAN QUANT OS
Tool: Fetch Bitget Spot HYPEUSDT costs
Version: 1.0.0

Requires:
    BITGET_API_KEY
    BITGET_API_SECRET
    BITGET_API_PASSPHRASE

The endpoint is authenticated because the account-specific fee rate
is the correct source for personalized maker/taker costs.

Run:
    python tools\fetch_bitget_costs.py
"""

from pathlib import Path
import base64
import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode

import requests


BASE_URL = "https://api.bitget.com"
REQUEST_PATH = "/api/v3/account/fee-rate"
SYMBOL = "HYPEUSDT"
CATEGORY = "SPOT"


def sign(secret, message):
    digest = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).digest()
    return base64.b64encode(digest).decode()


def main():
    api_key = os.getenv("BITGET_API_KEY")
    api_secret = os.getenv("BITGET_API_SECRET")
    passphrase = os.getenv("BITGET_API_PASSPHRASE")

    if not all((api_key, api_secret, passphrase)):
        raise RuntimeError(
            "Set BITGET_API_KEY, BITGET_API_SECRET and "
            "BITGET_API_PASSPHRASE first."
        )

    timestamp = str(int(time.time() * 1000))
    params = {
        "category": CATEGORY,
        "symbol": SYMBOL,
    }
    query = "?" + urlencode(sorted(params.items()))
    prehash = timestamp + "GET" + REQUEST_PATH + query

    headers = {
        "ACCESS-KEY": api_key,
        "ACCESS-SIGN": sign(api_secret, prehash),
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json",
    }

    response = requests.get(
        BASE_URL + REQUEST_PATH + query,
        headers=headers,
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()

    if payload.get("code") != "00000":
        raise RuntimeError(json.dumps(payload, indent=2))

    data = payload["data"]
    maker = float(data["makerFeeRate"])
    taker = float(data["takerFeeRate"])

    print("=" * 70)
    print("BITGET SPOT COSTS")
    print("=" * 70)
    print(f"Symbol       : {SYMBOL}")
    print(f"Maker fee    : {maker:.6%}")
    print(f"Taker fee    : {taker:.6%}")
    print(f"Request time : {payload.get('requestTime')}")
    print()
    print("Set for current PowerShell session:")
    print(f'$env:BITGET_MAKER_FEE="{maker}"')
    print(f'$env:BITGET_TAKER_FEE="{taker}"')
    print()
    print("Do NOT put API keys in source files.")


if __name__ == "__main__":
    main()
