# -*- coding: utf-8 -*-
"""Estornos/chargebacks da GetNet saem da DRE da Amana (Joao, 27/11/2026).
   Eram devolucao de reserva paga como Adiantamento de Hospedagem (1.04.01, sem nota):
   a origem de cada um casa com o adiantamento recebido. No Omie foram para a 2.01.78
   "Devolucao de adiantamento de hospedagem", sem DRE. Aqui saem da linha "Taxa de
   cartao credito" (Despesas Financeiras, abaixo do EBITDA) na Amana e no consolidado:
   o EBITDA nao muda, o resultado sobe. Agosto: so esta linha (os 15.630,20 seguem segurados).
   Idempotente.  PAINEL=<dir> GRAVA=1 python3 estornos_fora_dre.py"""
import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
_p=os.path.join(os.path.dirname(os.path.abspath(__file__)),"publica_set.py")
g={"__file__":_p}; exec(open(_p,encoding="utf-8").read().rsplit("\nmain()",1)[0],g)
kpis,soma_em,ordena,cats_do_mes,carrega,R2=g["kpis"],g["soma_em"],g["ordena"],g["cats_do_mes"],g["carrega"],g["R2"]
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
CAT="Taxa de cartão crédito"
EST=[("3","23/03",6621.62),("4","30/04",10688.66),("4","30/04",3020.32),("5","04/05",6506.85),
     ("5","20/05",7640.22),("8","10/08",8054.99),("10","15/10",1967.90),("10","22/10",11489.00)]
def tot(A): return R2(sum(x["v"] for t,gs in A.items() for gg,cos in gs.items() for co,l in cos.items() for x in l))
for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); mexeu=set()
    for e in ("amana","consol"):
        E=D["entities"][e]
        for m,d,v in EST:
            l=E["tx"].get(m,{}).get(CAT,[])
            i=next((k for k,t in enumerate(l) if t["d"]==d and abs(t["v"]+v)<0.005 and "GETNET" in (t.get("p") or "").upper()),None)
            if i is None: continue
            l.pop(i)
            for t_,gs in E["dre"][m].items():
                for g_,cos in gs.items():
                    for co,it in cos.items():
                        for x in it:
                            if x["cat"]==CAT: x["v"]=R2(x["v"]+v)
            mexeu.add((e,m))
        for m in sorted({m for ee,m in mexeu if ee==e},key=int):
            A=E["dre"][m]; E["dre_result"][m]=tot(A); old=D["resumo"][e].get(m) or {}
            r,c=kpis(A,old.get("oc"),old.get("adr")); D["resumo"][e][m]=r; E["comp"][m]=c
        if any(ee==e for ee,m in mexeu):
            m26=[str(x) for x in D["anos"]["2026"]["meses"]]; m25=[str(x) for x in D["anos"]["2025"]["meses"]]
            for T,meses in (("T",m26),("TT",m26+m25)):
                arv={}; txa={}
                for m in meses:
                    Am=E["dre"].get(m) or {}; soma_em(arv,Am); Xm=(E.get("tx") or {}).get(m) or {}
                    for cat in cats_do_mes(Am):
                        if cat in Xm: txa.setdefault(cat,[]).extend(Xm[cat])
                ordena(arv); E["dre"][T]=arv; E["tx"][T]=txa; E["dre_result"][T]=tot(arv)
                old=D["resumo"][e].get(T) or {}; rt,ct=kpis(arv,old.get("oc"),old.get("adr")); D["resumo"][e][T]=rt; E["comp"][T]=ct
    for e,m in sorted(mexeu): print(arq,e,m,"res",D["resumo"][e][m]["res"],"ebitda",D["resumo"][e][m]["ebitda"])
    if os.environ.get("GRAVA") and mexeu: open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
