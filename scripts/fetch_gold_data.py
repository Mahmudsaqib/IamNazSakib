"""Fetch gold OHLCV snapshots (runs inside GitHub Actions, where the internet is open).

Sources (best effort, every failure is logged, whatever succeeds is committed):
  1. Yahoo Finance via yfinance  -> COMEX GC=F futures (real volume) + XAUUSD=X spot
  2. TradingView via tvDatafeed (no-login mode) -> OANDA:XAUUSD, COMEX:GC1!
Outputs CSV files in data/raw/ plus fetch_log.txt / fetched_at.txt.
"""
from __future__ import annotations

import datetime as dt
import pathlib
import traceback

OUT = pathlib.Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)
LOG: list[str] = []


def log(msg: str) -> None:
    print(msg, flush=True)
    LOG.append(msg)


def save(df, path: pathlib.Path, label: str) -> None:
    if df is None or len(df) == 0:
        log(f"{label}: EMPTY")
        return
    df.to_csv(path)
    log(f"{label}: {len(df)} rows  first={df.index[0]}  last={df.index[-1]}")


# ---------------------------------------------------------------- 1) yfinance
try:
    import yfinance as yf

    for sym, name in [("GC=F", "gc"), ("XAUUSD=X", "xau")]:
        for interval, period in [("5m", "5d"), ("15m", "1mo"), ("1h", "3mo"), ("1d", "2y")]:
            label = f"yf {sym} {interval}/{period}"
            try:
                df = yf.download(
                    sym, interval=interval, period=period, progress=False,
                    auto_adjust=False, prepost=False, threads=False,
                )
                if df is not None and len(df) and hasattr(df.columns, "levels"):
                    df.columns = df.columns.get_level_values(0)
                if df is not None and len(df):
                    df.index.name = "time"
                    df = df[["Open", "High", "Low", "Close", "Volume"]]
                save(df, OUT / f"{name}_{interval}_{period}.csv", label)
            except Exception as exc:  # noqa: BLE001
                log(f"{label}: ERROR {exc!r}")
except Exception as exc:  # noqa: BLE001
    log(f"yfinance unavailable: {exc!r}")
    traceback.print_exc()

# ---------------------------------------------------------------- 2) TradingView (tvDatafeed)
try:
    from tvDatafeed import Interval, TvDatafeed

    tv = TvDatafeed()  # no-login mode
    plan = [
        (Interval.in_5_minute, 2000, "5m"),
        (Interval.in_15_minute, 3000, "15m"),
        (Interval.in_1_hour, 2000, "1h"),
        (Interval.in_4_hour, 1000, "4h"),
        (Interval.in_daily, 1200, "1d"),
        (Interval.in_weekly, 600, "1w"),
        (Interval.in_monthly, 240, "1mo"),
    ]
    for sym, exch, name in [("XAUUSD", "OANDA", "tv_xau"), ("GC1!", "COMEX", "tv_gc")]:
        for iv, n_bars, tag in plan:
            label = f"tv {exch}:{sym} {tag}"
            try:
                df = tv.get_hist(symbol=sym, exchange=exch, interval=iv, n_bars=n_bars)
                save(df, OUT / f"{name}_{tag}.csv", label)
            except Exception as exc:  # noqa: BLE001
                log(f"{label}: ERROR {exc!r}")
except Exception as exc:  # noqa: BLE001
    log(f"tvDatafeed unavailable: {exc!r}")
    traceback.print_exc()

(OUT / "fetch_log.txt").write_text("\n".join(LOG) + "\n")
(OUT / "fetched_at.txt").write_text(dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") + "\n")
log("done")
