# -*- coding: utf-8 -*-
"""DFC: a "Variavel" da Amana (2.02.97 renomeada no Omie em out/2026) saiu em
   2.3 Despesas com Pessoal; vai para Vendas e Marketing, a posicao do DRE do
   Omie, com o nome do Omie (Joao, 26/11/2026). Idempotente.
   PAINEL=<dir> python3 dfc_variavel_out26.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
R2=lambda v: round((v or 0)+0.0,2)
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
DE,PARA,G="Variável","Variável","2.3 Despesas de Vendas e Marketing"   # nome do Omie (26/11)
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); n=0
    for e in ("amana","consol"):
        ent=D["entities"][e]
        for m,md in (ent.get("dfc") or {}).items():
            desp=md.get("despesas") or {}
            for g in list(desp):
                if g==G or DE not in desp[g]["cats"]: continue
                v=desp[g]["cats"].pop(DE)["total"]; desp[g]["total"]=R2(desp[g]["total"]-v)
                if not desp[g]["cats"]: del desp[g]
                no=desp.setdefault(G,{"total":0.0,"cats":{}})
                no["cats"].setdefault(PARA,{"total":0.0}); no["cats"][PARA]["total"]=R2(no["cats"][PARA]["total"]+v)
                no["total"]=R2(no["total"]+v); n+=1
            tp=(ent.get("txp") or {}).get(m) or {}
            if DE in tp and DE!=PARA:
                tp[PARA]=sorted((tp.get(PARA) or [])+tp.pop(DE),key=lambda x:(x["d"][3:],x["d"][:2]))
    open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
    print(arq,"linhas movidas:",n)
