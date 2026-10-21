# -*- coding: utf-8 -*-
"""Conserta a consolidacao de agosto na DRE. Eu havia sufixado TODAS as categorias
   com (Amana)/(Topazio); a convencao publicada (jan a jul) sufixa so as linhas de
   RECEITA e soma as despesas numa linha unica por categoria. Era isso que fazia o
   Booking (Comissoes Externas/Parceiros) aparecer duas vezes no total do ano."""
import json,sys
R2=lambda v: round((v or 0)+0.0,2)
M8=json.load(open("dre_mes_8.json"))
IC="Compra de Diarias a Topazio"                     # repasse: eliminado no consolidado
COM_SUFIXO=("01. Receita Bruta de Vendas","01. Outras Receitas")
suf={"amana":" (Amana)","topazio":" (Topázio)"}
arv={}; txc={}
for emp in ("amana","topazio"):
    for g1,d1 in M8[emp]["tree"].items():
        for g2,d2 in d1.items():
            for g3,lst in d2.items():
                for it in lst:
                    if emp=="amana" and it["cat"]==IC: continue
                    nome=it["cat"]+suf[emp] if g3 in COM_SUFIXO else it["cat"]
                    no=arv.setdefault(g1,{}).setdefault(g2,{}).setdefault(g3,{})
                    no[nome]=R2(no.get(nome,0)+it["v"])
                    if it["cat"] in M8[emp]["txp"]: txc.setdefault(nome,[]).extend(M8[emp]["txp"][it["cat"]])
for g1 in arv:
    for g2 in arv[g1]:
        for g3 in arv[g1][g2]:
            arv[g1][g2][g3]=sorted([{"cat":k,"v":v} for k,v in arv[g1][g2][g3].items()],key=lambda x:-abs(x["v"]))
for k in txc: txc[k]=sorted(txc[k],key=lambda x:x["d"])
for ALVO in sys.argv[1:]:
    s=open(ALVO,encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: end=k+1;break
    D=json.loads(s[j:end])
    antes=sum(1 for g1,d1 in D["entities"]["consol"]["dre"]["8"].items() for g2,d2 in d1.items() for g3,l in d2.items() for x in l)
    D["entities"]["consol"]["dre"]["8"]=arv; D["entities"]["consol"]["tx"]["8"]=txc
    dep2=sum(1 for g1,d1 in arv.items() for g2,d2 in d1.items() for g3,l in d2.items() for x in l)
    tot=R2(sum(x["v"] for g1,d1 in arv.items() for g2,d2 in d1.items() for g3,l in d2.items() for x in l))
    open(ALVO,"w",encoding="utf-8").write(s[:j]+json.dumps(D,ensure_ascii=False)+s[end:])
    print(f'{ALVO.split("/")[-1]}: consol agosto {antes} -> {dep2} categorias | resultado {tot:,.2f}')
