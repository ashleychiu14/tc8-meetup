import datetime as dt, math, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from data import RAW_2025, RAW_2026

def parse(raw, year):
    out=[]
    for line in raw.strip().splitlines():
        line=line.strip()
        if not line: continue
        d,v=line.split()
        m,day=d.split('/')
        out.append([dt.date(year,int(m),int(day)), float(v), 'raw'])
    return out

s = parse(RAW_2025,2025)+parse(RAW_2026,2026)

FIXES=[]
def fix(i,newdate,newval,why):
    old=(s[i][0],s[i][1]); s[i][0]=newdate; s[i][1]=newval; s[i][2]='fixed'
    FIXES.append((old,(newdate,newval),why))

for i,(d,v,_) in enumerate(s):
    if d==dt.date(2025,4,14) and v==47383: fix(i,dt.date(2025,5,14),47383,"順序錯置：夾在5/12與5/28之間，4/14應為5/14")
    if d==dt.date(2025,5,28) and v==477755: fix(i,d,47755,"多打一位數 477755 -> 47755")
    if d==dt.date(2025,6,10) and v==487818: fix(i,d,48781,"多打一位數 487818 -> 48781（也可能是48718，見敏感度）")
seen={}
for i,(d,v,_) in enumerate(s):
    if d in seen and d==dt.date(2026,5,6):
        fix(i,dt.date(2026,5,7),v,"2026/05/06 出現兩次，第二筆視為 05/07")
    seen[d]=1
s.sort(key=lambda x:x[0])

dates=[x[0] for x in s]; vals=[x[1] for x in s]
n=len(s)
print("=== 資料清理 ===")
for a,b,w in FIXES: print(f"  {a[0]} {a[1]:.0f}  ->  {b[0]} {b[1]:.0f}   ({w})")
print(f"\n=== 基本 ===")
print(f"筆數 {n}；區間 {dates[0]} ~ {dates[-1]}")
span=(dates[-1]-dates[0]).days
print(f"日曆天 {span} 天 = {span/365.25:.2f} 年")
print(f"起 {vals[0]:.0f} -> 迄 {vals[-1]:.0f}   總報酬 {(vals[-1]/vals[0]-1)*100:+.2f}%")
cagr=(vals[-1]/vals[0])**(365.25/span)-1
print(f"CAGR {cagr*100:+.2f}%")

# 取樣間隔
gaps=[(dates[i+1]-dates[i]).days for i in range(n-1)]
gaps_sorted=sorted(gaps)
print(f"\n=== 取樣密度 ===")
print(f"間隔天數 中位數 {gaps_sorted[len(gaps)//2]}  平均 {sum(gaps)/len(gaps):.1f}  最大 {max(gaps)}")
print("最大缺口 top5:")
idx=sorted(range(n-1), key=lambda i:-gaps[i])[:5]
for i in idx:
    print(f"  {dates[i]} -> {dates[i+1]}   {gaps[i]:>3}天   {vals[i]:.0f} -> {vals[i+1]:.0f}  ({(vals[i+1]/vals[i]-1)*100:+.2f}%)")
# 每月筆數
from collections import Counter
c=Counter((d.year,d.month) for d in dates)
print("\n每月觀測筆數:")
y=None
for (yy,mm) in sorted(c):
    print(f"  {yy}-{mm:02d}: {c[(yy,mm)]:>2}", end="")
    if mm%6==0: print()
print()

# 回撤（以觀測點為準）
print("\n=== 回撤（基於觀測點，實際低點可能更深）===")
peak=vals[0]; peak_d=dates[0]; dd=[]
cur=None
for d,v,_ in s:
    if v>=peak:
        if cur: dd.append(cur); cur=None
        peak=v; peak_d=d
    else:
        r=v/peak-1
        if cur is None or r<cur['mdd']:
            cur={'peak_d':peak_d,'peak':peak,'trough_d':d,'trough':v,'mdd':r,'rec_d':None}
        elif cur: pass
