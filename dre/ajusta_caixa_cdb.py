# -*- coding: utf-8 -*-
"""Leva o caixa de setembro do painel ao extrato do CDB do Bradesco.

O extrato de investimentos de 30/09 diz: renda bruta acumulada 6.159,33 (era
5.302,45 em 31/08) e IRRF acumulado 1.231,86 -> valor liquido 78.779,08.
O painel tinha 78.811,59, com um "ajuste" de -342,47 que mirava o numero errado.
No Omie lancei o rendimento bruto de setembro (856,88) e o complemento do IR
(889,39); 342,47 + 889,39 = 1.231,86, o IR do extrato. Aqui o caixa do painel
acompanha: a DRE sai do Omie pelo publica_set.py, o DFC e ajustado por este.
   GRAVA=1 python3 ajusta_caixa_cdb.py"""
import json,os,sys
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f")
PAINEL=os.path.expanduser("~/painel-amanatopazio/")
REND=856.88; IRC=-889.39; DELTA=R2(REND+IRC)          # -32,51
ALVO=78779.08
CAT_R="Rendimentos Aplicações"; CAT_I="IR - Aplicação"
NOVO_R={"d":"30/09","p":"Rendimento bruto de setembro do CDB do Bradesco (extrato de investimentos)","b":"Bradesco - CDB DI PJ","nf":"","v":REND}
NOVO_I={"d":"30/09","p":"Complemento do IR retido do CDB do Bradesco (1.231,86 no extrato de 30/09)","b":"Bradesco - CDB DI PJ","nf":"","v":IRC}
def carrega(p):
    s=open(p,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])
def mexe(d,cat,v):
    """soma v na categoria cat do DFC, mantendo o total do grupo"""
    for sec in ("receitas","despesas"):
        for g,gd in (d.get(sec) or {}).items():
            if cat in gd["cats"]:
                gd["cats"][cat]["total"]=R2(gd["cats"][cat]["total"]+v)
                gd["total"]=R2(sum(c["total"] for c in gd["cats"].values()))
                return True
    return False
s,j0,j1,D=carrega(PAINEL+"index.html")
for e in ("amana","consol"):
    pre="Amana · " if e=="consol" else ""
    for m in ("9","T","TT"):
        d=D["entities"][e]["dfc"].get(m)
        if not d: continue
        assert mexe(d,CAT_R,REND), "%s %s sem %s"%(e,m,CAT_R)
        assert mexe(d,CAT_I,IRC), "%s %s sem %s"%(e,m,CAT_I)
        d["resultado"]=R2(d["resultado"]+DELTA); d["acumulado"]=R2(d["saldo_inicial"]+d["resultado"])
        c=next(x for x in d["contas"] if x["n"]==pre+"Bradesco - CDB DI PJ")
        c["sf"]=R2(c["sf"]+DELTA)
        if m=="9": assert abs(c["sf"]-ALVO)<0.005,"conta ficou %s"%f(c["sf"])
        assert abs(R2(sum(x["sf"] for x in d["contas"]))-d["acumulado"])<0.02, "%s %s contas x acumulado"%(e,m)
        tx=D["entities"][e]["txp"][m]
        tx.setdefault(CAT_R,[]).append(dict(NOVO_R)); tx.setdefault(CAT_I,[]).append(dict(NOVO_I))
        b=D["saldo_contas"][e]["banco"].get(m)
        if b:
            sc=next(x for x in b if x["n"]==pre+"Bradesco - CDB DI PJ"); sc["v"]=R2(sc["v"]+DELTA)
        print("  %-8s %-3s resultado %14s | acumulado %14s | CDB %12s"%(e,m,f(d["resultado"]),f(d["acumulado"]),f(c["sf"])))
if os.environ.get("GRAVA"):
    blob=json.dumps(D,ensure_ascii=False)
    for arq in ("index.html","socios.html"):
        t,a,b,_=carrega(PAINEL+arq)
        open(PAINEL+arq,"w",encoding="utf-8").write(t[:a]+blob+t[b:]); print("  gravado",arq)
else: print("  (nada gravado -- rode com GRAVA=1)")
