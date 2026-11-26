# -*- coding: utf-8 -*-
"""Custo intercompany da Amana em set e out/2026 pelas NFS-e da Topazio (Joao, 26/11/2026).

   A receita da Topazio desses meses ja sai da relacao de NFS-e (todas contra a Amana,
   conferidas no Portal Nacional em 26/11: emitidas, nenhuma cancelada). A perna da Amana
   ficava menor porque parte dos pagamentos estava em 2.01.04 Adiantamento, sem DRE.
   Aqui a linha "Compra de Diarias a Topazio" da Amana passa a ser a soma das mesmas notas,
   nota a nota no detalhe -- as duas pontas ficam iguais e Amana + Topazio = consolidado.
   NF 12, 17 e 18 nao tem pagamento que case e seguem no Omie da Amana como adiantamento:
   o detalhe diz isso. O consolidado nao muda (ele ja elimina as duas pontas).
   Idempotente.  PAINEL=<dir> GRAVA=1 python3 ic_amana_pelas_notas.py"""
import os,sys,json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
_src=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"publica_set.py"),encoding="utf-8").read()
g={"__file__":os.path.join(os.path.dirname(os.path.abspath(__file__)),"publica_set.py")}
exec(_src.rsplit("\nmain()",1)[0],g)
kpis,soma_em,ordena,cats_do_mes,carrega,R2=g["kpis"],g["soma_em"],g["ordena"],g["cats_do_mes"],g["carrega"],g["R2"]
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
IC="Compra de Diarias a Topazio"; MESES=("9","10"); ANO="2026"
NO_ADIANT={"12","17","18"}   # sem pagamento que case: no Omie da Amana ainda em 2.01.04

for arq in ("index.html","socios.html"):
    s,a,b,D=carrega(PAINEL+arq); E=D["entities"]; am=E["amana"]
    for m in MESES:
        nfs=[t for k,l in (E["topazio"]["tx"].get(m) or {}).items() for t in l
             if (t.get("p") or "").upper().startswith("AMANA EMPREENDIMENTOS") and t["v"]>0]
        tot=R2(sum(t["v"] for t in nfs))
        A=am["dre"][m]; achou=False
        for t_,gs in A.items():
            for g_,cos in gs.items():
                for co,l in cos.items():
                    for x in l:
                        if x["cat"]==IC: x["v"]=-tot; achou=True
        assert achou, "linha %s nao existe na Amana em %s"%(IC,m)
        am["tx"][m][IC]=[{"d":t["d"],"p":"POUSADA TOPAZIO LTDA"+(" · no Omie da Amana ainda em adiantamento (2.01.04), sem pagamento que case" if t["nf"] in NO_ADIANT else ""),
                          "nf":t["nf"],"v":-t["v"],"b":""} for t in sorted(nfs,key=lambda t:(t["d"][3:],t["d"][:2]))]
        am["dre_result"][m]=R2(sum(x["v"] for t_,gs in A.items() for g_,cos in gs.items() for co,l in cos.items() for x in l))
        r,c=kpis(A); D["resumo"]["amana"][m]=r; am["comp"][m]=c
        print(arq,"amana",m,"custo IC",tot,"EBITDA",r["ebitda"],"res",r["res"])
    m26=[str(x) for x in D["anos"][ANO]["meses"]]; m25=[str(x) for x in D["anos"]["2025"]["meses"]]
    for tot,meses in (("T",m26),("TT",m26+m25)):
        arv={}; txa={}
        for m in meses:
            Am=am["dre"].get(m) or {}; soma_em(arv,Am); Xm=(am.get("tx") or {}).get(m) or {}
            for cat in cats_do_mes(Am):
                if cat in Xm: txa.setdefault(cat,[]).extend(Xm[cat])
        ordena(arv); am["dre"][tot]=arv; am["tx"][tot]=txa
        am["dre_result"][tot]=R2(sum(x["v"] for t_,gs in arv.items() for g_,cos in gs.items() for co,l in cos.items() for x in l))
        rt,ct=kpis(arv); old=D["resumo"]["amana"].get(tot) or {}
        rt["oc"]=old.get("oc"); rt["adr"]=old.get("adr"); D["resumo"]["amana"][tot]=rt; am["comp"][tot]=ct
    for m in MESES:
        sm=R2(D["resumo"]["amana"][m]["ebitda"]+D["resumo"]["topazio"][m]["ebitda"]); cs=D["resumo"]["consol"][m]["ebitda"]
        print("  identidade %s: Amana+Topazio %s | consolidado %s"%(m,sm,cs)); assert abs(sm-cs)<0.01
    if os.environ.get("GRAVA"):
        open(PAINEL+arq,"w",encoding="utf-8").write(s[:a]+json.dumps(D,ensure_ascii=False)+s[b:])
        print("  gravado",arq)