if cur: dd.append(cur)
# 重算：完整 peak-to-trough-to-recovery
def drawdowns(dates,vals,thresh=0.05):
    res=[];peak=vals[0];pd_=dates[0];tr=vals[0];td=dates[0];inn=False
    for d,v in zip(dates,vals):
        if v>peak:
            if inn and (tr/peak-1)<=-thresh:
                res.append((pd_,peak,td,tr,tr/peak-1,d,(d-pd_).days,(td-pd_).days,(d-td).days))
            peak=v;pd_=d;tr=v;td=d;inn=False
        else:
            if v<tr: tr=v;td=d
            inn=True
    if inn and (tr/peak-1)<=-thresh:
        res.append((pd_,peak,td,tr,tr/peak-1,None,None,(td-pd_).days,None))
    return res
for r in drawdowns(dates,vals,0.05):
    pd_,pk,td,tr,mdd,rd,tot,decl,rec=r
    rs=f"{rd} (共{tot}天, 跌{decl}天/回{rec}天)" if rd else "尚未回到高點"
    print(f"  高 {pd_} {pk:.0f}  -> 低 {td} {tr:.0f}   {mdd*100:6.2f}%   收復 {rs}")

# 波動度（用對數報酬 / sqrt(天數) 標準化）
import statistics
lr=[]
for i in range(n-1):
    g=(dates[i+1]-dates[i]).days
    lr.append((math.log(vals[i+1]/vals[i])/math.sqrt(g), g))
sd=statistics.pstdev([x[0] for x in lr])
print(f"\n=== 波動度 ===")
print(f"以 sqrt(日曆天) 標準化後的日波動 {sd*100:.3f}% -> 年化 ~{sd*math.sqrt(365.25)*100:.1f}%")
# 分年
for yr in (2025,2026):
    sub=[(d,v) for d,v,_ in s if d.year==yr]
    dd2=[x[0] for x in sub]; vv=[x[1] for x in sub]
    l=[math.log(vv[i+1]/vv[i])/math.sqrt((dd2[i+1]-dd2[i]).days) for i in range(len(sub)-1)]
    print(f"  {yr}: n={len(sub)}  期間報酬 {(vv[-1]/vv[0]-1)*100:+.2f}%  年化波動 ~{statistics.pstdev(l)*math.sqrt(365.25)*100:.1f}%")

# 分段（依主要轉折）
print("\n=== 分段（各制度/regime）===")
segs=[("熊市段 2025 高點->低點", dt.date(2025,2,21), dt.date(2025,4,7)),
      ("V轉修復 2025",           dt.date(2025,4,7),  dt.date(2025,8,12)),
      ("盲區(無資料)",            dt.date(2025,8,12), dt.date(2025,11,3)),
      ("盤整/下行 2025Q4-2026Q1", dt.date(2025,11,3), dt.date(2026,3,30)),
      ("主升段 2026",            dt.date(2026,3,30), dt.date(2026,6,19)),
      ("2026 夏季震盪",           dt.date(2026,6,19), dt.date(2026,8,19))]
m={d:v for d,v,_ in s}
for name,a,b in segs:
    va,vb=m[a],m[b]; days=(b-a).days
    ann=((vb/va)**(365.25/days)-1)*100
    print(f"  {name:26s} {a}->{b}  {days:>3}天  {(vb/va-1)*100:+7.2f}%  年化 {ann:+8.1f}%")

# 月報酬（用最接近月底的觀測點）
print("\n=== 月末近似報酬（以每月最後一筆觀測）===")
last={}
for d,v,_ in s: last[(d.year,d.month)]=(d,v)
keys=sorted(last)
prev=None; mr=[]
for k in keys:
    d,v=last[k]
    if prev: mr.append((k,(v/prev[1]-1)*100,(d-prev[0]).days))
    prev=(d,v)
for k,r,g in mr: print(f"  {k[0]}-{k[1]:02d}: {r:+7.2f}%  (間隔{g}天)")
pos=sum(1 for _,r,_ in mr if r>0)
print(f"  月勝率 {pos}/{len(mr)} = {pos/len(mr)*100:.0f}%")

# 敏感度: 6/10 48781 vs 48718
print("\n=== 敏感度：2025/6/10 = 48781 或 48718 ===")
print("  只影響該點，對總報酬/CAGR/最大回撤皆無影響（該點非峰非谷）。")
