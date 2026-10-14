"""Render the ICT / volume-profile charts for XAUUSD from data/raw (TradingView OANDA + COMEX)."""
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


def candles(ax, df: pd.DataFrame, width_min: float):
    w = width_min / (24 * 60) * 0.8
    for t, r in df.iterrows():
        x = mdates.date2num(t.tz_convert(None) if t.tzinfo else t)
        c = UP if r.close >= r.open else DN
        ax.plot([x, x], [r.low, r.high], color=c, lw=0.8, zorder=2)
        ax.add_patch(Rectangle((x - w / 2, min(r.open, r.close)), w, max(abs(r.close - r.open), 0.05), facecolor=c, edgecolor=c, lw=0.6, zorder=3))


def hline(ax, y, label, color="#999", ls="--", lw=1.0, x_text=None, va="bottom", fs=8, ha="left"):
    ax.axhline(y, color=color, ls=ls, lw=lw, zorder=1)
    ax.text(ax.get_xlim()[1] if x_text is None else x_text, y, f" {label}", color=color, fontsize=fs, va=va, ha=ha, zorder=6, clip_on=False, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))


def box(ax, x0, x1, y0, y1, color, label=None, alpha=0.18, fs=8, text_color=None, hatch=None):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=color, edgecolor=color, alpha=alpha, lw=0.8, zorder=1, hatch=hatch))
    if label:
        ax.text(x0, y1, f" {label}", color=text_color or color, fontsize=fs, va="bottom", ha="left", zorder=6)


def num(ts: str) -> float:
    return mdates.date2num(pd.Timestamp(ts).tz_localize(None))


# ---------------------------------------------------------------------------- data
x15 = load("tv_xau_15m.csv").tz_convert("UTC")
x5 = load("tv_xau_5m.csv").tz_convert("UTC")
g5 = load("tv_gc_5m.csv").tz_convert("UTC")
xd = load("tv_xau_1d.csv")
last = x15.index[-1]
price = float(x15.close.iloc[-1])
stamp = f"{last.strftime('%Y-%m-%d %H:%M')} UTC  ({last.tz_convert(NY).strftime('%H:%M')} NY)"

# ---------------------------------------------------------------------------- chart 1: 15m ICT map + VP
seg = x15[x15.index >= "2026-10-13 00:00"]
fig = plt.figure(figsize=(17, 9.5), dpi=130)
gs = fig.add_gridspec(1, 2, width_ratios=[5.2, 1], wspace=0.02)
ax = fig.add_subplot(gs[0, 0])
axv = fig.add_subplot(gs[0, 1], sharey=ax)
candles(ax, seg, 15)
x0, x1 = num(str(seg.index[0] - pd.Timedelta(hours=8))), num(str(last + pd.Timedelta(hours=12)))
ax.set_xlim(x0, x1)
ax.set_ylim(4040, 4215)
xend = num(str(last))
xl = x0  # label anchor (empty left margin)

# sessions (today, NY time -> UTC): Asia 00-04, London KZ 06-09, NY AM KZ 11-14, NY PM 17:30-20
for a, b, lab, col in [("2026-10-14 00:00", "2026-10-14 04:00", "Asia", "#607d8b"), ("2026-10-14 06:00", "2026-10-14 09:00", "London KZ", "#8e24aa"),
                       ("2026-10-14 11:00", "2026-10-14 14:00", "NY AM KZ", "#fb8c00"), ("2026-10-14 17:30", "2026-10-14 20:00", "NY PM (next window)", "#1e88e5")]:
    ax.axvspan(num(a), num(b), color=col, alpha=0.06, zorder=0)
    ax.text(num(a), 4213.5, lab, fontsize=8, color=col, va="top")

# PD arrays
box(ax, num("2026-10-14 12:30"), x1, 4107.69, 4144.67, DN, None)
box(ax, num("2026-10-14 12:00"), x1, 4107.37, 4136.02, "#b71c1c", None, alpha=0.10, hatch="//")
ax.text(num("2026-10-14 14:35"), 4109.5, "1h FVG 4107.4-4136.0 (CE 4121.7)\n15m FVG 4107.7-4144.7 (CE 4126.2)", color="#b71c1c", fontsize=7.5, va="top")
box(ax, num("2026-10-14 12:15"), x1, 4144.67, 4155.84, "#6a1b9a", None)
ax.text(num("2026-10-14 14:35"), 4156.3, "15m bearish OB 4144.7-4155.8", color="#6a1b9a", fontsize=7.5, va="bottom")
box(ax, num("2026-10-14 12:35"), x1, 4111.05, 4113.46, DN, None, alpha=0.35)
box(ax, num("2026-10-14 13:50"), x1, 4095.46, 4098.27, DN, None, alpha=0.35)
# plan zones
box(ax, num("2026-10-14 14:30"), x1, 4046, 4067, UP, None, alpha=0.22)
ax.text(num("2026-10-14 14:40"), 4046.5, "BUY PLAN (counter-trend):\nsweep < 4066.5 + 5m/15m bullish MSS\n-> entry at new FVG / OB\nSL $3-5 under the sweep low\nTP 4100 / 4118 / 4142", color="#1b5e20", fontsize=7.5, va="bottom")
box(ax, num("2026-10-14 14:30"), x1, 4118, 4136, DN, None, alpha=0.28)
ax.text(num("2026-10-14 14:40"), 4136.5, "SELL PLAN (pro-trend): retrace 4118-4136\n+ 5m bearish MSS | SL > 4145\nTP 4080 / 4066 / 4000", color="#b71c1c", fontsize=7.5, va="bottom")

