"""
Ch.01 - One tool call: get_price

The atomic unit of our quant agent.
Market -> tool call -> structured result -> model reads it.

Supports three markets from one interface:
  - A-stock  (eastmoney direct API) - Shanghai/Shenzhen
  - Crypto   (Binance via ccxt)     - needs VPN in China
  - US stock (yfinance)             - sometimes rate-limited
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from typing import Any

import requests

# ── The tool contract (Ch.01: "the schema is the contract") ──────────

GET_PRICE_SCHEMA = {
    "name": "get_price",
    "description": (
        "Returns the latest price and today's OHLCV (open/high/low/close/volume) "
        "for a given trading symbol. "
        "Use this when you need current market data for a specific asset. "
        "Supports three markets, auto-detected by symbol format:\n"
        "  - A-stock: 6-digit code like '600001' or '000001'\n"
        "  - Crypto:  pair like 'BTC/USDT' or 'ETH/USDT'\n"
        "  - US stock: ticker like 'AAPL' or 'TSLA'\n"
        "Do NOT use for: historical multi-day data, order placement, "
        "or fundamental analysis (PE ratio, financial reports)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": (
                    "Trading symbol. Format determines market:\n"
                    "  A-stock:  '600001' (Shanghai) or '000001' (Shenzhen)\n"
                    "  Crypto:   'BTC/USDT'\n"
                    "  US stock: 'AAPL'"
                ),
            },
            "market": {
                "type": "string",
                "enum": ["a_stock", "crypto", "us_stock", "auto"],
                "description": (
                    "Which market to query. Default 'auto' detects from symbol format. "
                    "Set explicitly if auto-detection gets it wrong."
                ),
            },
        },
        "required": ["symbol"],
    },
}


# ── Market adapters (Ch.01: "your code is the kitchen") ──────────────

def _detect_market(symbol: str) -> str:
    """Auto-detect market from symbol format."""
    if "/" in symbol:
        return "crypto"
    if symbol.isdigit() and len(symbol) == 6:
        return "a_stock"
    if symbol.isalpha() and 1 <= len(symbol) <= 5:
        return "us_stock"
    raise ValueError(
        f"Cannot auto-detect market for symbol '{symbol}'. "
        f"Set `market` explicitly to 'a_stock', 'crypto', or 'us_stock'."
    )


def _fetch_a_stock(symbol: str) -> dict[str, Any]:
    """
    Fetch A-stock real-time quote via eastmoney direct API.

    Uses the same backend as akshare but queries a single stock,
    avoiding the bulk-data scraping pattern that triggers blocks.
    """
    # Shanghai: secid=1.<code>, Shenzhen: secid=0.<code>
    if symbol.startswith(("6", "5")):
        secid = f"1.{symbol}"
    else:
        secid = f"0.{symbol}"

    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f169,f170",
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    d = data.get("data")
    if d is None:
        return {"error": f"A-stock symbol '{symbol}' not found", "market": "a_stock"}

    price = d.get("f43")
    if price is None:
        return {"error": f"No price data for '{symbol}' (halted or suspended?)", "market": "a_stock"}

    return {
        "market": "a_stock",
        "symbol": symbol,
        "name": str(d.get("f58", "")),
        "price": float(price) / 100,
        "change_pct": float(d.get("f170", 0)) / 100,
        "change_amount": float(d.get("f169", 0)) / 100,
        "volume": int(d.get("f47", 0)),
        "amount": float(d.get("f48", 0)),
        "high": float(d.get("f44", 0)) / 100,
        "low": float(d.get("f45", 0)) / 100,
        "open": float(d.get("f46", 0)) / 100,
        "pre_close": float(d.get("f60", 0)) / 100,
        "timestamp": datetime.now().isoformat(),
    }


def _fetch_crypto(symbol: str) -> dict[str, Any]:
    """Fetch crypto ticker via ccxt (Binance - needs VPN in China)."""
    import ccxt  # type: ignore

    exchange = ccxt.binance()
    ticker = exchange.fetch_ticker(symbol)

    return {
        "market": "crypto",
        "symbol": symbol,
        "price": float(ticker["last"]),
        "change_pct": float(ticker["percentage"]),
        "change_amount": float(ticker["change"]),
        "high": float(ticker["high"]),
        "low": float(ticker["low"]),
        "volume": float(ticker["baseVolume"]),
        "bid": float(ticker["bid"]) if ticker["bid"] else None,
        "ask": float(ticker["ask"]) if ticker["ask"] else None,
        "timestamp": datetime.now().isoformat(),
    }


def _fetch_us_stock(symbol: str) -> dict[str, Any]:
    """Fetch US stock quote via yfinance (may hit rate limits)."""
    import yfinance as yf  # type: ignore

    # yfinance is aggressive with rate limiting.
    # Small delay helps when querying a few symbols.
    time.sleep(1.0)

    ticker = yf.Ticker(symbol)
    info = ticker.info

    return {
        "market": "us_stock",
        "symbol": symbol,
        "name": info.get("shortName", symbol),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "change_pct": info.get("regularMarketChangePercent"),
        "high": info.get("dayHigh"),
        "low": info.get("dayLow"),
        "volume": info.get("volume"),
        "open": info.get("regularMarketOpen"),
        "pre_close": info.get("previousClose"),
        "currency": info.get("currency", "USD"),
        "timestamp": datetime.now().isoformat(),
    }


# ── The tool dispatcher (Ch.01: "look up the function by name") ──────

def get_price(symbol: str, market: str = "auto") -> dict[str, Any]:
    """
    Execute a get_price tool call.

    This is the dispatch function — Ch.01 step 3 ("You execute").
    Validates market, routes to the correct adapter, wraps errors as results
    so the model can read them instead of crashing.

    Args:
        symbol: Trading symbol (auto-detected or explicit).
        market: 'a_stock', 'crypto', 'us_stock', or 'auto' (default).

    Returns:
        Structured price data dict, or an error dict the model can recover from.
    """
    # Auto-detect or validate market
    if market == "auto":
        try:
            market = _detect_market(symbol)
        except ValueError as e:
            return {"error": str(e), "symbol": symbol}

    # Validate — not just against schema, but against the real world
    # (Ch.01: "validate the arguments before executing")
    if market not in ("a_stock", "crypto", "us_stock"):
        return {
            "error": f"Unknown market '{market}'. "
            f"Valid values: a_stock, crypto, us_stock, auto.",
            "symbol": symbol,
        }

    # Dispatch (Ch.01: "the wire format does not care what the tool does")
    try:
        match market:
            case "a_stock":
                return _fetch_a_stock(symbol)
            case "crypto":
                return _fetch_crypto(symbol)
            case "us_stock":
                return _fetch_us_stock(symbol)
    except Exception as e:
        # Ch.01: "If the function fails at runtime, return *that* as a
        # tool_result too — with a message useful to the model, not a stack trace."
        return {
            "error": f"Failed to fetch {market} price for '{symbol}': {e}",
            "symbol": symbol,
            "market": market,
        }


# ── Demo: exercise the tool directly ─────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Ch.01 Demo - One tool call per market")
    print("=" * 60)

    # This is what the model would emit (Ch.01 step 2)
    # tool_use: { id: "call_001", name: "get_price", input: { symbol: "600519" } }
    print("\n[A-stock] Kweichow Moutai (600519)")
    result = get_price("600519")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n[Crypto] BTC/USDT")
    result = get_price("BTC/USDT")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n[US stock] AAPL")
    result = get_price("AAPL")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Ch.01: "When something goes wrong, return the error as a tool_result"
    print("\n[Error] Unknown symbol")
    result = get_price("??INVALID??")
    print(json.dumps(result, ensure_ascii=False, indent=2))
