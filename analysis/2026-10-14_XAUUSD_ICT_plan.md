# XAUUSD (Gold) — ICT + Volume Profile Intraday Plan
**Date:** 2026-10-14 (Wed) · **Data:** TradingView `OANDA:XAUUSD` (price) + `COMEX:GC1!` (real volume), last bar **14:15 UTC = 10:15 NY = 20:15 BST** · **Style:** Intraday (15m–1H entry)
**Verdict:** HTF bearish, price mid-displacement, SSL below untouched → **NO BUY right now.** Buy only after the 4,066.5 sweep + MSS (plan A) or an early 4,107.4 reclaim with volume (plan B, smaller size).

Charts: `analysis/out/xauusd_15m_ict_map.png` · `analysis/out/xauusd_5m_ny_session_volume.png` · `analysis/out/xauusd_daily_htf.png`
Re-run: trigger the *Fetch gold market data* workflow → `git pull` → `python scripts/ict_analysis.py && python scripts/plot_charts.py`

---

## 1. Context
| Item | Value |
|---|---|
| Spot (14:15 UTC) | **4,091.5** · day O 4,161.08 / H 4,170.49 (03:15 UTC, Asia) / L **4,079.73** (13:20 UTC = 09:20 NY) · −1.67 % |
| News | US CPI (Sep) 12:30 UTC: headline 3.7 % y/y (exp 3.6), 0.6 % m/m · core 2.6 % (exp 2.5), 0.3 % m/m (exp 0.2) → **hot** |
| Rates / USD | Dec Fed hike ≈ 90 % priced · 2Y > 4.81 % · DXY ≈ 102 (near 18-month high) |
| Next events | Beige Book 18:00 UTC (00:00 BST) · **PPI + Retail Sales Thu 12:30 UTC (18:30 BST)** · Middle-East / oil headlines |

## 2. HTF structure (Daily / 4H / 1H) — all bearish
* Daily lower highs **4,399.67 (Sep 18) → 4,227.53 (Oct 2) → 4,217.40 (Oct 12)**; lower lows **4,235.17 → 4,110.87 (Sep 28) → 4,066.54 (Oct 7)**. Price below 50/100/200-day SMAs.
* Dealing range **4,066.54 – 4,217.40**, EQ **4,141.97**. Price sits at 16.6 % of the range (deep discount). OTE retracement levels 62/70.5/79 % = 4,123.9 / 4,111.0 / **4,098.2** → price is already *below* the 79 % level ⇒ the "buy the OTE" idea for this range has failed ⇒ probability of a run on the range low rises.
* 1H: bearish MSS at 08:00 UTC (close < 4,144.46), then the CPI displacement.
* Today the drop swept: Sep low / PML **4,110.87**, 1H equal lows 4,112.5 and 4,124–4,125 (Oct 2/5), yesterday's low 4,147.0.
* Price is back at the **top of the Jun–Aug base (3,942–4,166)**. The **Aug-3 daily bullish OB 4,019.2–4,079.2** (origin of the August rally) — today's low 4,079.73 tapped its top exactly; mean threshold **4,049**.

## 3. Key levels (spot)
| Level | Price | Role |
|---|---|---|
| PDH | 4,200.63 | BSL |
| Today / Asia high | 4,170.49 | BSL |
| 15m bearish OB (12:15 UTC candle) | **4,144.67 – 4,155.84** (MT 4,150.25) | unmitigated — top of sell zone |
| PDL | 4,147.0 | — |
| Daily EQ | **4,141.97** | broke down after CPI; reclaim = CPI move negated |
| 15m bearish FVG | **4,107.69 – 4,144.67** (CE 4,126.18) | untouched |
| 1H bearish FVG | **4,107.37 – 4,136.02** (CE 4,121.70) | untouched |
| 5m bearish FVGs | 4,118.34–4,149.49 (CE 4,133.9) · 4,111.05–4,113.46 · 4,095.46–4,098.27 | retrace magnets |
| Sep low (PML) | 4,110.87 | swept |
| **LTF bullish MSS trigger** | **4,107.37** (13:35 UTC high) | 5m/15m close above = first bullish shift |
| 4,100 | 4,100 | psych |
| 5m higher low | 4,086.72 (14:00 UTC) | micro support |
| **Today's low** | **4,079.73** | 5m close below = continuation |
| **PWL / Oct-7 low / range low** | **4,066.54** | **SSL #1 — draw on liquidity** |
| Daily OB mean threshold | 4,049 | sweep target zone 4,049–4,066 |
| Daily OB low | 4,019.2 | deeper HTF demand |
| Big figure / summer lows | 4,000 · 3,996 (Jul 29) · 3,960 (Jul 17) · 3,942 (Jun 30) | SSL #2 |

