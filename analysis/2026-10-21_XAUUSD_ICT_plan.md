# XAUUSD intraday update — 21 October 2026

## Data and limitations
- Retrieved 2026-10-21 11:56:28 UTC (17:56 Bangladesh) by GitHub Actions run 39595633276; raw CSVs and fetch log are in data/raw.
- TradingView feed through tvDatafeed: OANDA:XAUUSD for price, COMEX:GC1! for exchange volume. This is a retrieved snapshot, not a continuously updating TradingView browser chart.
- Latest spot observation: 4139.650 in the 11:55 UTC 5m bar (incomplete). Last completed 5m close: 4139.295 at 11:50 UTC. Last completed 15m close: 4138.035 in the 11:30 bar. The 11:45 15m bar and 11:00 hourly bar are incomplete and are NOT close confirmations.
- COMEX 5m data ends at 11:45 UTC, lagging spot. Latest common-timestamp futures/spot close basis: +18.05. Profile levels shifted by that basis are approximate; basis varies over time. Spot broker volume is tick activity, not centralized gold traded volume.
- No independently verified news/calendar review in this update. Recheck high-impact releases before entry; volatility, spread and slippage can invalidate a tight stop.

## Direction
Short-term upward recovery toward 4143, then 4149–4155 if resistance is cleared. This is NOT a confirmed higher-timeframe uptrend. Daily/4h remain bearish-leaning, with successively lower highs (4199.08, 4190.42, 4155.57). Do not reuse the October 15 targets as today's base case.

## ICT / structure evidence
- Today's low 4106.345 swept previous-day low 4111.680 and recovered.
- At 10:30 UTC, a completed 15m candle closed 4128.515 above local swing high 4125.925: bullish short-term structure shift.
- Recovery subsequently cleared Asia high 4129.645 and prior evening high 4131.880. Today's observed high: 4141.185.
- Confirmed 15m bullish FVG: 4132.245–4137.040 (11:30 pattern); narrower 5m FVG: 4134.620–4137.040. Deeper 15m bullish FVG: 4121.130–4125.435; recent 15m bullish order block: 4125.435–4128.825.
- Higher-timeframe overhead supply: resampled 4h bearish FVG 4149.550–4161.350; previous-day high 4155.570. First nearby 5m bearish FVG 4142.560–4144.575.
- The automated report's confirmed hourly swings lag the latest breakout; the hourly breakout bar is still incomplete.

## Volume profile / participation
Using COMEX 5m bars from NY midnight (04:00 UTC) through 11:45 UTC; 1-dollar bins, volume uniformly distributed over each bar's high–low range; 70% value area:

| Level | Futures | Approx. spot equivalent |
|---|---:|---:|
| POC | 4139.5 | 4121.45 |
| VAH | 4144.0 | 4125.95 |
| VAL | 4131.0 | 4112.95 |

Price is above approximate session value, consistent with an upward expansion, but also extended from the main traded area. The 11:40 futures 5m bar traded 1622 contracts versus a median 332 over the preceding 299 bars (~4.9x); elevated participation accompanies the advance, not proof of future gains. Monthly profile VAL maps to approximately 4131.95, near shallow pullback support; this is only a futures-basis proxy.

## Conditional BUY setups — no blind limit order
| Plan | Watch zone | Required evidence before buying | Protective stop | Targets |
|---|---|---|---|---|
| A: shallow pullback | 4132–4135 | Price visits zone, then a completed 5m candle closes back above 4135 with a bullish response; reassess if actual fill is above zone | 4127 | 4143, 4149, 4155 |
| B: deeper pullback | 4122–4126 | Zone holds, then completed 5m close back above 4126; reassess actual fill and R:R | 4116 | 4135, 4143, 4150 |

Plan A example at 4134: risk $7/oz, reward $9/$15/$21 = 1.3R/2.1R/3R, BEFORE fees/spread. If confirmation forces entry at 4136, first target is only 0.8R; do not chase or assume the quoted zone remains executable. Prefer >=2R to the intended main target after costs. These are alternative scenarios, not instructions to stack trades or average down.

A completed 15m close below 4129 weakens/cancels the shallow setup before entry; its 4127 protective stop still applies if already filled. Reassess the deeper zone separately, never widen an existing stop to it. Below 4116 the deeper setup is invalid; a 15m close below 4117 suggests risk back toward 4111/4106. Below 4106, next downside references are 4100 and 4091.

No market buy around 4139–4140: too close to initial resistance. If there is no pullback or confirmation, no trade. Above 4155–4161 with sustained 15m closes and a successful retest, reassess for 4167/4171; not today's unconditional target.

## Risk and correction to prior conversation
No measured probabilities support the previously stated 55%/30%/15% scenario weights; they should not be relied on. Similarly, 4145 was not the day's low on October 15; it was a NY-AM local low. Neither old level is an active entry instruction now. Limit loss per trade to a small predefined fraction (e.g. 0.5–1%); broker-specific contract sizing must be checked. Stops can slip. This analysis offers conditional scenarios, not guaranteed direction.

## Reproduction
- `/home/user/.venv/bin/python scripts/ict_analysis.py --out analysis/out`
- `/home/user/.venv/bin/python scripts/plot_gold_20261021.py`
- Dated chart: `analysis/out/2026-10-21_xauusd_15m.png`.
