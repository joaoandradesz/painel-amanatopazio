# -*- coding: utf-8 -*-
"""Duas arrumacoes pedidas pelo Joao em 21/10/2026, em todos os meses:

1. "Aluguel de veiculos" (Topazio) sai de 21. Custos / 05. Pessoal indireto da
   operacao e vai para 21. Custos / 01. Arrendamento -- e arrendamento da
   autorizacao de veiculo, nao pessoal. No Omie a categoria 2.04.84 passou a ter
   o mesmo codigo_dre do Arrendamento - Pousada (1.21.02). EBITDA nao muda:
   as duas posicoes caem em cfix.
2. "Agencia de MKT" (Amana) passa a se chamar "Marketing", o nome que a Topazio
   ja usa no mesmo lugar -- no consolidado as duas viram uma linha so, que era o
   objetivo: menos uma linha em despesas comerciais. No Omie a categoria 2.02.02
   da Amana foi renomeada.

Nenhum total muda; o que muda e onde a linha aparece e como ela se chama.
   GRAVA=1 python3 arruma_arvore.py"""
import json,os,collections
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f")
PAINEL=os.path.expanduser("~/painel-amanatopazio/")
MOVE=[] if __import__("os").environ.get("SO_RENOMEIA") else [("topazio","Aluguel de veículos",("1. Lucro Bruto","21. Custos","05. Pessoal indireto da operação"),
                                       ("1. Lucro Bruto","21. Custos","01. Arrendamento"),
                                       "2.1 Pessoal indireto da operação","2.1 Arrendamento"),
      ("consol","Aluguel de veículos",("1. Lucro Bruto","21. Custos","05. Pessoal indireto da operação"),
                                      ("1. Lucro Bruto","21. Custos","01. Arrendamento"),
                                      "2.1 Pessoal indireto da operação","2.1 Arrendamento")]
RENOMEIA=[("amana","Agencia de MKT","Marketing"),("consol","Agencia de MKT","Marketing"),
 # 21/10: a "Taxa de Permanencia" da Amana e o mesmo ISS de permanencia da ilha que a
 # Topazio chama de "ISS | Permanencia" -- mesmas observacoes, mesmo orgao, e ja estava
 # no mesmo no da arvore. Mesmo nome nas duas => uma linha so no consolidado.
 ("amana","Taxa de Permanência","ISS | Permanência"),("consol","Taxa de Permanência","ISS | Permanência")]
def carrega(p):
    s=open(p,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])
def tot_dre(ent,m):
    return R2(sum(x["v"] for t,gs in ((ent.get("dre") or {}).get(m) or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l))
def tot_dfc(ent,m):
    md=(ent.get("dfc") or {}).get(m) or {}
    return R2(sum(cd["total"] for sec in ("receitas","despesas") for gd in (md.get(sec) or {}).values() for cd in gd["cats"].values()))
s,j0,j1,D=carrega(PAINEL+"index.html")
antes={(e,m):(tot_dre(D["entities"][e],m),tot_dfc(D["entities"][e],m))
       for e in ("amana","topazio","consol") for m in set(list((D["entities"][e].get("dre") or {}))+list((D["entities"][e].get("dfc") or {})))}

for e,cat,de,para,gde,gpara in MOVE:
    ent=D["entities"][e]; nd=nc=0
    for m,T in (ent.get("dre") or {}).items():
        no=(((T.get(de[0]) or {}).get(de[1])) or {}).get(de[2])
        if not no: continue
        fica=[x for x in no if x["cat"]!=cat]; vai=[x for x in no if x["cat"]==cat]
        if not vai: continue
        T[de[0]][de[1]][de[2]]=fica
        if not fica: del T[de[0]][de[1]][de[2]]
        dst=T.setdefault(para[0],{}).setdefault(para[1],{}).setdefault(para[2],[])
        for x in vai:
            ex=next((y for y in dst if y["cat"]==x["cat"]),None)
            if ex: ex["v"]=R2(ex["v"]+x["v"])
            else: dst.append({"cat":x["cat"],"v":R2(x["v"])})
        T[para[0]][para[1]][para[2]]=sorted(dst,key=lambda x:-abs(x["v"])); nd+=1
    for m,md in (ent.get("dfc") or {}).items():
        g=(md.get("despesas") or {}).get(gde)
        if not g or cat not in g["cats"]: continue
        v=g["cats"].pop(cat)
        g["total"]=R2(sum(c["total"] for c in g["cats"].values()))
        if not g["cats"]: del md["despesas"][gde]
        d=md["despesas"].setdefault(gpara,{"total":0.0,"cats":{}})
        d["cats"][cat]={"total":R2((d["cats"].get(cat) or {}).get("total",0)+v["total"])}
        d["total"]=R2(sum(c["total"] for c in d["cats"].values())); nc+=1
    print("  %-8s %-22s %s -> %s | DRE %d meses, caixa %d meses"%(e,cat,de[2][:28],para[2],nd,nc))

for e,velho,novo in RENOMEIA:
    ent=D["entities"][e]; nd=nc=0
    for m,T in (ent.get("dre") or {}).items():
        for t,gs in T.items():
            for g,cos in gs.items():
                for co,l in cos.items():
                    if not any(x["cat"]==velho for x in l): continue
                    agg=collections.OrderedDict()
                    for x in l:
                        k=novo if x["cat"]==velho else x["cat"]
                        agg[k]=R2(agg.get(k,0)+x["v"])
                    cos[co]=sorted([{"cat":k,"v":v} for k,v in agg.items() if abs(v)>0.004],key=lambda x:-abs(x["v"])); nd+=1
        tx=(ent.get("tx") or {}).get(m) or {}
        if velho in tx:
            tx[novo]=sorted(tx.pop(velho)+(tx.get(novo) or []),key=lambda x:(x.get("d","")[3:],x.get("d","")[:2]))
    for m,md in (ent.get("dfc") or {}).items():
        for sec in ("receitas","despesas"):
            for g,gd in (md.get(sec) or {}).items():
                if velho not in gd["cats"]: continue
                v=gd["cats"].pop(velho)
                gd["cats"][novo]={"total":R2((gd["cats"].get(novo) or {}).get("total",0)+v["total"])}
                gd["total"]=R2(sum(c["total"] for c in gd["cats"].values())); nc+=1
        tp=(ent.get("txp") or {}).get(m) or {}
        if velho in tp:
            tp[novo]=sorted(tp.pop(velho)+(tp.get(novo) or []),key=lambda x:(x.get("d","")[3:],x.get("d","")[:2]))
    print("  %-8s %-22s -> %-22s | DRE %d nos, caixa %d grupos"%(e,velho,novo,nd,nc))

ruim=[]
for (e,m),(a,b) in antes.items():
    if abs(tot_dre(D["entities"][e],m)-a)>0.004: ruim.append(("DRE",e,m,a,tot_dre(D["entities"][e],m)))
    if abs(tot_dfc(D["entities"][e],m)-b)>0.004: ruim.append(("caixa",e,m,b,tot_dfc(D["entities"][e],m)))
for r in ruim: print("  TOTAL MUDOU:",r)
assert not ruim, "nenhuma das duas arrumacoes pode mexer em total"
print("  nenhum total mudou")
if os.environ.get("GRAVA"):
    blob=json.dumps(D,ensure_ascii=False)
    for arq in ("index.html","socios.html"):
        t,a,b,_=carrega(PAINEL+arq)
        open(PAINEL+arq,"w",encoding="utf-8").write(t[:a]+blob+t[b:]); print("  gravado",arq)
else: print("  (nada gravado -- rode com GRAVA=1)")