## 4. Volume status
**COMEX GC1! 5m volume (3-day avg ≈ 400 contracts/5m):**
* 12:30 CPI candle **8,611 (21.5×)** → 12:40 **6,854 (17×)** → 13:00 **4,506 (11×)**: three initiative sell legs.
* The actual low 13:15/13:20 printed on **1,512 / 1,178 (3.8× / 2.9×)** → sellers thinning at the low (volume did not confirm the final low).
* 13:30 bounce candle **4,117 (10×)** = responsive buying at 4,080–4,090; the pull-back 13:50–13:55 only 1,373 / 1,661 (3–4×).
* Net: initiative = sellers, responsive buyers present at 4,080–4,090, **no initiative buying through 4,107 yet**. Day volume 127.7k by 10:05 NY vs 100–169k full recent days → heavy, institutional day.
* ICT *volume imbalances*: none in today's drop (bodies overlap) — the imbalances are the FVGs above.

**Volume profile (what the TradingView fixed-range VP shows):**
| Profile | POC | VAH | VAL | HVN | LVN |
|---|---|---|---|---|---|
| Oct 1 → now, OANDA tick vol | **4,163** | 4,192 | **4,132** | 4,135 · 4,141 · 4,163 · 4,185 | **4,099** · 4,201 |
| Oct 1 → now, COMEX real vol (−26 basis) | 4,167 | 4,194 | 4,128 | 4,123 · 4,141 · 4,165 · 4,183 | 4,099 |
| Today only (OANDA) | 4,144.5 | 4,167 | 4,097 | **4,092.5 (new node forming)** | 4,109.5 |

Reading: price is **below the October value area (VAL 4,132)** and sitting under the **LVN 4,099**. A fresh HVN is building at ~4,088–4,093 (a ledge). Acceptance below value + heavy sell volume = the auction is looking lower (4,066 → summer base). Buyers' tell = an impulsive 5m/15m close back above **4,107.4** on ≥ 2× volume (LVN reclaim → rotation to VAL 4,132 / EQ 4,142). Below 4,079 there is essentially no volume node until the summer base (4,020–4,060) → a break travels fast.

## 5. Decision: **do NOT buy now**
1. HTF (D/4H/1H) bearish + bearish news fuel → a buy is counter-trend.
2. Price is inside a displacement leg; the only discount arrays are below (4,049–4,079 daily OB, 4,066.5 SSL).
3. 4,066.54 and 4,000 liquidity untouched; the daily-range OTE has already failed.
4. No 5m/15m bullish MSS (needs close > 4,107.37).

## 6. Buy plans (counter-trend scalp / intraday)
**Plan A — SSL sweep + MSS (preferred, best in NY PM 17:30–20:00 UTC = 23:30–02:00 BST)**
1. Wait for a sweep **below 4,066.54**, ideally into **4,049–4,066** (daily OB mean threshold + pivot S1 4,060).
2. Confirm on 5m/15m: displacement candle closing above the last lower-high made during the sweep, leaving a bullish FVG; sweep bar on high volume, reclaim bar ≥ 2× avg; ideally SMT with silver (silver does not make a new low).
3. Entry: FVG CE or the bullish OB that launched the MSS. SL $3–5 under the sweep low.
4. Targets: TP1 **4,100** (partial, SL→BE) · TP2 **4,118–4,126** (1H/15m FVG CE) · TP3 **4,142** (EQ). Example: entry 4,062 / SL 4,044 / TP1 4,100 (2.1R) / TP2 4,122 (3.3R).
5. Invalidation: 15m close < 4,045 with no reclaim → stand aside; next zone **4,019 (OB low) → 4,000** with the same checklist.

**Plan B — early LVN reclaim (aggressive, half size)**
* 5m close **> 4,107.37** with displacement and ≥ 2× COMEX volume → wait for the retrace into the new 5m FVG (≈ 4,095–4,105) → entry; SL below 4,086.7 (safer: below 4,079.7); TP 4,121.7 / 4,126.2 / 4,136–4,142. Lower probability because the 4,066.5 pool is untouched; skip during NY lunch (16:00–17:30 UTC).

## 7. Pro-trend sell (the A+ ICT setup today)
Retrace into **4,118–4,136** (1H FVG CE 4,121.7 · 15m FVG CE 4,126.2 · 5m FVG CE 4,133.9) → 5m bearish MSS → short, SL above **4,145** (15m FVG top / PDL 4,147) → TP 4,080 / 4,066 / 4,049 / 4,000. Bias flips only on a 15m close above **4,144.67** + reclaim of EQ 4,142.

## 8. Timing (BST = UTC+6)
* 20:30–21:00 BST: 10:00–11:00 NY macro window (we are here).
* 22:00–23:30 BST: NY lunch — no entries.
* **23:30–02:00 BST: NY PM session — best window for Plan A.**
* 00:00 BST: Beige Book. 03:00 BST: daily close — a close < 4,100 (below Sep low 4,110.87) confirms daily continuation.
* Thu 18:30 BST: PPI + Retail Sales — flatten or hard SL before it.

## 9. Risk
≤ 1 % per trade · no entries inside news candles · gold spikes $20–30 on Middle-East headlines · minimum 1:2 RR or skip.
