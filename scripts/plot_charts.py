"""Render the ICT / volume-profile charts for XAUUSD from data/raw (TradingView OANDA + COMEX).

Snapshot annotations live in the SNAPSHOT dict below; update them after each re-analysis
(`python scripts/ict_analysis.py` prints the fresh structure / FVG / OB / level numbers).
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from ict_analysis import NY, load, volume_profile  # noqa: E402

OUT = pathlib.Path("analysis/out")
OUT.mkdir(parents=True, exist_ok=True)
UP, DN = "#26a69a", "#ef5350"
RED, GRN, PUR, ORG, GRY, BLU = "#b71c1c", "#1b5e20", "#6a1b9a", "#ff9800", "#757575", "#1e88e5"

# ----------------------------------------------------------------------------- snapshot (2026-10-15 14:55 UTC)
SNAPSHOT = {
    "m15_start": "2026-10-14 12:00",
    "m15_ylim": (4065, 4225),
    "m5_start": "2026-10-15 10:00",
    "m5_ylim": (4120, 4192),
    # (y0, y1, color, label, alpha, start_time)
    "zones_15m": [
        (4166.62, 4179.70, RED, "4h bear FVG 4166.6-4179.7 (CE 4173.2) rejected once", 0.14, "2026-10-14 12:00"),
        (4173.19, 4177.56, RED, "1h bear FVG 4173.2-4177.6 (untouched)", 0.22, "2026-10-14 12:00"),
        (4149.94, 4155.07, GRN, "5m bull FVG 4149.9-4155.1 / session POC 4155.5", 0.18, "2026-10-15 14:20"),
        (4136.56, 4151.54, PUR, "BUY 1: 1h bull OB (MT 4144) -> 4144-4150", 0.10, "2026-10-15 01:00"),
        (4130.91, 4137.19, GRN, "BUY 2: FVG 4130.9-4137.2 + EQL 4130.2/4131.6 (held twice)", 0.28, "2026-10-15 00:15"),
        (4112.80, 4128.03, GRN, "BUY 3 / last line: FVG 4112.8-4128.0 (CE 4120.4)", 0.20, "2026-10-15 00:00"),
    ],
    # (y, label, color, ls, lw, va)
    "levels_15m": [
        (4217.395, "T3 range high 4217.4", GRY, "--", 1.0, "bottom"),
        (4207.485, "PWH 4207.5", GRY, ":", 1.0, "bottom"),
        (4200.625, "T2 Oct-13 high 4200.6", GRY, "--", 1.0, "bottom"),
        (4189.585, "T1 weekly open 4189.6 = MAIN TARGET", BLU, "-", 1.4, "bottom"),
        (4170.49, "PDH 4170.5 = first target (unclaimed)", RED, "-", 1.4, "bottom"),
        (4168.72, "today high 4168.7", GRY, ":", 1.0, "top"),
        (4145.005, "NY-AM low 4145.0", GRN, ":", 1.0, "top"),
        (4141.97, "Daily EQ 4142.0", ORG, "-.", 1.2, "top"),
        (4139.0, "today VAL 4139", GRY, ":", 0.9, "top"),
        (4130.245, "EQL 4130.2 / 4131.6 (London + PPI sweeps)", GRN, "--", 1.2, "top"),
        (4105.64, "INVALIDATION 4105.6 (15m close below)", RED, "--", 1.2, "top"),
        (4099.89, "today low 4099.9", GRY, "--", 1.0, "top"),
        (4073.545, "PDL 4073.5", RED, ":", 1.0, "top"),
    ],
    "sessions_15m": [
        ("2026-10-14 11:00", "2026-10-14 14:00", "Wed NY AM (CPI)", "#fb8c00"),
        ("2026-10-15 00:00", "2026-10-15 04:00", "Asia", "#607d8b"),
        ("2026-10-15 06:00", "2026-10-15 09:00", "London KZ", "#8e24aa"),
        ("2026-10-15 11:00", "2026-10-15 14:00", "NY AM (PPI 12:30)", "#fb8c00"),
        ("2026-10-15 17:30", "2026-10-15 20:00", "NY PM (next)", BLU),
    ],
    "notes_15m": [
        ("2026-10-15 06:00", 4131.6, "2026-10-14 14:30", 4120, "06:00 London: sweep of EQL 4136 into FVG\n= BUY A filled -> 4160 (+$29)", GRN),
        ("2026-10-15 12:30", 4130.2, "2026-10-14 19:00", 4096, "12:30 PPI 1.3% m/m (hot) -> spike to 4130.2\nabsorbed in 5 min (4046 contracts) = bear trap", GRN),
        ("2026-10-15 13:15", 4168.7, "2026-10-14 15:30", 4200, "13:15 high 4168.7: rejected at 4h FVG bottom,\n$1.8 short of PDH -> PDH still a magnet", RED),
    ],
}


def candles(ax, df: pd.DataFrame, width_min: float):
    w = width_min / (24 * 60) * 0.8
    for t, r in df.iterrows():
        x = mdates.date2num(t.tz_convert(None) if t.tzinfo else t)
        c = UP if r.close >= r.open else DN
        ax.plot([x, x], [r.low, r.high], color=c, lw=0.8, zorder=2)
        ax.add_patch(Rectangle((x - w / 2, min(r.open, r.close)), w, max(abs(r.close - r.open), 0.05), facecolor=c, edgecolor=c, lw=0.6, zorder=3))


def hline(ax, y, label, color=GRY, ls="--", lw=1.0, x_text=None, va="bottom", fs=8, ha="left"):
    ax.axhline(y, color=color, ls=ls, lw=lw, zorder=1)
    ax.text(ax.get_xlim()[1] if x_text is None else x_text, y, f" {label}", color=color, fontsize=fs, va=va, ha=ha, zorder=6, clip_on=False,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))


def box(ax, x0, x1, y0, y1, color, label=None, alpha=0.18, fs=7.5, text_color=None, hatch=None, label_x=None, va="bottom"):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=color, edgecolor=color, alpha=alpha, lw=0.8, zorder=1, hatch=hatch))
    if label:
        ax.text(x0 if label_x is None else label_x, y1 if va == "bottom" else y0, f" {label}", color=text_color or color, fontsize=fs, va=va, ha="left", zorder=6,
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.6))


def num(ts: str) -> float:
    return mdates.date2num(pd.Timestamp(ts).tz_localize(None))


# ----------------------------------------------------------------------------- data
x15 = load("tv_xau_15m.csv").tz_convert("UTC")
x5 = load("tv_xau_5m.csv").tz_convert("UTC")
g5 = load("tv_gc_5m.csv").tz_convert("UTC")
g15 = load("tv_gc_15m.csv").tz_convert("UTC")
xd = load("tv_xau_1d.csv")
last = x15.index[-1]
price = float(x15.close.iloc[-1])
stamp = f"{last.strftime('%Y-%m-%d %H:%M')} UTC  ({last.tz_convert(NY).strftime('%H:%M')} NY)"
S = SNAPSHOT

# ----------------------------------------------------------------------------- chart 1: 15m ICT map + VP
seg = x15[x15.index >= S["m15_start"]]
fig = plt.figure(figsize=(18, 10), dpi=130)
gs = fig.add_gridspec(1, 2, width_ratios=[5.2, 1], wspace=0.02)
ax = fig.add_subplot(gs[0, 0])
axv = fig.add_subplot(gs[0, 1], sharey=ax)
candles(ax, seg, 15)
x0 = num(str(seg.index[0] - pd.Timedelta(hours=9)))
x1 = num(str(last + pd.Timedelta(hours=14)))
ax.set_xlim(x0, x1)
ax.set_ylim(*S["m15_ylim"])
xend = num(str(last))
for a, b, lab, col in S["sessions_15m"]:
    ax.axvspan(num(a), num(b), color=col, alpha=0.06, zorder=0)
    ax.text(num(a), S["m15_ylim"][1] - 1.5, lab, fontsize=8, color=col, va="top")
for y0, y1, col, lab, al, start in S["zones_15m"]:
    box(ax, num(start), x1, y0, y1, col, None, alpha=al)
    ax.text(num(str(last + pd.Timedelta(minutes=30))), (y0 + y1) / 2, lab, color=col, fontsize=7.5, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
for y, lab, col, ls, lw, va in S["levels_15m"]:
    hline(ax, y, lab, col, ls, lw, x_text=x0, va=va)
for xa, ya, xt, yt, txt, col in S["notes_15m"]:
    ax.annotate(txt, xy=(num(xa), ya), xytext=(num(xt), yt), fontsize=8, color=col, arrowprops=dict(arrowstyle="->", color=col), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=col, alpha=0.85))
ax.annotate(f"now {price:.1f}", xy=(xend, price), xytext=(xend + 0.03, price + 9), fontsize=9, color="black", arrowprops=dict(arrowstyle="->", color="black"), zorder=7)
ax.set_title(f"XAUUSD 15m (OANDA via TradingView) - ICT map   |   last bar {stamp}", fontsize=11, loc="left")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M", tz="UTC"))
ax.grid(alpha=0.15)
ax.set_ylabel("USD / oz")

vp = volume_profile(x15[x15.index >= "2026-10-01"], 2.0)
cent, vol = np.array(vp["bins"]["centers"]), np.array(vp["bins"]["volume"])
colors = ["#90a4ae" if not (vp["VAL"] <= c <= vp["VAH"]) else "#5c6bc0" for c in cent]
axv.barh(cent, vol, height=1.8, color=colors, alpha=0.85)
axv.axhline(vp["POC"], color="#e65100", lw=1.6)
axv.axhline(vp["VAH"], color="#283593", lw=1.0, ls="--")
axv.axhline(vp["VAL"], color="#283593", lw=1.0, ls="--")
axv.text(vol.max() * 0.98, vp["POC"], f"POC {vp['POC']:.0f}", ha="right", va="bottom", fontsize=8, color="#e65100")
axv.text(vol.max() * 0.98, vp["VAH"], f"VAH {vp['VAH']:.0f}", ha="right", va="bottom", fontsize=8, color="#283593")
axv.text(vol.max() * 0.98, vp["VAL"], f"VAL {vp['VAL']:.0f}", ha="right", va="top", fontsize=8, color="#283593")
for l in vp["LVN"]:
    axv.text(vol.max() * 0.02, l, f"LVN {l:.0f}", fontsize=7, color="#555", va="center")
axv.axhline(price, color="black", lw=0.8)
axv.set_title("Vol. profile Oct 1-15\n(OANDA tick vol)", fontsize=9)
axv.tick_params(labelleft=False)
axv.set_xticks([])
axv.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_15m_ict_map.png", bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------- chart 2: daily HTF
d = xd[xd.index >= "2026-06-01"]
fig, ax = plt.subplots(figsize=(16, 8), dpi=130)
candles(ax, d, 24 * 60)
x0, x1 = num(str(d.index[0])), num(str(d.index[-1] + pd.Timedelta(days=9)))
ax.set_xlim(x0, x1)
ax.set_ylim(3880, 4760)
box(ax, num("2026-06-10"), num("2026-08-05"), 3942, 4166, "#9e9e9e", "Jun-Aug accumulation base 3942-4166", alpha=0.12)
box(ax, num("2026-08-03"), x1, 4019.24, 4079.2, UP, "Aug-3 daily bullish OB 4019-4079 (origin of Aug rally) - Wed low 4073.5 tapped it", alpha=0.15)
box(ax, num("2026-10-07"), x1, 4066.535, 4217.395, ORG, None, alpha=0.08)
box(ax, num("2026-09-28"), x1, 4200.33, 4257.69, RED, "4h bearish FVG 4200-4258 (CE 4229)", alpha=0.10)
hline(ax, 4217.395, "Oct-12 high 4217.4 (range high / LH) - daily trend flips only above", "#555")
hline(ax, 4141.97, "EQ 4142", ORG, "-.")
hline(ax, 4066.535, "Oct-7 low 4066.5 (range low / PWL)", "#c62828", "-", 1.4)
hline(ax, 4000, "4000 psych", "#9e9e9e", ":")
hline(ax, 3942.1, "Jun-30 low 3942 / Jul-17 3960 = deeper SSL", "#c62828", ":")
for t, p, lab in [("2026-08-25", 4697.105, "4697"), ("2026-09-03", 4510.93, "LH 4511"), ("2026-09-18", 4399.67, "LH 4400"), ("2026-10-02", 4227.53, "LH 4228"), ("2026-10-12", 4217.395, "LH 4217")]:
    ax.annotate(lab, xy=(num(t), p), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=RED)
for t, p, lab in [("2026-09-02", 4282.625, "4283"), ("2026-09-16", 4235.165, "HL 4235"), ("2026-09-28", 4110.87, "LL 4111 (swept Wed)"), ("2026-10-07", 4066.535, "LL 4066.5"), ("2026-10-14", 4073.545, "Wed 4073.5")]:
    ax.annotate(lab, xy=(num(t), p), xytext=(0, -12), textcoords="offset points", ha="center", fontsize=8, color=GRN)
ax.annotate(f"now {price:.0f}", xy=(num(str(d.index[-1])), price), xytext=(25, 25), textcoords="offset points", fontsize=9, arrowprops=dict(arrowstyle="->"))
ax.set_title(f"XAUUSD Daily (OANDA) - HTF still bearish (LH 4217 intact); Wed swept the Sep low and closed back >4100 = potential turtle soup   |   {stamp}", fontsize=10, loc="left")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_daily_htf.png", bbox_inches="tight")
plt.close(fig)

# ----------------------------------------------------------------------------- chart 3: 5m Asia rally + COMEX volume
s5 = x5[x5.index >= S["m5_start"]]
v5 = g5[g5.index >= S["m5_start"]]
avg_asia = float(g5[(g5.index >= "2026-10-12") & (g5.index < "2026-10-15")]["volume"].mean())
fig = plt.figure(figsize=(16, 9), dpi=130)
gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
ax = fig.add_subplot(gs[0, 0])
axb = fig.add_subplot(gs[1, 0], sharex=ax)
candles(ax, s5, 5)
x0, x1 = num(str(s5.index[0])), num(str(last + pd.Timedelta(minutes=120)))
ax.set_xlim(x0, x1)
ax.set_ylim(*S["m5_ylim"])
xr = num(str(last + pd.Timedelta(minutes=10)))
for y0, y1, col, lab, al, start in [
    (4166.62, 4179.70, RED, "4h bear FVG 4166.6-4179.7 (CE 4173.2) - must be cleared for T1", 0.14, "2026-10-15 10:00"),
    (4173.19, 4177.56, RED, "1h bear FVG 4173.2-4177.6 (counter-trend sell scalp zone)", 0.22, "2026-10-15 10:00"),
    (4149.94, 4155.07, GRN, "5m bull FVG 4149.9-4155.1 (CE 4152.5)", 0.18, "2026-10-15 14:20"),
    (4136.56, 4151.54, PUR, "1h bull OB 4136.6-4151.5 (MT 4144.0) = BUY 1 zone 4144-4150", 0.10, "2026-10-15 10:00"),
    (4130.91, 4137.19, GRN, "BUY 2 zone 4130.9-4137.2 (EQL 4130.2 / 4131.6)", 0.28, "2026-10-15 10:00"),
]:
    box(ax, num(start), x1, y0, y1, col, None, alpha=al)
    if lab:
        ax.text(xr, (y0 + y1) / 2, lab, color=col, fontsize=7.5, va="center", bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
hline(ax, 4189.585, "T1 weekly open 4189.6", BLU, "-", 1.2, x_text=x0)
hline(ax, 4170.49, "PDH 4170.5 (first target, unclaimed)", RED, "-", 1.2, x_text=x0)
hline(ax, 4168.72, "13:15 high 4168.7", GRY, ":", 1.0, x_text=x0, va="top")
hline(ax, 4164.92, "14:40 LH 4164.9 = minor BSL", GRY, ":", 1.0, x_text=x0, va="top")
hline(ax, 4160.64, "EQH 4160-4162 (swept 13:15)", GRY, ":", 0.8, x_text=x0, va="top")
hline(ax, 4145.005, "14:15 low 4145.0 (1h OB MT 4144)", GRN, "--", 1.0, x_text=x0, va="top")
hline(ax, 4141.97, "Daily EQ 4142", ORG, "-.", 1.0, x_text=x0, va="top")
hline(ax, 4130.245, "PPI low 4130.2 / London low 4131.6 = EQL", GRN, "--", 1.2, x_text=x0, va="top")
ax.annotate(f"now {price:.1f}", xy=(num(str(last)), price), xytext=(20, 18), textcoords="offset points", fontsize=9, arrowprops=dict(arrowstyle="->"))
ax.annotate("PPI spike absorbed in one 5m bar\n= bear trap / turtle soup #2", xy=(num("2026-10-15 12:30"), 4131), xytext=(num("2026-10-15 10:20"), 4123.5), fontsize=8, color=GRN, arrowprops=dict(arrowstyle="->", color=GRN))
ax.annotate("rejection at 4h FVG bottom;\nlower highs 4168.7 -> 4164.9 = NY-AM balance 4145-4169", xy=(num("2026-10-15 13:15"), 4168.7), xytext=(num("2026-10-15 10:20"), 4183), fontsize=8, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
ax.set_title(f"XAUUSD 5m - Thursday NY session (PPI) + COMEX GC1! real volume   |   {stamp}", fontsize=10, loc="left")
ax.tick_params(labelbottom=False)
ax.grid(alpha=0.15)
cols = [UP if r.close >= r.open else DN for _, r in v5.iterrows()]
axb.bar([mdates.date2num(t.tz_convert(None)) for t in v5.index], v5.volume.values, width=5 / (24 * 60) * 0.8, color=cols)
axb.axhline(avg_asia, color="#555", ls="--", lw=0.8)
axb.text(x0, avg_asia, f" 3-day avg 5m vol ~ {avg_asia:.0f}", fontsize=8, va="bottom", color="#555")
for t, txt in [("2026-10-15 12:30", "PPI 4046 (8.6x) sell"), ("2026-10-15 12:35", "3071 (6.6x) buy-back"), ("2026-10-15 13:15", "3187 (6.8x) wick at 4h FVG"), ("2026-10-15 14:00", "1903 (4.1x) dip bought")]:
    ts = pd.Timestamp(t, tz="UTC")
    v = float(v5.loc[ts, "volume"]) if ts in v5.index else 0
    axb.annotate(txt, xy=(num(t), v), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7.5)
axb.set_ylabel("COMEX contracts / 5m")
axb.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz="UTC"))
axb.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_5m_ny_session_volume.png", bbox_inches="tight")
plt.close(fig)
print("charts written:", sorted(p.name for p in OUT.glob("*.png")))
