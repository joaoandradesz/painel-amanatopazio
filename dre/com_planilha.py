# -*- coding: utf-8 -*-
"""Indicadores comerciais da Pousada Topazio (ocupacao, ADR, RevPAR) pelo
   "Relatorio Diario Comercial Topazio.xlsx" (Joao, 26/11/2026).

   Por que a planilha e nao o relatorio comercial mensal: no mensal a ocupacao
   conta as cortesias e o ticket nao (noites pagas), entao RevPAR != ADR x ocupacao
   em TODOS os meses (dif. de 60 a 337 reais). A planilha fecha a identidade com
   15 UHs: RevPAR = receita / (15 x dias), ADR = receita / noites,
   ocupacao = noites / (15 x dias). Ela cobre ago, set e out/26; jan-jul seguem
   o mensal (nao ha outra fonte). Outubro: os demais campos (hospedes, reservas,
   cancelamentos, cortesias, previsao, venda direta) vem do mensal de outubro.
   Idempotente.  PAINEL=<dir> python3 com_planilha.py"""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from consolida import carrega
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
# mes: (ADR, RevPAR, receita de hospedagem) — aba mais recente que traz o mes
PLAN={"8":(1636.00,1386.00,644480.00),"9":(1602.78,1228.79,552958.00),"10":(1647.85,1431.68,665731.00)}
# relatorio comercial mensal de outubro/2026 (pag. 2, 5 e 7): o que a planilha nao tem
UHS,DIAS=15,{"8":31,"9":30,"10":31}
OUT_MENSAL={"hosp":834,"est":4.12,"res":89,"pagas":78,"canc":67,"cort":37,
            "prev":672812.00,"vd":49.52,"txcanc":35.21}
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq)
    for m,(adr,rp,rec) in PLAN.items():
        c=D["com"].setdefault(m,{})
        if m=="10": c.update(OUT_MENSAL)
        n=round(rec/adr)
        c.update({"oc":round(n/(UHS*DIAS[m])*100,2),"tkt":adr,"revpar":rp,"rec":rec,"noites":n})
        for e in ("topazio","consol"):
            r=D["resumo"][e].get(m)
            if r is not None: r["oc"]=c["oc"]; r["adr"]=adr
    D["com_fonte"]=("Relatório Comercial mensal · Pousada Topázio (jan–jul/26 e demais campos) · "
                    "ocupação, ADR e RevPAR de ago–out/26 pelo Relatório Diário Comercial")
    open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
    print(arq,{m:{k:D["com"][m][k] for k in ("oc","tkt","revpar","noites","rec")} for m in PLAN})
