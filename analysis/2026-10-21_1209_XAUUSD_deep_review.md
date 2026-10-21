# XAUUSD — deep ICT/SMC + actual COMEX contract volume

## Decision, in plain Bengali
**স্বল্পমেয়াদে উপরের দিকে ঝোঁক; বড় চার্টে এখনো নিচের চাপ।** প্রথম পথ 4143.57 → 4149.55 → 4155.57. Do not interpret this as a guaranteed sequence or a confirmed daily reversal.

**New conditional reference entries:** BUY 4134.50 / SL 4128.00; SELL 4154.00 / SL 4163.00 only after an upside sweep and bearish confirmation. These are proposed future entries, not orders already filled and not current bid/ask quotes.

## 1. Snapshot / source quality
- Fetch pipeline: GitHub Actions run 39597299187, raw snapshot retrieved **2026-10-21 12:09:28 UTC / 18:09:28 Bangladesh**.
- Latest OANDA:XAUUSD 5m observation: **4139.945**, in the incomplete 12:05 bar. Last completed 5m bar: 12:00, close 4139.050. Last completed 15m bar: 11:45, close 4139.930. Last completed hourly bar: 11:00, close 4139.930.
- Actual exchange-volume proxy: TradingView COMEX:GC1! OHLCV, in contracts, not OANDA tick activity. The latest futures bar starts **11:55 UTC**, ends 12:00; retrieval is 9m28s after that end. This is delayed futures data, not a real-time execution feed. Exchange entitlement/latency is not independently verified.
- Yahoo GC=F cross-check for 11:40: close 4156.8999, volume 1633 versus TradingView 4156.9 / 1622. Vendor counts differ slightly; use a single feed consistently, do not add them.
- Spot gold is OTC: no single consolidated global spot volume. No footprint, bid/ask delta, order book, open interest, or participant-identity data are available. Candle colour does NOT prove buyer-initiated/seller-initiated volume or institutional accumulation.
- All structure/FVG confirmations below use completed bars. Daily current session is excluded from completed-day claims. For 4h use native OANDA bars (opens 01/05/09/13/17/21 UTC here), not a midnight-UTC hourly resample.
- This update does not independently verify macro news or an economic calendar. Check high-impact events before placing orders.

## 2. Top-down ICT/SMC structure
| Timeframe | Observation | Interpretation |
|---|---|---|
| Daily | Successive recent daily rally highs 4199.08 → 4190.42 → 4155.57; Oct 19 and 20 closed lower | Broad bearish pressure, no confirmed daily reversal |
| Native 4h | Prior low 4111.68 was breached by today's 4106.345; overhead bearish FVG 4149.55–4158.81, CE 4154.18 | Recovery may run into supply; structural downtrend risk remains |
| 1h | Completed 11:00 bar closed 4139.93, above 4129.645 and 4131.88 | Internal bullish shift; not a break above 4155.57 external high |
| 15m | 10:30 bar closed 4128.515 above swing 4125.925; 11:30 closed 4138.035 | Upward displacement and local structure shift |
| 5m | Higher highs/lows on the recovery; recent support low 4125.260 | Prefer pullback/reclaim buys over chasing price near supply |

The automated confirmed-swing label can still show bearish-leaning on 1h/15m because a symmetric pivot requires future right-side bars. Interpret the completed breakout candle alongside the lagging pivot label, not as a guaranteed trend flip. Order-block candidates are heuristic, not proof of actual institutional positions.

## 3. Liquidity, dealing range and PD arrays
- Previous-day high **4155.570**, low **4111.680**, close **4125.465**.
- Today's observed low **4106.345** traded below PDL and recovered (a price-based sell-side liquidity sweep interpretation).
- At 10:15 UTC, **4111.855** swept the more recent 4117.660 local low and recovered, but stayed ABOVE London low 4110.815 and PDL 4111.680. This was not a second sweep of either lower reference.
- Asia high **4129.645** and prior evening high **4131.880** have already been exceeded; next overhead pools/references **4141.985**, **4143.57**, **4149.55**, **4155.57**, **4158.81**, then **4167.31–4169.70**.
- Native 4h bearish FVG **4149.55–4158.81** (CE **4154.18**); 1h bearish FVG **4155.44–4158.81**; 15m bearish FVG **4155.27–4158.66**. Confluence supports a conditional rejection-sell watch near 4154–4157, not a blind sell.
- First nearby 5m bearish FVG **4142.56–4144.57**, CE **4143.57**: initial profit-taking/resistance area.
- 15m bullish FVG **4132.24–4137.04**, CE **4134.64**; nested 5m bullish FVG **4134.62–4137.04**.
- 15m bullish order-block candidate **4125.44–4128.82**, mean **4127.13**; deeper bullish FVG **4121.13–4125.44**. These are support references, not instructions to average down.
- Current impulse 4111.855 → 4141.985: midpoint **4126.92**, 62–79% pullback/OTE **4118.18–4123.30** (70.5%: 4120.74). A 4134.5 buy is a shallow-FVG continuation trade, NOT an OTE/discount buy. Distinguish them.

## 4. Actual volume evidence
Completed COMEX bars 11:00–11:55 UTC:

