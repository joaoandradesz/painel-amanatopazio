# -*- coding: utf-8 -*-
"""A linha da Amana "Pontuacao e Premiacao" e a conta 2.02.97, que o Omie chama de
   "Variavel" desde out/2026 (Despesas de Vendas e Marketing no DRE do Omie). O Tiago
   (26/11/2026): Variavel substitui a pontuacao, inclusive no passado; o Joao: fica como
   esta no sistema. Renomeia em todos os meses da Amana e separa no consolidado a parte
   da Amana (Variavel) da parte da Topazio (segue "Pontuacao e Premiacao").
   So nome: nenhum valor, nenhuma posicao. Idempotente.  PAINEL=<dir> python3 renomeia_variavel.py"""
import json,os,sys,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
R2=lambda v: round((v or 0)+0.0,2)
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
DE,PARA="Pontuação e Premiação","Variável"
chave=lambda x:(x.get("d"),x.get("p"),x.get("nf"),R2(x.get("v")))
def tira(lst,sai):
    c=collections.Counter(chave(x) for x in sai); fica=[]
    for x in lst:
        k=chave(x)
        if c[k]>0: c[k]-=1
        else: fica.append(x)
    assert sum(c.values())==0, "detalhe da Amana nao encontrado no consolidado"
    return fica
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); E=D["entities"]; n=0
    am,co=E["amana"],E["consol"]
    for m,A in (am.get("dre") or {}).items():          # DRE
        va=0.0
        for t,gs in A.items():
            for g,cos in gs.items():
                for c,l in cos.items():
                    for x in l:
                        if x["cat"]==DE: x["cat"]=PARA; n+=1
                        if x["cat"]==PARA: va+=x["v"]
        txa=(am.get("tx") or {}).get(m) or {}
        if DE in txa: txa[PARA]=txa.pop(DE)
        if not va: continue
        for t,gs in ((co.get("dre") or {}).get(m) or {}).items():
            for g,cos in gs.items():
                for c,l in cos.items():
                    for x in list(l):
                        if x["cat"]!=DE: continue
                        resto=R2(x["v"]-va); x["cat"]=PARA; x["v"]=R2(va)
                        if abs(resto)>0.004: l.append({"cat":DE,"v":resto})
                    l.sort(key=lambda x:-abs(x["v"]))
        txc=(co.get("tx") or {}).get(m) or {}
        if DE in txc:
            txc[DE]=tira(txc[DE],txa.get(PARA) or []); txc[PARA]=list(txa.get(PARA) or [])
            if not txc[DE]: del txc[DE]
    for m,md in (am.get("dfc") or {}).items():          # DFC
        va=0.0
        for sec in ("receitas","despesas"):
            for g,gd in (md.get(sec) or {}).items():
                if DE in gd["cats"]: gd["cats"][PARA]=gd["cats"].pop(DE); n+=1
                if PARA in gd["cats"]: va+=gd["cats"][PARA]["total"]; ga=(sec,g)
        tpa=(am.get("txp") or {}).get(m) or {}
        if DE in tpa: tpa[PARA]=tpa.pop(DE)
        if not va: continue
        sec,g=ga; gc=((co.get("dfc") or {}).get(m) or {}).get(sec,{}).get(g)
        if gc and DE in gc["cats"]:
            resto=R2(gc["cats"][DE]["total"]-va); del gc["cats"][DE]
            gc["cats"][PARA]={"total":R2(va)}
            if abs(resto)>0.004: gc["cats"][DE]={"total":resto}
        tpc=(co.get("txp") or {}).get(m) or {}
        if DE in tpc:
            tpc[DE]=tira(tpc[DE],tpa.get(PARA) or []); tpc[PARA]=list(tpa.get(PARA) or [])
            if not tpc[DE]: del tpc[DE]
    open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
    print(arq,"linhas renomeadas na Amana:",n)
