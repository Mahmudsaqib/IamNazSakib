"""ICT + Volume-Profile analysis for XAUUSD / GC=F from the CSVs in data/raw.

Usage:  python scripts/ict_analysis.py  [--out analysis/out]

Computes (all times handled in UTC, sessions defined in New-York time):
  * HTF structure (daily / 4h / 1h): swing highs/lows, dealing range, equilibrium,
    premium/discount, previous day/week high-low (PDH/PDL/PWH/PWL)
  * Fair-value gaps (3-candle imbalances) and volume imbalances (body gaps)
  * Order blocks (last opposite candle before a displacement that breaks structure)
  * Liquidity pools: equal highs/lows, session highs/lows (Asia / London / NY)
  * Market-structure shift / CHoCH detection on 15m and 5m
  * Volume profile (POC / VAH / VAL / HVN / LVN) from COMEX GC=F volume
Writes a JSON report and PNG charts.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

RAW = pathlib.Path("data/raw")


# ----------------------------------------------------------------------------- loading
def load(name: str) -> pd.DataFrame | None:
    """Load a CSV produced by scripts/fetch_gold_data.py, index -> UTC DatetimeIndex."""
    p = RAW / name
    if not p.exists():
        return None
    df = pd.read_csv(p)
    tcol = df.columns[0]
    df[tcol] = pd.to_datetime(df[tcol], utc=True, errors="coerce")
    df = df.dropna(subset=[tcol]).set_index(tcol).sort_index()
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"vol": "volume"})
    for c in ("open", "high", "low", "close"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if "volume" in df:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    else:
        df["volume"] = 0.0
    df = df.dropna(subset=["open", "high", "low", "close"])
    df = df[~df.index.duplicated(keep="last")]
    # Daily bars from TradingView/COMEX are stamped at the 17:00/18:00-NY session open of the
    # previous calendar day -> move them onto the session date (NY) at 00:00 UTC.
    if len(df) > 3 and pd.Series(df.index).diff().median() >= pd.Timedelta(hours=20):
        df.index = (df.index + pd.Timedelta(hours=5)).normalize()
        df = df[~df.index.duplicated(keep="last")]
    return df


def first_available(*names: str) -> tuple[str | None, pd.DataFrame | None]:
    for n in names:
        df = load(n)
        if df is not None and len(df) > 10:
            return n, df
    return None, None


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    o = df.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    return o.dropna(subset=["open"])


# ----------------------------------------------------------------------------- structure
@dataclass
class Swing:
    time: str
    price: float
    kind: str  # "high" | "low"


def swings(df: pd.DataFrame, left: int = 3, right: int = 3) -> list[Swing]:
    hi, lo = df["high"].values, df["low"].values
    out: list[Swing] = []
    for i in range(left, len(df) - right):
        if hi[i] == hi[i - left : i + right + 1].max() and (hi[i] > hi[i - left : i]).all():
            out.append(Swing(str(df.index[i]), float(hi[i]), "high"))
        if lo[i] == lo[i - left : i + right + 1].min() and (lo[i] < lo[i - left : i]).all():
            out.append(Swing(str(df.index[i]), float(lo[i]), "low"))
    out.sort(key=lambda s: s.time)
    return out


def structure_bias(sw: list[Swing]) -> dict:
    highs = [s for s in sw if s.kind == "high"][-3:]
    lows = [s for s in sw if s.kind == "low"][-3:]
    hh = len(highs) >= 2 and highs[-1].price > highs[-2].price
    hl = len(lows) >= 2 and lows[-1].price > lows[-2].price
    lh = len(highs) >= 2 and highs[-1].price < highs[-2].price
    ll = len(lows) >= 2 and lows[-1].price < lows[-2].price
    if lh and ll:
        bias = "bearish"
    elif hh and hl:
        bias = "bullish"
    elif lh or ll:
        bias = "bearish-leaning"
    elif hh or hl:
        bias = "bullish-leaning"
    else:
        bias = "ranging"
    return {
        "bias": bias,
        "last_highs": [asdict(h) for h in highs],
        "last_lows": [asdict(l) for l in lows],
    }


def dealing_range(sw: list[Swing], price: float) -> dict:
    """Most recent significant swing high and swing low bracketing current price."""
    highs = [s for s in sw if s.kind == "high" and s.price > price]
    lows = [s for s in sw if s.kind == "low" and s.price < price]
    if not highs or not lows:
        return {}
    hi = highs[-1]
    lo = lows[-1]
    eq = (hi.price + lo.price) / 2
    pos = (price - lo.price) / (hi.price - lo.price) if hi.price != lo.price else 0.5
    return {
        "range_high": asdict(hi),
        "range_low": asdict(lo),
        "equilibrium": round(eq, 2),
        "price_position_pct": round(pos * 100, 1),
        "zone": "premium" if price > eq else "discount",
        "ote_buy_zone": [round(lo.price + (hi.price - lo.price) * 0.21, 2), round(lo.price + (hi.price - lo.price) * 0.38, 2)],
        "ote_sell_zone": [round(lo.price + (hi.price - lo.price) * 0.62, 2), round(lo.price + (hi.price - lo.price) * 0.79, 2)],
    }


# ----------------------------------------------------------------------------- PD arrays
def fvgs(df: pd.DataFrame, min_size: float = 0.0, lookback: int = 400) -> list[dict]:
    """3-candle fair value gaps. Bullish: low[i+1] > high[i-1]; bearish: high[i+1] < low[i-1]."""
    d = df.iloc[-lookback:]
    hi, lo, cl = d["high"].values, d["low"].values, d["close"].values
    out = []
    for i in range(1, len(d) - 1):
        if lo[i + 1] > hi[i - 1] and (lo[i + 1] - hi[i - 1]) >= min_size:
            top, bot = lo[i + 1], hi[i - 1]
            kind = "bullish"
        elif hi[i + 1] < lo[i - 1] and (lo[i - 1] - hi[i + 1]) >= min_size:
            top, bot = lo[i - 1], hi[i + 1]
            kind = "bearish"
        else:
            continue
        # mitigation: has price traded back into / through the gap afterwards?
        after = d.iloc[i + 2 :]
        if kind == "bullish":
            filled = bool((after["low"] <= bot).any()) if len(after) else False
            touched = bool((after["low"] <= top).any()) if len(after) else False
        else:
            filled = bool((after["high"] >= top).any()) if len(after) else False
            touched = bool((after["high"] >= bot).any()) if len(after) else False
        out.append(
            {
                "time": str(d.index[i]),
                "kind": kind,
                "top": round(float(top), 2),
                "bottom": round(float(bot), 2),
                "ce": round(float((top + bot) / 2), 2),
                "size": round(float(top - bot), 2),
                "touched": touched,
                "filled": filled,
            }
        )
    return out


def volume_imbalances(df: pd.DataFrame, lookback: int = 300, min_size: float = 0.5) -> list[dict]:
    """ICT volume imbalance: gap between consecutive candle BODIES while wicks overlap."""
    d = df.iloc[-lookback:]
    o, h, l, c = d["open"].values, d["high"].values, d["low"].values, d["close"].values
    out = []
    for i in range(1, len(d)):
        b1_top, b1_bot = max(o[i - 1], c[i - 1]), min(o[i - 1], c[i - 1])
        b2_top, b2_bot = max(o[i], c[i]), min(o[i], c[i])
        if b2_bot > b1_top and (b2_bot - b1_top) >= min_size and l[i] <= h[i - 1]:
            out.append({"time": str(d.index[i]), "kind": "bullish", "top": round(float(b2_bot), 2), "bottom": round(float(b1_top), 2)})
        elif b2_top < b1_bot and (b1_bot - b2_top) >= min_size and h[i] >= l[i - 1]:
            out.append({"time": str(d.index[i]), "kind": "bearish", "top": round(float(b1_bot), 2), "bottom": round(float(b2_top), 2)})
    return out


def order_blocks(df: pd.DataFrame, sw: list[Swing], lookback: int = 400) -> list[dict]:
    """Bearish OB: last up-candle before a displacement that breaks a swing low.
    Bullish OB: last down-candle before a displacement that breaks a swing high."""
    d = df.iloc[-lookback:]
    idx = list(d.index.astype(str))
    out = []
    sw_lows = [s for s in sw if s.kind == "low"]
    sw_highs = [s for s in sw if s.kind == "high"]
    o, h, l, c = d["open"].values, d["high"].values, d["low"].values, d["close"].values
    for i in range(2, len(d)):
        # bearish displacement candle closing below a prior swing low
        prior_lows = [s for s in sw_lows if s.time < idx[i] and s.time >= idx[0]]
        if prior_lows and c[i] < prior_lows[-1].price and c[i] < o[i] and (o[i] - c[i]) > 0.6 * (h[i] - l[i]):
            # walk back to last up candle
            j = i - 1
            while j > 0 and c[j] <= o[j]:
                j -= 1
            if j > 0:
                top, bot = float(h[j]), float(l[j])
                after = d.iloc[i + 1 :]
                mitigated = bool((after["high"] >= bot).any()) if len(after) else False
                out.append({"time": idx[j], "kind": "bearish", "top": round(top, 2), "bottom": round(bot, 2), "mean_threshold": round((top + bot) / 2, 2), "broke": prior_lows[-1].price, "mitigated": mitigated})
        prior_highs = [s for s in sw_highs if s.time < idx[i] and s.time >= idx[0]]
        if prior_highs and c[i] > prior_highs[-1].price and c[i] > o[i] and (c[i] - o[i]) > 0.6 * (h[i] - l[i]):
            j = i - 1
            while j > 0 and c[j] >= o[j]:
                j -= 1
            if j > 0:
                top, bot = float(h[j]), float(l[j])
                after = d.iloc[i + 1 :]
                mitigated = bool((after["low"] <= top).any()) if len(after) else False
                out.append({"time": idx[j], "kind": "bullish", "top": round(top, 2), "bottom": round(bot, 2), "mean_threshold": round((top + bot) / 2, 2), "broke": prior_highs[-1].price, "mitigated": mitigated})
    # de-duplicate by (kind, time)
    seen, uniq = set(), []
    for ob in out:
        k = (ob["kind"], ob["time"])
        if k not in seen:
            seen.add(k)
            uniq.append(ob)
    return uniq


def equal_levels(sw: list[Swing], tol: float = 2.0) -> dict:
    eqh, eql = [], []
    highs = [s for s in sw if s.kind == "high"]
    lows = [s for s in sw if s.kind == "low"]
    for a, b in zip(highs, highs[1:]):
        if abs(a.price - b.price) <= tol:
            eqh.append({"level": round((a.price + b.price) / 2, 2), "times": [a.time, b.time]})
    for a, b in zip(lows, lows[1:]):
        if abs(a.price - b.price) <= tol:
            eql.append({"level": round((a.price + b.price) / 2, 2), "times": [a.time, b.time]})
    return {"equal_highs": eqh[-5:], "equal_lows": eql[-5:]}


def mss(df: pd.DataFrame, sw: list[Swing], lookback: int = 200) -> dict:
    """Latest market-structure shift: close beyond the most recent opposing swing."""
    d = df.iloc[-lookback:]
    last_high = [s for s in sw if s.kind == "high"][-1:] or None
    last_low = [s for s in sw if s.kind == "low"][-1:] or None
    res = {"bullish_mss": None, "bearish_mss": None}
    if last_high:
        lh = last_high[0]
        after = d[d.index.astype(str) > lh.time]
        brk = after[after["close"] > lh.price]
        if len(brk):
            res["bullish_mss"] = {"broke_high": lh.price, "at": str(brk.index[0]), "close": float(brk["close"].iloc[0])}
    if last_low:
        ll = last_low[0]
        after = d[d.index.astype(str) > ll.time]
        brk = after[after["close"] < ll.price]
        if len(brk):
            res["bearish_mss"] = {"broke_low": ll.price, "at": str(brk.index[0]), "close": float(brk["close"].iloc[0])}
    return res


# ----------------------------------------------------------------------------- sessions
NY = "America/New_York"


def session_ranges(df: pd.DataFrame, day: pd.Timestamp) -> dict:
    """Asia (20:00-00:00 prev day NY), London (02:00-05:00 NY), NY AM (07:00-10:00), NY PM (13:30-16:00)."""
    ny = df.tz_convert(NY)
    d0 = day.tz_convert(NY).normalize()
    spans = {
        "asia": (d0 - pd.Timedelta(hours=4), d0),  # 20:00 prev day -> 00:00
        "asia_late": (d0, d0 + pd.Timedelta(hours=2)),  # 00:00 -> 02:00
        "london_kz": (d0 + pd.Timedelta(hours=2), d0 + pd.Timedelta(hours=5)),
        "ny_am_kz": (d0 + pd.Timedelta(hours=7), d0 + pd.Timedelta(hours=10)),
        "ny_lunch": (d0 + pd.Timedelta(hours=12), d0 + pd.Timedelta(hours=13, minutes=30)),
        "ny_pm": (d0 + pd.Timedelta(hours=13, minutes=30), d0 + pd.Timedelta(hours=16)),
    }
    out = {}
    for k, (a, b) in spans.items():
        seg = ny[(ny.index >= a) & (ny.index < b)]
        if len(seg):
            out[k] = {"high": float(seg["high"].max()), "low": float(seg["low"].min()), "bars": int(len(seg))}
    return out


def daily_levels(d1: pd.DataFrame) -> dict:
    d = d1.copy()
    out = {}
    if len(d) >= 2:
        prev, cur = d.iloc[-2], d.iloc[-1]
        out["PDH"], out["PDL"], out["PDC"] = float(prev["high"]), float(prev["low"]), float(prev["close"])
        out["today_open"], out["today_high"], out["today_low"] = float(cur["open"]), float(cur["high"]), float(cur["low"])
    w = d.resample("W-FRI", label="right", closed="right").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    if len(w) >= 2:
        out["PWH"], out["PWL"], out["PWC"] = float(w.iloc[-2]["high"]), float(w.iloc[-2]["low"]), float(w.iloc[-2]["close"])
        out["week_high"], out["week_low"], out["week_open"] = float(w.iloc[-1]["high"]), float(w.iloc[-1]["low"]), float(w.iloc[-1]["open"])
    m = d.resample("MS").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    if len(m) >= 2:
        out["PMH"], out["PML"] = float(m.iloc[-2]["high"]), float(m.iloc[-2]["low"])
        out["month_open"], out["month_high"], out["month_low"] = float(m.iloc[-1]["open"]), float(m.iloc[-1]["high"]), float(m.iloc[-1]["low"])
    return out


# ----------------------------------------------------------------------------- volume profile
def volume_profile(df: pd.DataFrame, bin_size: float = 2.0, va_pct: float = 0.70) -> dict:
    """Distribute each bar's volume uniformly across its high-low range."""
    lo, hi = float(df["low"].min()), float(df["high"].max())
    edges = np.arange(np.floor(lo / bin_size) * bin_size, np.ceil(hi / bin_size) * bin_size + bin_size, bin_size)
    vol = np.zeros(len(edges) - 1)
    for h, l, v in zip(df["high"].values, df["low"].values, df["volume"].values):
        if v <= 0:
            continue
        a = np.searchsorted(edges, l, side="right") - 1
        b = np.searchsorted(edges, h, side="left")
        a, b = max(a, 0), min(max(b, a + 1), len(vol))
        vol[a:b] += v / (b - a)
    if vol.sum() == 0:
        return {}
    poc_i = int(vol.argmax())
    # value area: expand from POC until 70% of volume captured
    total, acc = vol.sum(), vol[poc_i]
    lo_i, hi_i = poc_i, poc_i
    while acc < va_pct * total and (lo_i > 0 or hi_i < len(vol) - 1):
        up = vol[hi_i + 1] if hi_i < len(vol) - 1 else -1
        dn = vol[lo_i - 1] if lo_i > 0 else -1
        if up >= dn:
            hi_i += 1
            acc += up
        else:
            lo_i -= 1
            acc += dn
    centers = (edges[:-1] + edges[1:]) / 2
    # HVN / LVN: local maxima / minima of smoothed profile
    k = 3
    sm = np.convolve(vol, np.ones(k) / k, mode="same")
    hvn, lvn = [], []
    for i in range(1, len(sm) - 1):
        if sm[i] > sm[i - 1] and sm[i] >= sm[i + 1] and sm[i] > 0.5 * sm.max():
            hvn.append(round(float(centers[i]), 1))
        if sm[i] < sm[i - 1] and sm[i] <= sm[i + 1] and sm[i] < 0.25 * sm.max() and edges[0] + 4 * bin_size < centers[i] < edges[-1] - 4 * bin_size:
            lvn.append(round(float(centers[i]), 1))
    return {
        "range": [round(lo, 2), round(hi, 2)],
        "POC": round(float(centers[poc_i]), 1),
        "VAH": round(float(edges[hi_i + 1]), 1),
        "VAL": round(float(edges[lo_i]), 1),
        "HVN": hvn,
        "LVN": lvn,
        "bins": {"centers": centers.round(1).tolist(), "volume": vol.round(0).tolist()},
    }


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="analysis/out")
    args = ap.parse_args()
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Prefer TradingView OANDA spot for price structure, COMEX futures for volume.
    n5, spot5 = first_available("tv_xau_5m.csv", "xau_5m_5d.csv", "tv_gc_5m.csv", "gc_5m_5d.csv")
    n15, spot15 = first_available("tv_xau_15m.csv", "xau_15m_1mo.csv", "tv_gc_15m.csv", "gc_15m_1mo.csv")
    n1h, spot1h = first_available("tv_xau_1h.csv", "xau_1h_3mo.csv", "tv_gc_1h.csv", "gc_1h_3mo.csv")
    n1d, spot1d = first_available("tv_xau_1d.csv", "xau_1d_2y.csv", "tv_gc_1d.csv", "gc_1d_2y.csv")
    nv15, fut15 = first_available("tv_gc_15m.csv", "gc_15m_1mo.csv")
    nv5, fut5 = first_available("tv_gc_5m.csv", "gc_5m_5d.csv")
    if spot15 is None or spot1d is None:
        print("missing core data", file=sys.stderr)
        print((RAW / "fetch_log.txt").read_text() if (RAW / "fetch_log.txt").exists() else "no log")
        return 1

    report: dict = {"sources": {"5m": n5, "15m": n15, "1h": n1h, "1d": n1d, "vol15m": nv15, "vol5m": nv5}}
    price = float(spot15["close"].iloc[-1])
    last_t = spot15.index[-1]
    report["last_bar_utc"] = str(last_t)
    report["last_bar_ny"] = str(last_t.tz_convert(NY))
    report["price"] = price

    # HTF
    sw_d = swings(spot1d, 2, 2)
    report["daily"] = {"structure": structure_bias(sw_d), "dealing_range": dealing_range(sw_d, price), "levels": daily_levels(spot1d)}
    h4 = resample(spot1h, "4h") if spot1h is not None else None
    if h4 is not None and len(h4) > 20:
        sw_4 = swings(h4, 3, 3)
        report["h4"] = {"structure": structure_bias(sw_4), "dealing_range": dealing_range(sw_4, price), "fvg_open": [f for f in fvgs(h4, 1.0, 300) if not f["filled"]][-8:], "swings": [asdict(s) for s in sw_4[-8:]]}
    if spot1h is not None:
        sw_1 = swings(spot1h, 3, 3)
        report["h1"] = {
            "structure": structure_bias(sw_1),
            "dealing_range": dealing_range(sw_1, price),
            "fvg_open": [f for f in fvgs(spot1h, 1.0, 300) if not f["filled"]][-10:],
            "order_blocks": order_blocks(spot1h, sw_1, 300)[-6:],
            "equal_levels": equal_levels(sw_1, 2.5),
            "mss": mss(spot1h, sw_1),
            "swings": [asdict(s) for s in sw_1[-10:]],
        }
    # LTF
    sw_15 = swings(spot15, 3, 3)
    report["m15"] = {
        "structure": structure_bias(sw_15),
        "dealing_range": dealing_range(sw_15, price),
        "fvg_open": [f for f in fvgs(spot15, 0.8, 300) if not f["filled"]][-12:],
        "volume_imbalances": volume_imbalances(spot15, 150, 0.8)[-10:],
        "order_blocks": order_blocks(spot15, sw_15, 300)[-6:],
        "equal_levels": equal_levels(sw_15, 1.5),
        "mss": mss(spot15, sw_15),
        "swings": [asdict(s) for s in sw_15[-12:]],
        "sessions_today": session_ranges(spot15, last_t),
        "sessions_prev_day": session_ranges(spot15, last_t - pd.Timedelta(days=1)),
    }
    if spot5 is not None:
        sw_5 = swings(spot5, 3, 3)
        report["m5"] = {
            "structure": structure_bias(sw_5),
            "fvg_open": [f for f in fvgs(spot5, 0.5, 300) if not f["filled"]][-12:],
            "order_blocks": order_blocks(spot5, sw_5, 300)[-6:],
            "mss": mss(spot5, sw_5),
            "swings": [asdict(s) for s in sw_5[-12:]],
        }
    # volume profiles (COMEX volume)
    if fut15 is not None:
        ny = fut15.tz_convert(NY)
        today = ny.index[-1].normalize()
        vp = {}
        vp["today"] = volume_profile(ny[ny.index >= today], 1.0)
        vp["prev_day"] = volume_profile(ny[(ny.index >= today - pd.Timedelta(days=1)) & (ny.index < today)], 1.0)
        vp["last_5d"] = volume_profile(fut15[fut15.index >= fut15.index[-1] - pd.Timedelta(days=5)], 2.0)
        month_start = pd.Timestamp(fut15.index[-1].year, fut15.index[-1].month, 1, tz="UTC")
        vp["month_to_date"] = volume_profile(fut15[fut15.index >= month_start], 2.0)
        vp["full_1mo"] = volume_profile(fut15, 2.0)
        for k in vp:
            vp[k].pop("bins", None) if k != "month_to_date" else None
        report["volume_profile"] = vp
        # today's volume behaviour by session
        rows = []
        for t, r in ny[ny.index >= today].iterrows():
            rows.append((t.strftime("%H:%M"), float(r["volume"])))
        report["today_volume_by_bar_ny"] = rows

    (out_dir / "report.json").write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps({k: v for k, v in report.items() if k not in ("today_volume_by_bar_ny",)}, indent=1, default=str)[:20000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
