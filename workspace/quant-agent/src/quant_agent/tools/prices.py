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
    Fetch A-stock real-time quote via Sina finance API.

    Sina is more lenient than eastmoney and doesn't require
    browser-mimicking headers. Falls back gracefully on failure.
    """
    # Shanghai: sh600519, Shenzhen: sz000001
    if symbol.startswith(("6", "5")):
        code = f"sh{symbol}"
    else:
        code = f"sz{symbol}"

    url = f"https://hq.sinajs.cn/list={code}"
    headers = {
        "Referer": "https://finance.sina.com.cn/",
        "User-Agent": "Mozilla/5.0",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        resp.encoding = "gbk"  # Sina uses GBK
    except requests.RequestException as e:
        return {
            "error": f"Failed to fetch a_stock price for '{symbol}': {e}",
            "symbol": symbol,
            "market": "a_stock",
        }

    # Sina returns: var hq_str_sh600519="name,open,pre_close,price,high,low,..."
    text = resp.text
    if '=""' in text or "=" not in text:
        return {"error": f"A-stock symbol '{symbol}' not found on Sina", "market": "a_stock"}

    # Extract the quoted CSV portion
    try:
        raw = text.split('="')[1].rstrip('";\n')
        fields = raw.split(",")
    except IndexError:
        return {"error": f"Failed to parse Sina response for '{symbol}'", "market": "a_stock"}

    return {
        "market": "a_stock",
        "symbol": symbol,
        "name": fields[0],
        "open": float(fields[1]),
        "pre_close": float(fields[2]),
        "price": float(fields[3]),
        "high": float(fields[4]),
        "low": float(fields[5]),
        "volume": int(fields[8]),
        "amount": float(fields[9]),
        "change_pct": round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2),
        "change_amount": round(float(fields[3]) - float(fields[2]), 2),
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


# ═════════════════════════════════════════════════════════════════════
# get_kline — historical candlestick data
# ═════════════════════════════════════════════════════════════════════

GET_KLINE_SCHEMA = {
    "name": "get_kline",
    "description": (
        "Returns historical K-line (candlestick) data for a given A-stock symbol. "
        "Each bar contains open, high, low, close, and volume. "
        "Use this to analyze price trends, volatility, and volume patterns over time. "
        "Supports daily bars ('D'), weekly ('W'), monthly ('M'), "
        "and intraday ('5', '15', '30', '60' minutes).\n"
        "Do NOT use for: real-time tick data, order book depth, or non-A-stock markets."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "A-stock 6-digit code, e.g. '600519' or '000001'.",
            },
            "scale": {
                "type": "string",
                "enum": ["5", "15", "30", "60", "240"],
                "description": (
                    "Bar interval in minutes: '5'/'15'/'30'/'60' for intraday, "
                    "'240' for daily (~4h trading session). Default '240'."
                ),
            },
            "count": {
                "type": "integer",
                "description": "Number of bars to return (max 200, default 20).",
            },
        },
        "required": ["symbol"],
    },
}


def _fetch_a_kline(symbol: str, scale: str = "240", count: int = 20) -> dict[str, Any]:
    """Fetch A-stock K-line data via Sina API."""
    count = min(max(count, 1), 200)  # clamp to [1, 200]

    if symbol.startswith(("6", "5")):
        code = f"sh{symbol}"
    else:
        code = f"sz{symbol}"

    url = "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    params = {"symbol": code, "scale": scale, "datalen": count, "ma": "no"}
    headers = {"Referer": "https://finance.sina.com.cn/", "User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = "gbk"
    except requests.RequestException as e:
        return {"error": f"Failed to fetch kline for '{symbol}': {e}", "symbol": symbol}

    try:
        raw_bars = resp.json()
    except json.JSONDecodeError:
        return {"error": f"Failed to parse kline response for '{symbol}'", "symbol": symbol}

    if not raw_bars or not isinstance(raw_bars, list):
        return {"error": f"No kline data for '{symbol}' (delisted or invalid?)", "symbol": symbol}

    # Normalize: keep only the fields the model needs
    bars = []
    for b in raw_bars:
        bars.append({
            "time": b.get("day", ""),
            "open": float(b["open"]),
            "high": float(b["high"]),
            "low": float(b["low"]),
            "close": float(b["close"]),
            "volume": int(float(b["volume"])),
        })

    # Compute a brief summary for the model
    closes = [b["close"] for b in bars]
    first_close = closes[0]
    last_close = closes[-1]
    trend_pct = round((last_close - first_close) / first_close * 100, 2) if first_close else 0

    return {
        "market": "a_stock",
        "symbol": symbol,
        "scale": scale,
        "count": len(bars),
        "trend": {
            "start_price": first_close,
            "end_price": last_close,
            "change_pct": trend_pct,
            "highest": max(b["high"] for b in bars),
            "lowest": min(b["low"] for b in bars),
        },
        "bars": bars,
        "timestamp": datetime.now().isoformat(),
    }


def get_kline(symbol: str, scale: str = "240", count: int = 20) -> dict[str, Any]:
    """Dispatch kline requests (currently A-stock only)."""
    try:
        return _fetch_a_kline(symbol, scale, count)
    except Exception as e:
        return {"error": f"Failed to fetch kline for '{symbol}': {e}", "symbol": symbol}


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