# levels (labels anchored in the empty left margin)
hline(ax, 4200.625, "PDH 4200.6", "#555", x_text=xl)
hline(ax, 4170.49, "Today/Asia high 4170.5", "#607d8b", x_text=xl)
hline(ax, 4147.0, "PDL 4147.0", "#555", x_text=xl, va="top")
hline(ax, 4141.97, "Daily EQ 4142.0", "#ff9800", "-.", 1.2, x_text=xl, va="top")
hline(ax, 4110.87, "Sep low 4110.9 (swept)", "#9e9e9e", ":", 1.0, x_text=xl)
hline(ax, 4100, "4100", "#9e9e9e", ":", 1.0, x_text=xl, va="top")
hline(ax, 4107.37, "MSS trigger 4107.4", "#1b5e20", "--", 1.0, x_text=xl, va="bottom")
hline(ax, 4086.72, "5m HL 4086.7", "#1b5e20", ":", 0.9, x_text=xl, va="top")
hline(ax, 4079.73, "Today low 4079.7 = Aug-3 daily OB top", "#c62828", "-", 1.2, x_text=xl, va="top")
hline(ax, 4066.535, "PWL / Oct-7 low 4066.5 = SSL", "#c62828", "-", 1.6, x_text=xl, va="bottom")
hline(ax, 4049.0, "Daily OB mean threshold 4049", "#2e7d32", "-.", 1.0, x_text=xl, va="bottom")
ax.annotate(f"now {price:.1f}", xy=(xend, price), xytext=(xend + 0.02, price + 6), fontsize=9, color="black", arrowprops=dict(arrowstyle="->", color="black"), zorder=7)
ax.annotate("CPI 3.7%/core 2.6% (hot)\n12:30 UTC displacement", xy=(num("2026-10-14 12:30"), 4150), xytext=(num("2026-10-13 15:00"), 4190), fontsize=8, color="#b71c1c", arrowprops=dict(arrowstyle="->", color="#b71c1c"))

ax.set_title(f"XAUUSD 15m (OANDA via TradingView) - ICT map   |   last bar {stamp}", fontsize=11, loc="left")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M", tz="UTC"))
ax.grid(alpha=0.15)
ax.set_ylabel("USD / oz")

# volume profile (spot tick volume, month-to-date)
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
axv.set_title("Vol. profile Oct 1-14\n(OANDA tick vol)", fontsize=9)
axv.tick_params(labelleft=False)
axv.set_xticks([])
axv.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_15m_ict_map.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------- chart 2: daily HTF
d = xd[xd.index >= "2026-06-01"]
fig, ax = plt.subplots(figsize=(16, 8), dpi=130)
candles(ax, d, 24 * 60)
x0, x1 = num(str(d.index[0])), num(str(d.index[-1] + pd.Timedelta(days=9)))
ax.set_xlim(x0, x1)
ax.set_ylim(3880, 4760)
# base + breakout
box(ax, num("2026-06-10"), num("2026-08-05"), 3942, 4166, "#9e9e9e", "Jun-Aug accumulation base 3942-4166", alpha=0.12)
box(ax, num("2026-08-03"), x1, 4019.24, 4079.2, UP, "Aug-3 daily bullish OB 4019-4079 (origin of Aug rally)  MT 4049", alpha=0.15)
box(ax, num("2026-10-07"), x1, 4066.535, 4217.395, "#ff9800", None, alpha=0.08)
hline(ax, 4217.395, "Oct-12 high 4217.4 (range high / LH)", "#555")
hline(ax, 4141.97, "EQ 4142", "#ff9800", "-.")
hline(ax, 4066.535, "Oct-7 low 4066.5 (range low / PWL)", "#c62828", "-", 1.4)
hline(ax, 4000, "4000 psych", "#9e9e9e", ":")
hline(ax, 3942.1, "Jun-30 low 3942 / Jul-17 3960 = deeper SSL", "#c62828", ":")
for t, p, lab in [("2026-08-25", 4697.105, "4697"), ("2026-09-03", 4510.93, "LH 4511"), ("2026-09-18", 4399.67, "LH 4400"), ("2026-10-02", 4227.53, "LH 4228"), ("2026-10-12", 4217.395, "LH 4217")]:
    ax.annotate(lab, xy=(num(t), p), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color="#b71c1c")
