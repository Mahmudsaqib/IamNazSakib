"""Native TradingView OANDA monthly -> weekly -> daily, price action only.
Session labels derive from the NY session-open date + one calendar day.
Current month/week/session is excluded from all confirmation calculations.
Run at repository root. Dated annotations are guarded against future snapshots.
"""
from pathlib import Path
import sys
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0,str(Path(__file__).parent))
from ict_analysis import swings, fvgs

ROOT=Path('data/raw'); OUT=Path('analysis/out'); OUT.mkdir(parents=True,exist_ok=True)
now=pd.Timestamp((ROOT/'fetched_at.txt').read_text().strip())
ny=now.tz_convert('America/New_York')
trading_day=(ny.tz_localize(None).normalize()+pd.Timedelta(days=int(ny.hour>=17)))
frames={}; completed={}
result={'retrieved_utc':str(now),'retrieved_bangladesh':str(now.tz_convert('Asia/Dhaka')),'source':'TradingView OANDA:XAUUSD via tvDatafeed; no browser chart interaction; no indicators or volume analysis','current_trading_session':str(trading_day.date()),'timeframes':{}}
for tf in ['1mo','1w','1d']:
    df=pd.read_csv(ROOT/f'tv_xau_{tf}.csv')
    opened=pd.to_datetime(df.pop('datetime'),utc=True)
    sessions=opened.dt.tz_convert('America/New_York').dt.tz_localize(None).dt.normalize()+pd.Timedelta(days=1)
    if tf=='1mo': labels=sessions.dt.to_period('M').dt.start_time; current=trading_day.to_period('M').start_time
    elif tf=='1w': labels=sessions.dt.to_period('W-SUN').dt.start_time;current=trading_day.to_period('W-SUN').start_time
    else: labels=sessions;current=trading_day
    df.index=pd.DatetimeIndex(labels).tz_localize('UTC'); df=df.sort_index()
    closed=df[df.index<pd.Timestamp(current,tz='UTC')]
    frames[tf]=df;completed[tf]=closed
    assert len(df)==len(closed)+1, 'Expect exactly one current period, inspect unexpected feed data'
    result['timeframes'][tf]={'bars':len(df),'last_completed_period':str(closed.index[-1].date()),'current_period':str(df.index[-1].date()),'current_bar_unconfirmed':df.iloc[-1][['open','high','low','close']].to_dict(),'previous_completed_bar':closed.iloc[-1][['open','high','low','close']].to_dict(),'swings_1_each_side':[vars(s) for s in swings(closed,1,1)[-12:]],'swings_2_each_side':[vars(s) for s in swings(closed,2,2)[-12:]],'unfilled_completed_fvgs':[v for v in fvgs(closed,1,1200) if not v['filled']][-14:]}
