"""Closed-candle ICT/SMC review and actual COMEX contract-volume diagnostics.
Run from repository root. Data remain a delayed snapshot, not a live execution feed.
Volume-at-price is estimated from OHLCV; no footprint, bid/ask delta or L2 is available.
"""
from pathlib import Path
import json
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import Rectangle
sys.path.insert(0, str(Path(__file__).parent))
from ict_analysis import load, swings, structure_bias, fvgs, order_blocks, mss, volume_profile

OUT = Path('analysis/out')
OUT.mkdir(exist_ok=True, parents=True)
now = pd.Timestamp(Path('data/raw/fetched_at.txt').read_text().strip())
stamp = now.strftime('%Y-%m-%d_%H%M')
closed = {}
report = {'retrieved_utc': str(now), 'method': 'Closed native-timeframe spot candles; exchange futures contract volume. No bid/ask delta. OHLCV-derived estimated volume profile.'}
for tf, delta in [('5m','5min'), ('15m','15min'), ('1h','1h'), ('4h','4h')]:
    raw = load('tv_xau_'+tf+'.csv')
    d = raw[raw.index + pd.Timedelta(delta) <= now]
    closed[tf] = d
    sw = swings(d,3,3)
    report[tf] = {'latest_observation': {'bar_start': str(raw.index[-1]), 'price': float(raw.close.iloc[-1]), 'complete': bool(raw.index[-1]+pd.Timedelta(delta)<=now)}, 'last_completed_bar': str(d.index[-1]), 'structure': structure_bias(sw), 'swings': [vars(v) for v in sw[-10:]], 'mss': mss(d,sw), 'open_fvgs': [v for v in fvgs(d,.7,300) if not v['filled']][-10:], 'order_block_candidates': order_blocks(d,sw,300)[-6:]}

s = closed['5m']
fraw = load('tv_gc_5m.csv')
f = fraw[fraw.index+pd.Timedelta('5min')<=now]
j = s[['close']].join(f[['close']],rsuffix='_gc').dropna()
b = j.close_gc-j.close
basis = float(b.iloc[-1])
report['volume_source'] = {'symbol': 'COMEX:GC1!', 'units': 'contracts per bar', 'latest_bar_start': str(f.index[-1]), 'latest_bar_end': str(f.index[-1]+pd.Timedelta('5min')), 'feed_gap_minutes_since_latest_bar_end': float((now-f.index[-1]-pd.Timedelta('5min')).total_seconds()/60), 'basis_common_timestamp': str(j.index[-1]), 'latest_futures_minus_spot': basis, 'basis_last_12_range': [float(b.tail(12).min()),float(b.tail(12).max())]}
ny_midnight = now.tz_convert('America/New_York').normalize().tz_convert('UTC')
profiles = {}
for name, df in [('today_ny_midnight_5m', f[f.index>=ny_midnight]), ('prior_ny_day_5m', f[(f.index>=ny_midnight-pd.Timedelta('1D')) & (f.index<ny_midnight)])]:
    vp = volume_profile(df,1)
    profiles[name] = {k:v for k,v in vp.items() if k!='bins'}
    profiles[name]['approx_spot_equivalent'] = {k:round(vp[k]-basis,2) for k in ['POC','VAH','VAL']}
    if name=='today_ny_midnight_5m': current_vp = vp
report['profiles'] = profiles
# Matched UTC hour comparison avoids treating a busy US hour as an ordinary Asia bar.
dates = sorted(set(f.index.strftime('%Y-%m-%d')))
today = now.strftime('%Y-%m-%d')
prior_dates = [day for day in dates if day < today and len(f.loc[day+' 11:00':day+' 11:55']) == 12][-3:]
comparison = {}
for day in prior_dates+[today]:
    d = f.loc[day+' 11:00':day+' 11:55']
    comparison[day] = {'bars': len(d), 'contracts': float(d.volume.sum())}
prior = [v['contracts'] for k,v in comparison.items() if k!=today and v['bars']==12]
ratio = comparison[today]['contracts']/np.mean(prior) if prior and comparison[today]['bars']==12 else None
report['volume_matched_1100_1155_utc'] = {'daily':comparison,'today_vs_prior_3_mean':ratio}
reference = f[f.index<pd.Timestamp(today+' 11:40',tz='UTC')].tail(300).volume
report['volume_1140'] = {'contracts': float(f.loc[today+' 11:40','volume']), 'preceding_300_bar_median': float(reference.median()), 'preceding_300_bar_mean': float(reference.mean())}
# Independent-source sanity check; different vendor counts need not be identical.
y = load('gc_5m_5d.csv')
report['crosscheck_yahoo_1140'] = {'volume':float(y.loc[today+' 11:40','volume']), 'close':float(y.loc[today+' 11:40','close'])}
(OUT / f'{stamp}_deep_review.json').write_text(json.dumps(report,indent=2,default=str)+'\n')

