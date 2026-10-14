# -*- coding: utf-8 -*-
"""AUDITORIA ESTRITA: testa CADA LINHA CLICAVEL, uma a uma, contra o que o
clique abre. A auditoria antiga somava a categoria na arvore inteira e por isso
nao via categoria espalhada em mais de uma posicao -- o bug do Prestadores."""
import json,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
SEM=set(["Intercompany não casado","Juros Pagos*","Multas Pagas*","Descontos Obtidos*"])
def carrega(arq):
    s=open(arq,encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return json.loads(s[j:k+1])
def audita(D):
    ruim=[];tot=0
    for e in ("amana","topazio","consol"):
        ent=D["entities"][e]
        for m in sorted((ent.get("dre") or {}).keys()):
            det={c:R2(sum(x["v"] for x in it)) for c,it in ((ent.get("tx") or {}).get(m) or {}).items()}
            for t,gs in (ent["dre"][m] or {}).items():
                for g,cos in gs.items():
                    for co,itens in cos.items():
                        pc=collections.defaultdict(float)
                        for x in itens: pc[x["cat"]]+=x["v"]
                        for c,v in pc.items():
                            if abs(R2(v))<0.005 or c in SEM: continue
                            tot+=1
                            if abs(R2(v)-det.get(c,0))>0.004: ruim.append(["DRE",e,m,t,g,co,c,R2(v),det.get(c,0)])
        for m in sorted((ent.get("dfc") or {}).keys()):
            det={c:R2(sum(x["v"] for x in it)) for c,it in ((ent.get("txp") or {}).get(m) or {}).items()}
            for sec in ("receitas","despesas"):
                for g,gd in ((ent["dfc"][m] or {}).get(sec) or {}).items():
                    for c,cd in gd["cats"].items():
                        if abs(R2(cd["total"]))<0.005 or c in SEM: continue
                        tot+=1
                        if abs(R2(cd["total"])-det.get(c,0))>0.004: ruim.append(["CAIXA",e,m,sec,g,"",c,R2(cd["total"]),det.get(c,0)])
    return tot,ruim
if __name__=="__main__":
    arq=sys.argv[1] if len(sys.argv)>1 else "/Users/joaoandrade/painel-amanatopazio/index.html"
    tot,ruim=audita(carrega(arq))
    f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
    print("linhas clicaveis testadas uma a uma: %d"%tot)
    print("linhas que mostram um valor e abrem outro: %d"%len(ruim))
    for r in ruim[:40]:
        print("   %-5s %-8s %-5s %-44s %-30s linha %12s detalhe %12s"%(r[0],r[1],r[2],(r[3]+"/"+r[4]+"/"+r[5])[:44],r[6][:30],f(r[7]),f(r[8])))
    if len(ruim)>40: print("   ... e mais %d"%(len(ruim)-40))
    sys.exit(1 if ruim else 0)
