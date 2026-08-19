import datetime as dt, math, statistics, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'analyze.py')).read().split("print(\"=== 資料清理")[0])
dates=[x[0] for x in s]; vals=[x[1] for x in s]; n=len(s)

print("=== 報酬集中度 ===")
def seg(a,b):
    m={d:v for d,v,_ in s}; return (m[b]/m[a]-1)*100
print(f"  2025-01-17 -> 2026-03-30 (437天, 佔全期75%): {seg(dt.date(2025,1,17),dt.date(2026,3,30)):+.2f}%")
print(f"  2026-03-30 -> 2026-08-19 (142天, 佔全期25%): {seg(dt.date(2026,3,30),dt.date(2026,8,19)):+.2f}%")
print(f"  2026-03-30 -> 2026-06-19 ( 81天, 佔全期14%): {seg(dt.date(2026,3,30),dt.date(2026,6,19)):+.2f}%")

print("\n=== 水下時間 (time under water) ===")
peak=vals[0]; uw=0; tot=0
for i in range(n-1):
    d=(dates[i+1]-dates[i]).days; tot+=d
    peak=max(peak,vals[i])
    if vals[i]<peak*0.999: uw+=d
print(f"  處於歷史高點以下的日曆天：{uw}/{tot} = {uw/tot*100:.1f}%")
# Ulcer index
peak=vals[0]; sq=0
for v in vals:
    peak=max(peak,v); sq+=((v/peak-1)*100)**2
print(f"  Ulcer Index = {math.sqrt(sq/n):.2f}%   (Martin ratio = CAGR/UI = {23.46/math.sqrt(sq/n):.2f})")

print("\n=== 單筆最大跳動（觀測點之間）===")
mv=sorted([( (vals[i+1]/vals[i]-1)*100, dates[i], dates[i+1], (dates[i+1]-dates[i]).days) for i in range(n-1)], key=lambda x:-abs(x[0]))[:8]
for r,a,b,g in mv: print(f"  {a} -> {b} ({g}天)  {r:+7.2f}%   日均 {r/g:+.2f}%")

print("\n=== 兩年同期對照（n=2，僅供觀察不可視為週期）===")
rows=[("年內高點(2月)","2025-02-21 49144","2026-02-12 58178"),
      ("年內低點","2025-04-07 38351","2026-03-30 51694"),
      ("峰->谷 幅度","-21.96%","-11.15%"),
      ("峰->谷 天數","45天","46天"),
      ("低點->6月中","2025-06-24 49310 (+28.6%)","2026-06-19 71209 (+37.8%)"),
      ("夏季走勢","2025 7-8月 續漲 +6.2%","2026 6/19-8/19 -5.7%")]
for a,b,c in rows: print(f"  {a:14s} | {b:28s} | {c}")

print("\n=== 目前狀態 ===")
hi=max(vals); hid=dates[vals.index(hi)]
print(f"  歷史高點 {hid} {hi:.0f}；現值 {vals[-1]:.0f}，距高點 {(vals[-1]/hi-1)*100:+.2f}%")
print(f"  距 2026 低點(3/30 51694) {(vals[-1]/51694-1)*100:+.2f}%")

print("\n=== 自由度檢查（能不能拿來擬合參數）===")
print(f"  觀測點 136；獨立的漲跌循環（>5%回撤）6 次；完整年度 1 個")
print(f"  以「每個可調參數至少需 10-30 個獨立事件」的經驗法則：可支撐 0 個自由參數")
