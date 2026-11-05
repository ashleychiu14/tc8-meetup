import datetime as dt,sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
src=open(__import__('os').path.join(__import__('os').path.dirname(__file__),'full.py')).read()
exec(src.split('print(f"筆數')[0])
def zz(D,V,th=0.06):
    piv=[]; hi=lo=V[0]; hd=ld=D[0]; trend=0
    for d,v in zip(D,V):
        if v>hi: hi,hd=v,d
        if v<lo: lo,ld=v,d
        if trend<=0 and v>=lo*(1+th):          # 確認由低點翻多
            if trend==-1: piv.append((ld,lo,'L'))
            trend=1; hi,hd=v,d
        elif trend>=0 and v<=hi*(1-th):        # 確認由高點翻空
            if trend==1: piv.append((hd,hi,'H'))
            trend=-1; lo,ld=v,d
    piv.append((hd if trend==1 else ld, hi if trend==1 else lo,'NOW'))
    return piv,trend
piv,trend=zz(D,V,0.06)
print("=== ZigZag 波段（6% 反轉門檻）===")
prev=None
for d,v,k in piv:
    lbl={'H':'波段高','L':'波段低','NOW':'目前極值'}[k]
    if prev: print(f"  {lbl} {d} {v:>7.0f}   {(v/prev[1]-1)*100:+7.2f}%  歷時{(d-prev[0]).days:>3}天")
    else:    print(f"  {lbl} {d} {v:>7.0f}")
    prev=(d,v)
print(f"\n  目前 ZigZag 趨勢方向：{'多' if trend==1 else '空'}；最新值 {V[-1]:.0f}")
print("\n=== 高點/低點結構 ===")
H=[(d,v) for d,v,k in piv if k=='H']; L=[(d,v) for d,v,k in piv if k=='L']
print("  波段高點序列：", " -> ".join(f"{v:.0f}({d})" for d,v in H))
print("  波段低點序列：", " -> ".join(f"{v:.0f}({d})" for d,v in L))
print("\n=== 關鍵價位（前波低點＝防守位）===")
for d,v in L[-3:]: print(f"   {d} {v:>7.0f}   距今 {(V[-1]/v-1)*100:+.2f}%")
for lv,nm in [(62780,'2026/07/28 前低'),(65393,'2026/06/10 前低'),(60818,'2026/04/17'),(57773,'2026/01/27'),(55667,'2025年底')]:
    print(f"   {nm:18s} {lv:>7.0f}   距今 {(V[-1]/lv-1)*100:+7.2f}%")