| Date | Contracts | Bars |
|---|---:|---:|
| Oct 16 | 2977 | 12 |
| Oct 19 | 3385 | 12 |
| Oct 20 | 4845 | 12 |
| **Oct 21** | **8638** | **12** |

Today's matched-hour participation is **2.31×** the prior three full trading-day windows' mean (3735.67). Sunday has no matching 11:00 session and is excluded, not counted as zero.

The 11:40 5m advance traded **1622 contracts**, **4.89×** the preceding 300 bars' median 332 (3.30× mean 491.65). The evidence supports increased participation in the recovery. It does not establish net aggressive buying or guarantee follow-through.

## 5. Volume Profile — actual volume, estimated distribution
Profile window: **NY midnight (04:00 UTC) to the latest 11:55 bar**, 5m COMEX candles, $1 bins, 70% value area. This is a NY-calendar-day profile, **not** the full CME session starting the prior evening. Each candle's volume is spread uniformly across its range. Without tick trades, this is NOT exact exchange volume-at-price.

| Reference | Futures | Approx. spot equivalent |
|---|---:|---:|
| POC | 4139.50 | **4120.43** |
| VAH | 4146.00 | **4126.93** |
| VAL | 4131.00 | **4111.93** |

Latest common timestamp (11:55) futures-minus-spot basis: **19.07**. Subtracting it translates the futures profile to approximate spot levels. Over the latest 12 common bars, basis ranged **18.245–19.07**, so decimal precision in the calculation is not execution precision. The spot equivalent may be off by $1 or more and by more over longer historical windows.

Spot is above approximate VAH: consistent with upward expansion from value, but extended relative to the high-volume area. The combination of a return below 4125 and failed reclaim would weaken continuation.

## 6. Exact reference levels and executable conditions
**All prices below are spot XAUUSD USD/oz, not futures prices.** Actual broker spread and fill change R:R. No blind market/limit order based solely on touching a level.

### A — preferred direction: continuation BUY
- Watch **4132.24–4137.04**, with planned reference entry **4134.50**.
- Trigger: pull back into the zone, form a bullish response, then a **completed 5m close above 4135**. Only then consider a subsequent retest around **4134.50**. If no retest/fill, no trade. Skip if a renewed bearish 5m structure break invalidates the response.
- Stop **4128.00**. Never widen it to the deeper FVG after entry.
- Targets **4143.50 → 4149.50 → 4154.50**.
- At the reference fill, risk $6.50/oz and gross R:R **1.38R / 2.31R / 3.08R**. T1 alone is not 2R; prefer the setup only if the intended main target remains realistic after costs. If entry becomes 4137, main target 4149.5 is only 1.39R: do not chase.
- A completed 15m close below **4129** cancels the shallow setup before entry. An active stop still applies immediately if already in a trade.

### B — conditional SELL after a sweep into supply
- Watch **4150–4158.81**; reference entry **4154.00**.
- Require price to trade above **4155.57**, then reject with a **completed 5m close below 4151** and a bearish response/local structure break. Consider **4154.00 only on a later failed retest**. Price merely touching 4154 on the way up is NOT the signal.
- Stop **4163.00**; targets **4143.00 → 4135.00 → 4127.00**.
- Risk $9/oz; gross R:R **1.22R / 2.11R / 3R**. If no retest or actual fill worsens reward/risk, skip.
- A sustained 15m acceptance above **4163** invalidates this resistance-sell thesis; reassess for **4167–4171**, not an automatic breakout buy.

### C — SELL only if recovery fails
- Completed 15m close below **4125.00**, then a failed retest of **4126–4128** with a bearish 5m close below 4126.
- Reference entry **4127.00** only on a subsequent failed retest; stop **4134.00**; targets **4117.00 → 4111.00 → 4106.50**.
- Gross R:R **1.43R / 2.29R / 2.93R**. A fast reversal above 4129 invalidates the pre-entry failed-reclaim signal; stop still protects an existing trade.

These are mutually conditional paths, not simultaneous buy/sell orders or instructions to average losses. If support 4125 breaks, local bullish bias becomes neutral-to-bearish; the deeper 4121–4125 area can still produce a bounce, so require the failed retest before selling into it.

## 7. Bottom line / risk
Base case: **first upward attempt toward 4143–4155 while 4125 support holds; at 4150–4159 reassess for rejection rather than assuming an uninterrupted rally**. A completed break/failed reclaim of 4125 changes the local path toward 4117/4111/4106. There are no calibrated probability estimates.

Risk a small pre-set amount (for example 0.5% of equity, no more than 1% per trade); check broker contract size. Stops can slip. Price quotes are a snapshot, so recheck current broker price, spread, closed candles and the economic calendar before acting. The exact reference numbers are planning levels, not promises that price will reach them.

This addendum supersedes untriggered entry references in the earlier 11:56 note; it is NOT an instruction to change the stop of any existing position.

## Reproduce
`/home/user/.venv/bin/python scripts/deep_gold_review.py`

Artifacts:
- `analysis/out/2026-10-21_1209_deep_review.json`
- `analysis/out/2026-10-21_1209_deep_ict_smc.png`
