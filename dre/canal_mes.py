# -*- coding: utf-8 -*-
"""Vendas/ocupacao por canal da Pousada Topazio, mes a mes (Tiago, 27/11/2026: com out/26
   selecionado o painel mostrava "set/26"). set/26 = o D.canal que ja estava publicado;
   out/26 = "Relatorio comercial mensal Outubro", pag. 4 ("Vendas por Canal 2026 - Semestre 2",
   coluna out/26, % do faturamento por canal, arredondado). O relatorio nao traz ocupacao por
   canal de out/26 -- fica sem dado e a tela avisa. Idempotente.  PAINEL=<dir> python3 canal_mes.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
OUT={"vendas":{"BOOKING":35,"DIRETA":28,"SITE":14,"EXPEDIA":12,"AZUL":7,"OUTROS":2,"DECOLAR":1,"ORINTER":1}}
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq)
    cm=D.get("canal_mes") or {}
    if "9" not in cm and D.get("canal"): cm["9"]=D["canal"]
    cm["10"]=OUT; D["canal_mes"]=cm
    open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
    print(arq,sorted(cm))
