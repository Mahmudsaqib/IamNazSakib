"""Dated, reproducible map; all annotations apply only to the saved Oct 21 snapshot."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.patches import Rectangle
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from ict_analysis import load, volume_profile

s = load('tv_xau_15m.csv').loc['2026-10-20 10:00':]
f = load('tv_gc_5m.csv')
spot5 = load('tv_xau_5m.csv')
j = spot5[['close']].join(f[['close']], rsuffix='_gc').dropna()
basis = float(j.iloc[-1].close_gc - j.iloc[-1].close)
vp = volume_profile(f.loc['2026-10-21 04:00':], 1)
fig, (ax, av) = plt.subplots(1, 2, figsize=(15, 8), gridspec_kw={'width_ratios': [5, 1]}, sharey=True)
fig.patch.set_facecolor('#f5f7fb')
for t, r in s.iterrows():
    x = md.date2num(t)
    c = '#00897b' if r.close >= r.open else '#d94b56'
    ax.vlines(x, r.low, r.high, color=c, lw=.8)
    ax.add_patch(Rectangle((x-.004, min(r.open,r.close)), .008, max(abs(r.close-r.open),.08), color=c))
for lo, hi, color, text in [(4149.55,4161.35,'#c62828','4H resistance 4149.6-4161.4'),(4132.24,4137.04,'#00897b','15m bullish FVG; watch 4132-4135'),(4121.13,4125.44,'#1565c0','Deeper support / buy watch 4122-4126')]:
    ax.axhspan(lo,hi,color=color,alpha=.12)
    ax.text(.015,hi,text,transform=ax.get_yaxis_transform(),va='bottom',fontsize=9,color=color)
for y, text, color in [(4155.57,'Previous-day high 4155.6','#a12e37'),(4143.57,'First resistance / T1 ~4143','#a12e37'),(4139.65,'Latest observed 4139.65 (bar incomplete)','#333333'),(4127,'Plan A stop 4127','#a12e37'),(4116,'Plan B stop 4116','#a12e37'),(4106.345,'Today low 4106.3','#777777')]:
    ax.axhline(y,color=color,lw=.85,ls='--')
    ax.text(.99,y,text,transform=ax.get_yaxis_transform(),ha='right',va='bottom',fontsize=8,color=color,bbox={'facecolor':'white','edgecolor':'none','alpha':.8})
centers = [v-basis for v in vp['bins']['centers']]
av.barh(centers,vp['bins']['volume'],height=.85,color='#90a4ae')
for k,c in [('POC','#ef6c00'),('VAH','#1565c0'),('VAL','#1565c0')]:
    y=vp[k]-basis
    av.axhline(y,color=c,lw=1)
    av.text(.03,y,f'{k} ~{y:.1f}',transform=av.get_yaxis_transform(),va='bottom',fontsize=8,color=c)
av.set_title('COMEX volume proxy\nNY midnight to 11:45 UTC',fontsize=9)
av.set_xlabel('Volume (contracts)')
ax.set_ylim(4102,4168)
ax.xaxis.set_major_formatter(md.DateFormatter('%d %b\n%H:%M'))
ax.grid(alpha=.15)
ax.set_ylabel('XAUUSD / USD per oz')
ax.set_xlabel('UTC; last 15m bar is incomplete')
ax.set_title('XAUUSD 15m | Short-term recovery; higher-timeframe downtrend risk',loc='left',fontsize=13,fontweight='bold',pad=20)
fig.suptitle('21 Oct 2026 | fetched 11:56 UTC / 17:56 Bangladesh',fontsize=11,y=.965)
fig.text(.06,.025,'Conditional setups only: wait for a 5m recovery close. No guaranteed pullback. Futures profile shifted by latest basis +18.05; approximate, not spot traded volume.',fontsize=9)
fig.subplots_adjust(left=.06,right=.98,top=.87,bottom=.12,wspace=.04)
out=Path('analysis/out/2026-10-21_xauusd_15m.png')
fig.savefig(out,dpi=150)
print(out)
