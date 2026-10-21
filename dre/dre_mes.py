# -*- coding: utf-8 -*-
"""Monta a arvore de DRE de um mes de 2026 a partir de dre_base_<emp>.json
   (titulos pela data de emissao + lancamentos avulsos de conta corrente),
   com os caminhos de arvore que jan-jul deixaram no painel.
   MES=8 python3 dre_mes.py          -> so mostra
   MES=8 GRAVA=1 python3 dre_mes.py  -> grava dre_mes_8.json"""
import json,os,sys,unicodedata,collections
sys.path.insert(0,'.')
from dre_map import painel,cats,caminhos
MES=os.environ["MES"]; MM="%02d/2026"%int(MES)
R2=lambda v: round((v or 0)+0.0,2)
def ch(c):
    c=unicodedata.normalize("NFKD",c or "").encode("ascii","ignore").decode().lower()
    for a,b in (("(inativa)",""),("&","e"),("*",""),(" ","")): c=c.replace(a,b)
    return c.strip()
P,_,_,_=painel()
OUT={}; DET={}
for emp in ("amana","topazio"):
    C=cats(emp); lab=json.load(open(f"drelab_{emp}.json"))
    cam=caminhos(P,emp); nomePainel={ch(n):n for n in cam}; camCh={ch(n):p for n,p in cam.items()}
    B=json.load(open(f"dre_base_{emp}.json"))
    agg=collections.defaultdict(float); det=collections.defaultdict(list)
    for t in B["titulos"]:
        if (t["emi"] or "")[3:]!=MM: continue
        for cod,val in t["cats"]:
            v=R2(val*t["sinal"])
            if not v or not cod: continue
            agg[cod]=R2(agg[cod]+v); det[cod].append({"d":t["emi"][:5],"p":t["obs"][:70],"nf":str(t["cod"]),"v":v,"b":"título"})
    for a in B["avulsos"]:
        if (a["data"] or "")[3:]!=MM: continue
        agg[a["cat"]]=R2(agg[a["cat"]]+a["v"]); det[a["cat"]].append({"d":a["data"][:5],"p":(a["cli"] or a["obs"])[:70],"nf":"","v":a["v"],"b":a["conta"]})
    arv={}; tot=0.0; fora=[]; txp={}
    for cod,v in sorted(agg.items()):
        c=C.get(cod)
        if c is None: fora.append(("categoria fora do cadastro",cod,v)); continue
        if not c["dre"]: fora.append(("conta de controle (sem DRE no Omie)",cod,c["desc"],v)); continue
        k=ch(c["desc"]); nome=nomePainel.get(k,c["desc"]); p=camCh.get(k)
        if p is None:
            d=c["dre"].split("."); g1=lab["lab1"].get(d[0]); g2=lab["lab2"].get(".".join(d[:2]))
            if not g1 or not g2: fora.append(("sem caminho",cod,c["desc"],v)); continue
            p=(g1,g2,f'{d[-1]}. {c["ddre"]}')
        g1,g2,g3=p
        arv.setdefault(g1,{}).setdefault(g2,{}).setdefault(g3,[]).append({"cat":nome,"v":v})
        txp[nome]=sorted(det[cod],key=lambda x:x["d"]); tot=R2(tot+v)
    for g1 in arv:
        for g2 in arv[g1]:
            for g3 in arv[g1][g2]: arv[g1][g2][g3]=sorted(arv[g1][g2][g3],key=lambda x:-abs(x["v"]))
    OUT[emp]={"tree":arv,"tot":tot,"txp":txp}
    print(f'== {emp}: resultado {tot:,.2f} | {len(txp)} categorias')
    for f in fora: print("   fora da DRE:",f[0],f[1:])
if os.environ.get("GRAVA"): json.dump(OUT,open(f"dre_mes_{MES}.json","w"),ensure_ascii=False); print("gravado dre_mes_%s.json"%MES)