# Dated map: visual annotations intentionally apply to the Oct 21 analysis only.
if stamp != '2026-10-21_1209':
    print('Report written; dated trading annotations skipped for a different snapshot.')
    sys.exit(0)
fig = plt.figure(figsize=(16,10),facecolor='#f5f7fb')
gs = fig.add_gridspec(2,2,width_ratios=[5,1.3],height_ratios=[3,1],hspace=.12,wspace=.06)
ax = fig.add_subplot(gs[0,0]); av = fig.add_subplot(gs[1,0],sharex=ax); ap=fig.add_subplot(gs[0,1],sharey=ax); info=fig.add_subplot(gs[1,1]); info.axis('off')
d = closed['15m'].loc['2026-10-20 10:00':]
for t,r in d.iterrows():
    x=md.date2num(t);c='#00897b' if r.close>=r.open else '#d34c58'
    ax.vlines(x,r.low,r.high,color=c,lw=.8)
    ax.add_patch(Rectangle((x-.004,min(r.open,r.close)),.008,max(abs(r.close-r.open),.07),color=c))
for lo,hi,c,text in [(4149.55,4158.81,'#bf3346','Native 4H supply 4149.55-4158.81; SELL watch 4154'),(4132.24,4137.04,'#00897b','15m bullish FVG; BUY watch 4134.5'),(4121.13,4125.44,'#1565c0','Deeper 15m FVG 4121.13-4125.44')]:
    ax.axhspan(lo,hi,color=c,alpha=.13)
    ax.text(.012,hi,text,transform=ax.get_yaxis_transform(),fontsize=9,color=c,va='bottom')
for y,text,c in [(4163,'Sell stop 4163','#bf3346'),(4155.57,'PDH 4155.57','#bf3346'),(4143.57,'First resistance 4143.57','#bf3346'),(4139.945,'Latest observed ~4139.95 (not plotted as a closed candle)','#333333'),(4128,'Buy stop 4128','#bf3346'),(4106.345,'Today low 4106.35','#777777')]:
    ax.axhline(y,color=c,ls='--',lw=.8)
    ax.text(.99,y,text,transform=ax.get_yaxis_transform(),ha='right',va='bottom',fontsize=8,color=c,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
ax.set_ylim(4102,4168);ax.set_ylabel('Spot XAUUSD / USD per oz');ax.grid(alpha=.15);ax.tick_params(labelbottom=False)
ax.set_title('XAUUSD | Intraday bullish recovery inside a higher-timeframe bearish structure',loc='left',fontweight='bold',fontsize=13,pad=16)
vol = f.loc[d.index[0]:]
colors=np.where(vol.close>=vol.open,'#00897b','#d34c58')
av.bar(vol.index,vol.volume,width=4/(24*60),color=colors)
av.set_ylabel('Actual COMEX\ncontracts / 5m');av.grid(alpha=.15)
av.xaxis.set_major_locator(md.AutoDateLocator(minticks=5,maxticks=9));av.xaxis.set_major_formatter(md.DateFormatter('%d %b\n%H:%M'))
av.set_xlabel('UTC | futures feed ends 11:55 bar (bar ended 12:00); snapshot retrieved 12:09')
centers=np.array(current_vp['bins']['centers'])-basis
ap.barh(centers,current_vp['bins']['volume'],height=.85,color='#90a4ae')
for key,c in [('POC','#ef6c00'),('VAH','#1565c0'),('VAL','#1565c0')]:
    y=current_vp[key]-basis;ap.axhline(y,color=c,lw=.9);ap.text(.03,y,f'{key} ~{y:.1f}',transform=ap.get_yaxis_transform(),va='bottom',fontsize=9,color=c)
ap.set_title('Estimated volume profile\nCOMEX -> spot proxy',fontsize=10);ap.set_xlabel('Contracts');ap.tick_params(labelleft=False)
info.text(0,.95,'Actual volume, estimated profile\n\n11:00-11:55 UTC: 8,638 contracts\n2.31x prior 3 matched-hour mean\n\n11:40 bar: 1,622 contracts\n4.89x prior 300-bar median\n\nNo bid/ask delta or footprint.\nNo automatic limit-order entries.',va='top',fontsize=9,linespacing=1.5)
fig.suptitle('21 October 2026 | retrieved 12:09 UTC / 18:09 Bangladesh | conditional levels, not a forecast guarantee',fontsize=11,y=.97)
fig.text(.06,.025,'Profile uses NY-midnight-to-latest futures OHLCV, uniform range allocation, 70% value area. Spot proxy subtracts latest common basis +19.07; not exact traded volume at spot prices.',fontsize=9)
fig.subplots_adjust(left=.06,right=.97,top=.9,bottom=.11)
path=OUT/f'{stamp}_deep_ict_smc.png';fig.savefig(path,dpi=150)
print(path)
print(json.dumps({k:v for k,v in report.items() if k not in closed},indent=2,default=str))
