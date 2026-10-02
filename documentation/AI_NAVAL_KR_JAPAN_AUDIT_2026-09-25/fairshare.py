import json, glob, os, collections
from nava import W, dk, strength
MAJ=["GER","ITA","JAP","ENG","FRA","USA","SOV"]
camps=collections.defaultdict(list)
for p in glob.glob("navjson/*.json"):
    d=json.load(open(p)); camps[d["campaign"][:8]].append(d)
def post(r, prev):
    # hysteresis: enter inf >1.5 exit <1.3 ; enter sup <0.8 exit >0.9
    if prev=="inf": return "inf" if r>=1.3 else ("sup" if r<0.8 else "neu")
    if prev=="sup": return "sup" if r<=0.9 else ("inf" if r>1.5 else "neu")
    return "inf" if r>1.5 else ("sup" if r<0.8 else "neu")
out=[]
for cid,saves in camps.items():
    saves.sort(key=lambda d:dk(d["date"]))
    stats={t:{m:collections.Counter() for m in "GAF"} for t in MAJ}
    timeline={t:[] for t in MAJ}
    prevs={t:{m:None for m in "GAF"} for t in MAJ}
    for d in saves:
        S={t:strength(f,"w") for t,f in d["countries"].items()}
        en=collections.defaultdict(set)
        for a,b in d["wars"]: en[a].add(b); en[b].add(a)
        for t in MAJ:
            if not en[t] or S.get(t,0)==0: continue
            E=en[t]; se=sum(S.get(e,0) for e in E)
            G=se/S[t]
            allies={x for e in E for x in en[e]}  # everyone fighting my enemies (me included)
            A=se/max(1,sum(S.get(x,0) for x in allies))
            F=sum(S.get(e,0)/max(1,sum(S.get(x,0) for x in en[e])) for e in E)
            row={}
            for m,r in (("G",G),("A",A),("F",F)):
                p=post(r,prevs[t][m]); prevs[t][m]=p; stats[t][m][p]+=1; row[m]=(round(r,2),p)
            timeline[t].append((d["date"].rsplit(".",2)[0],row))
    out.append(f"\n## campaign {cid}\n| tag | G global sup/neu/inf | A alliance | F fair-share | flips F |\n|---|---|---|---|---|")
    for t in MAJ:
        def f(m):
            c=stats[t][m]; n=sum(c.values()) or 1
            return f"{100*c['sup']//n}/{100*c['neu']//n}/{100*c['inf']//n} (n={sum(c.values())})"
        fl=[]; last=None
        for dt,row in timeline[t]:
            p=row["F"][1]
            if p!=last and last is not None: fl.append(f"{dt}:{last}->{p}({row['F'][0]})")
            last=p
        out.append(f"| {t} | {f('G')} | {f('A')} | {f('F')} | {'; '.join(fl) or '-'} |")
    out.append("\nJAP / ENG / USA timeline (every 6th save): date G A F")
    for t in ("JAP","ENG","USA","ITA","GER"):
        tl=timeline[t][::6]
        out.append(t+": "+" | ".join(f"{dt} {row['G'][0]} {row['A'][0]} {row['F'][0]}{row['F'][1][0]}" for dt,row in tl))
open("fairshare_out.md","w").write("\n".join(out)); print("\n".join(out))