for t, p, lab in [("2026-09-02", 4282.625, "4283"), ("2026-09-16", 4235.165, "HL 4235"), ("2026-09-28", 4110.87, "LL 4111"), ("2026-10-07", 4066.535, "LL 4066.5")]:
    ax.annotate(lab, xy=(num(t), p), xytext=(0, -12), textcoords="offset points", ha="center", fontsize=8, color="#1b5e20")
ax.annotate(f"now {price:.0f}", xy=(num(str(d.index[-1])), price), xytext=(25, -30), textcoords="offset points", fontsize=9, arrowprops=dict(arrowstyle="->"))
ax.set_title(f"XAUUSD Daily (OANDA) - HTF structure: lower highs + lower lows since Aug-25 top 4697; price back at the top of the summer base   |   {stamp}", fontsize=10, loc="left")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_daily_htf.png", bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------------------- chart 3: 5m NY session + COMEX volume
s5 = x5[x5.index >= "2026-10-14 10:30"]
v5 = g5[g5.index >= "2026-10-14 10:30"]
avg = float(g5[(g5.index >= "2026-10-09") & (g5.index < "2026-10-14")]["volume"].mean())
fig = plt.figure(figsize=(16, 9), dpi=130)
gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.05)
ax = fig.add_subplot(gs[0, 0])
axb = fig.add_subplot(gs[1, 0], sharex=ax)
candles(ax, s5, 5)
x0, x1 = num(str(s5.index[0])), num(str(last + pd.Timedelta(minutes=70)))
ax.set_xlim(x0, x1)
ax.set_ylim(4070, 4162)
box(ax, num("2026-10-14 12:30"), x1, 4118.34, 4149.49, DN, "5m bearish FVG 4118.3-4149.5 (CE 4133.9)")
box(ax, num("2026-10-14 12:35"), x1, 4111.05, 4113.46, DN, "5m FVG 4111.1-4113.5", alpha=0.3)
box(ax, num("2026-10-14 12:40"), x1, 4105.6, 4107.88, DN, None, alpha=0.3)
box(ax, num("2026-10-14 13:50"), x1, 4095.46, 4098.27, DN, "5m FVG 4095.5-4098.3", alpha=0.3)
box(ax, num("2026-10-14 12:25"), x1, 4149.49, 4155.84, "#6a1b9a", "5m bearish OB 4149.5-4155.8")
hline(ax, 4141.97, "Daily EQ 4142", "#ff9800", "-.")
hline(ax, 4136.02, "1h FVG top 4136.0", "#b71c1c", ":")
hline(ax, 4121.7, "1h FVG CE 4121.7", "#b71c1c", ":")
hline(ax, 4107.37, "13:35 high 4107.4 = bullish MSS trigger (5m close above)", "#1b5e20", "--", 1.2, va="top")
hline(ax, 4100, "4100", "#9e9e9e", ":")
hline(ax, 4086.72, "14:00 higher low 4086.7", "#1b5e20", ":")
hline(ax, 4079.73, "13:20 session low 4079.7", "#c62828", "-", 1.2)
ax.annotate(f"now {price:.1f}", xy=(num(str(last)), price), xytext=(20, 15), textcoords="offset points", fontsize=9, arrowprops=dict(arrowstyle="->"))
ax.set_title(f"XAUUSD 5m - NY session micro-structure + COMEX GC1! real volume   |   {stamp}", fontsize=10, loc="left")
ax.tick_params(labelbottom=False)
ax.grid(alpha=0.15)
cols = [UP if r.close >= r.open else DN for _, r in v5.iterrows()]
axb.bar([mdates.date2num(t.tz_convert(None)) for t in v5.index], v5.volume.values, width=5 / (24 * 60) * 0.8, color=cols)
axb.axhline(avg, color="#555", ls="--", lw=0.8)
axb.text(x0, avg, f" 3-day avg 5m vol = {avg:.0f}", fontsize=8, va="bottom", color="#555")
for t, txt in [("2026-10-14 12:30", "CPI candle 21x avg"), ("2026-10-14 12:40", "17x"), ("2026-10-14 13:00", "11x"), ("2026-10-14 13:20", "low on 2.9x\n(sellers thinning)"), ("2026-10-14 13:30", "bounce 10x"), ("2026-10-14 13:55", "pullback 3-4x")]:
    v = float(v5.loc[pd.Timestamp(t, tz="UTC"), "volume"]) if pd.Timestamp(t, tz="UTC") in v5.index else 0
    axb.annotate(txt, xy=(num(t), v), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7.5)
axb.set_ylabel("COMEX contracts / 5m")
axb.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz="UTC"))
axb.grid(alpha=0.15)
fig.savefig(OUT / "xauusd_5m_ny_session_volume.png", bbox_inches="tight")
plt.close(fig)
print("charts written:", sorted(p.name for p in OUT.glob("*.png")))
