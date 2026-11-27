# -*- coding: utf-8 -*-
"""Tiago, 27/11/2026: "Aluguel de veículos" da Topazio sai do grupo Arrendamento (que fica
   so com o arrendamento da pousada) e vira sublinha de Custos diversos, em todos os meses
   (Topazio e consolidado, acumulados inclusive). So posicao: os dois nos ficam em
   "21. Custos", acima do lucro bruto -- nenhum total muda. Idempotente.
   PAINEL=<dir> python3 move_veiculo_custos_diversos.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
CAT,DE,PARA="Aluguel de veículos",("1. Lucro Bruto","21. Custos","01. Arrendamento"),("1. Lucro Bruto","21. Custos","14. Custos diversos")
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); n=0
    for e in ("topazio","consol"):
        for m,T in (D["entities"][e].get("dre") or {}).items():
            no=T.get(DE[0],{}).get(DE[1],{}).get(DE[2])
            if not no: continue
            sai=[x for x in no if x["cat"]==CAT]
            if not sai: continue
            no[:]=[x for x in no if x["cat"]!=CAT]
            if not no: del T[DE[0]][DE[1]][DE[2]]
            dst=T.setdefault(PARA[0],{}).setdefault(PARA[1],{}).setdefault(PARA[2],[])
            for x in sai:
                ex=next((y for y in dst if y["cat"]==CAT),None)
                if ex: ex["v"]=round(ex["v"]+x["v"],2)
                else: dst.append(x)
            dst.sort(key=lambda x:-abs(x["v"])); n+=1
    open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
    print(arq,"nos movidos:",n)