spot=pd.read_csv(ROOT/'tv_xau_5m.csv').iloc[-1]
result['latest_5m_observation']={'bar_start_utc':spot.datetime,'price':float(spot.close),'complete':bool(pd.Timestamp(spot.datetime,tz='UTC')+pd.Timedelta('5min')<=now)}
if now.strftime('%Y-%m-%d_%H%M')!='2026-10-22_0129':
    (OUT/'topdown_latest_data.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    print('Data report saved; dated conclusions/annotations require a fresh manual review.');sys.exit(0)

# Explicitly chosen dealing ranges, not an automatic assertion that every pivot is major.
ranges={'1mo':(3942.1,5602.225),'1w':(4066.535,4697.105),'1d':(4066.535,4199.08)}
result['assessed_bias']={'monthly':'Bearish intermediate delivery; secular bullish structure not fully invalidated','weekly':'Bearish; August bullish internal recovery reversed in September','daily':'Bearish directional lean inside October consolidation; no close below 4066.535 yet'}
result['dealing_ranges']={k:{'low':lo,'high':hi,'EQ':round((hi+lo)/2,3),'position':'discount' if spot.close<(lo+hi)/2 else 'premium'} for k,(lo,hi) in ranges.items()}
result['confirmed_closes']={
 'monthly_jan_bullish_BOS': {'close':float(completed['1mo'].loc['2026-01-01','close']),'prior_oct25_high':4381.44},
 'monthly_jun_bearish_CHOCH': {'close':float(completed['1mo'].loc['2026-06-01','close']),'march_internal_low':4099.125},
 'weekly_jun22_bearish_continuation':{'close':float(completed['1w'].loc['2026-06-22','close']),'prior_march_low':4099.125},
 'weekly_aug17_internal_bullish_shift':{'close':float(completed['1w'].loc['2026-08-17','close']),'jun15_high':4382.615},
 'weekly_sep28_bearish_shift':{'close':float(completed['1w'].loc['2026-09-28','close']),'sep14_low':4235.165},
 'daily_sep28_bearish_BOS':{'close':float(completed['1d'].loc['2026-09-28','close']),'sep16_low':4235.165}}
(OUT/'2026-10-22_0129_topdown_data.json').write_text(json.dumps(result,indent=2,default=str)+'\n')

fig,axes=plt.subplots(3,1,figsize=(16,16),facecolor='#f5f7fb')
settings=[('1mo','2024-01-01','1M | Bearish intermediate correction; secular bull structure not fully broken',(1900,5750),[(3871.89,3928.685,'#00897b','Bull FVG 3871.89-3928.69 | CE 3900.29'),(3268.12,3439.035,'#00897b','Jul-2025 bullish OB 3268.12-3439.04')],[(5602.225,'Jan ATH / BSL 5602.23'),(5419.66,'Mar LH 5419.66'),(4697.105,'Aug LH 4697.11'),(4510.93,'PMH 4510.93'),(3942.1,'Jun SSL 3942.10')]),('1w','2026-01-01','1W | Bearish; August recovery reversed, current week remains unclosed',(3850,5750),[(4207.485,4244.27,'#bf3346','Bear FVG 4207.49-4244.27 | CE 4225.88'),(3996.055,4120.495,'#00897b','Jul-27 bullish OB 3996.06-4120.50 (mitigated)')],[(4697.105,'Aug LH 4697.11'),(4217.395,'PWH 4217.40'),(4073.545,'PWL 4073.55'),(3942.1,'Major SSL 3942.10')]),('1d','2026-08-17','1D | Bearish lean inside October compression; no new external LL below 4066.54',(3980,4730),[(4185.39,4254.58,'#bf3346','Bear FVG 4185.39-4254.58 | CE 4219.99'),(4254.58,4315.795,'#bf3346','Sep-25 bearish OB 4254.58-4315.80'),(4019.24,4079.185,'#00897b','Aug-03 bullish OB 4019.24-4079.19 (mitigated)')],[(4199.08,'Oct-16 LH 4199.08'),(4142.225,'PDH 4142.23'),(4105.025,'PDL 4105.03'),(4066.535,'External October low 4066.54')])]
for ax,(tf,start,title,ylim,zones,levels) in zip(axes,settings):
    d=frames[tf].loc[start:]
    for i,(t,r) in enumerate(d.iterrows()):
        c='#00897b' if r.close>=r.open else '#d34c58';alpha=.45 if t==d.index[-1] else 1
        ax.vlines(i,r.low,r.high,color=c,lw=1,alpha=alpha)
        ax.add_patch(Rectangle((i-.28,min(r.open,r.close)),.56,max(abs(r.close-r.open),1),color=c,alpha=alpha))
    for lo,hi,c,label in zones:
        ax.axhspan(lo,hi,color=c,alpha=.1)
        ax.text(.01,hi,label,transform=ax.get_yaxis_transform(),va='bottom',fontsize=8,color=c)
    for y,label in levels:
        ax.axhline(y,color='#777777',ls='--',lw=.7)
        ax.text(.99,y,label,transform=ax.get_yaxis_transform(),ha='right',va='bottom',fontsize=8,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
    eq=result['dealing_ranges'][tf]['EQ'];ax.axhline(eq,color='#ed8b23',ls='-.',lw=.8)
    ax.text(.5,eq,f'Selected range EQ {eq:.2f}',transform=ax.get_yaxis_transform(),va='bottom',fontsize=8,color='#ba650c')
    ax.axhline(float(spot.close),color='#202b3f',ls=':',lw=1)
    ticks=list(range(0,len(d),max(1,len(d)//9)));ax.set_xticks(ticks,[d.index[i].strftime('%Y-%m') if tf=='1mo' else d.index[i].strftime('%d %b') for i in ticks])
    ax.set_xlim(-1,len(d)+1);ax.set_ylim(*ylim);ax.set_ylabel('XAUUSD USD/oz');ax.grid(alpha=.1);ax.set_title(title,loc='left',fontsize=12,fontweight='bold',pad=12)
fig.suptitle('XAUUSD | Native TradingView OANDA price action | 22 Oct 2026, 01:29 UTC / 07:29 Bangladesh',fontsize=13,y=.985)
fig.text(.065,.012,'Only closed candles confirm structure. Faded final candle = current/unconfirmed month, week or day. Zones are ICT interpretations, not verified institutional orders. No indicators or volume used.',fontsize=9)
fig.tight_layout(rect=(.02,.03,.99,.965),h_pad=3)
path=OUT/'2026-10-22_0129_topdown_map.png';fig.savefig(path,dpi=150);print(path)
print(json.dumps(result['confirmed_closes'],indent=2))
