# -*- coding: utf-8 -*-
"""Orcamento do painel com a versao que o Tiago reenviou em 27/11/2026.
   A unica diferenca para a rev 15.09 carregada e a aliquota de impostos sobre a
   receita: 13% -> 16,5% (linha 95 da aba 'Orcamento DRE 2026 27'), que muda
   Deducoes e EBITDA orcados. Vendas e Marketing (13% de comissao + 13 mil de mkt)
   nao muda. Colunas F..Q = jan..dez/2026.   ORC=<xlsx> [GRAVA=1] python3 orcamento_impostos.py"""
import os,sys,json,openpyxl
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
ws=openpyxl.load_workbook(os.environ["ORC"],data_only=True)["Orçamento DRE 2026 27"]
assert abs(ws["C95"].value-0.165)<1e-9, ws["C95"].value
COLS=[openpyxl.utils.get_column_letter(i) for i in range(6,18)]
ded=[-round(ws[c+"95"].value,2) for c in COLS]; eb=[round(ws[c+"136"].value,2) for c in COLS]
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); o=D.get("orc")
    if not o: print(arq,"sem orcado"); continue
    antes=(sum(o["linhas"]["03. Deduções de Receita"][:10]),sum(o["meta_ebitda"][:10]))
    o["linhas"]["03. Deduções de Receita"]=ded; o["meta_ebitda"]=eb
    o["fonte"]=o["fonte"].split(" · reenviado")[0]+" · reenviado pelo Tiago em 27/11/2026 com impostos de 16,5% da receita"
    print(arq,"jan-out deducoes %.2f -> %.2f | EBITDA orcado %.2f -> %.2f"%(antes[0],sum(ded[:10]),antes[1],sum(eb[:10])))
    if os.environ.get("GRAVA"): open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
