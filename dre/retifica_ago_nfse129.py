# -*- coding: utf-8 -*-
"""Retificacao de agosto/2026: a NFS-e 129 e a hospedagem sem nota.

   27/10/2026: segurado ate dezembro. 27/11/2026: o Joao mandou aplicar ja
   ("aproveite pra ajustar aqueles 15k"). Acumulados T/TT agora sao refeitos
   a partir dos meses (antes eram somados a mao).


Dois pontos, os dois achados na conferencia contra a relacao de faturamento da
contabilidade, que deixava agosto R$ 15.630,20 abaixo:

 1. NFS-e 129 (Matheus Rocca, R$ 17.155,91) estava com a data da VENDA NO CARTAO
    (10/07) no lugar da data da nota. Corrigida no Omie para 31/08/2026, igual as
    vizinhas 127/130/131/132. Julho nao muda: no painel essa venda estava na perna
    de Adiantamento de Hospedagem, que e conta de controle e fica fora da DRE --
    por isso julho ja batia ao centavo e continua batendo.
 2. R$ 1.525,67 (Aline Affonso, reserva 2082, PIX em 31/08) e hospedagem recebida
    SEM NFS-e emitida. Sai da linha "Receita de Hospedagem" para "Hospedagem sem
    NFS-e", mesma linha de receita bruta no DRE. O dinheiro nao se mexe; o que muda
    e a linha, para que "Receita de Hospedagem" possa ser comparada com a relacao
    da contabilidade sem nota de rodape.

Receita bruta de agosto sobe 17.155,91 (so o item 1). A linha de hospedagem vai de
734.874,60 para 750.504,84 -- a contabilidade diz 750.504,80, e os 4 centavos sao
arredondamento deles nas mesmas 74 notas.

   python3 retifica_ago_nfse129.py            -> mostra o que faria
   GRAVA=1 python3 retifica_ago_nfse129.py    -> grava index.html e socios.html
"""
import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from consolida import carrega
_p=os.path.join(os.path.dirname(os.path.abspath(__file__)),"publica_set.py")
_g={"__file__":_p}; exec(open(_p,encoding="utf-8").read().rsplit("\nmain()",1)[0],_g)
kpis,soma_em,ordena,cats_do_mes=_g["kpis"],_g["soma_em"],_g["ordena"],_g["cats_do_mes"]
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")

NF129=17155.91; SEMNF=1525.67
ITEM129={"d":"31/08","p":"Matheus Rocca","b":"","nf":"129","v":NF129}
HOSP="Receita de Hospedagem"; NOVA="Hospedagem sem NFS-e"
CAM=("1. Lucro Bruto","01. Receita Líquida Operacional","01. Receita Bruta de Vendas")

_,a,b,D=carrega(PAINEL+"index.html")

def linha(e,nome):
    cos=D["entities"][e]["dre"]["8"][CAM[0]][CAM[1]][CAM[2]]
    for x in cos:
        if x["cat"]==nome: return cos,x
    return cos,None

for e,suf in (("amana",""),("consol"," (Amana)")):
    cos,x=linha(e,HOSP+suf)
    assert x is not None, "nao achei a linha de hospedagem em "+e
    assert abs(x["v"]-734874.60)<0.01, "%s: hospedagem de agosto nao e a esperada (%.2f)"%(e,x["v"])
    assert not any(c["cat"]==NOVA+suf for c in cos), e+": a linha nova ja existe"
    x["v"]=R2(x["v"]+NF129-SEMNF)
    cos.append({"cat":NOVA+suf,"v":SEMNF})

    tx=D["entities"][e]["tx"]["8"]
    it=tx[HOSP+suf]
    alvo=[y for y in it if abs(y["v"]-SEMNF)<0.005 and not (y.get("nf") or "").strip()]
    assert len(alvo)==1, "%s: esperava 1 titulo de %.2f sem NFS-e, achei %d"%(e,SEMNF,len(alvo))
    assert not any((y.get("nf") or "")=="129" for y in it), e+": a NFS-e 129 ja esta em agosto"
    it.remove(alvo[0]); it.append(dict(ITEM129))
    tx[NOVA+suf]=[alvo[0]]

    # mes 8 e acumulados refeitos pela mesma regra do publica_set (kpis/soma_em)
    E=D["entities"][e]; A=E["dre"]["8"]; old=D["resumo"][e].get("8") or {}
    r,c=kpis(A,old.get("oc"),old.get("adr")); D["resumo"][e]["8"]=r; E["comp"]["8"]=c; E["dre_result"]["8"]=r["res"]
    m26=[str(x) for x in D["anos"]["2026"]["meses"]]; m25=[str(x) for x in D["anos"]["2025"]["meses"]]
    for T,meses in (("T",m26),("TT",m26+m25)):
        arv={}; txa={}
        for m in meses:
            Am=E["dre"].get(m) or {}; soma_em(arv,Am); Xm=(E.get("tx") or {}).get(m) or {}
            for cat in cats_do_mes(Am):
                if cat in Xm: txa.setdefault(cat,[]).extend(Xm[cat])
        ordena(arv); E["dre"][T]=arv; E["tx"][T]=txa
        old=D["resumo"][e].get(T) or {}; rt,ct=kpis(arv,old.get("oc"),old.get("adr"))
        D["resumo"][e][T]=rt; E["comp"][T]=ct; E["dre_result"][T]=rt["res"]

    cos,x=linha(e,HOSP+suf)
    print("  %-7s hospedagem ago: %14s   nova linha: %10s   rb do mes: %14s"%(
        e,f(x["v"]),f(SEMNF),f(D["resumo"][e]["8"]["rb"])))

assert abs(D["entities"]["amana"]["dre"]["8"][CAM[0]][CAM[1]][CAM[2]][0]["v"]-750504.84)<0.01

if os.environ.get("GRAVA"):
    blob=json.dumps(D,ensure_ascii=False)
    for arq in ("index.html","socios.html"):
        t,a,b,_=carrega(PAINEL+arq)
        open(PAINEL+arq,"w",encoding="utf-8").write(t[:a]+blob+t[b:])
        print("  gravado",arq)
else:
    print("\n  (nada gravado -- rode com GRAVA=1)")
