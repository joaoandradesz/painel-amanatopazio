# -*- coding: utf-8 -*-
"""Varredura de TODAS as invariantes do painel, nao so linha x detalhe."""
import json,re,collections,sys
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
def carrega(arq):
    s=open(arq,encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return json.loads(s[j:k+1])
D=carrega(sys.argv[1] if len(sys.argv)>1 else "/Users/joaoandrade/painel-amanatopazio/index.html")
E=("amana","topazio","consol"); M26=[str(x) for x in range(1,9)]; M25=["2508","2509","2510","2511","2512"]
MD=[str(x) for x in range(1,10)]
pr=lambda *a: print("   ",*a)
SEM_CLIQUE=set(["Intercompany não casado","Juros Pagos*","Multas Pagas*","Descontos Obtidos*"])

falhas=collections.Counter()
def chk(nome,ok,msg=""):
    if not ok: falhas[nome]+=1; pr("FALHA",nome,msg)

print("B) arvores acumuladas = soma dos meses")
def arv(ent,m):
    o=collections.defaultdict(float)
    for t,gs in (ent["dre"].get(m) or {}).items():
        for g,cos in gs.items():
            for co,itens in cos.items():
                for x in itens: o[(t,g,co,x["cat"])]+=x["v"]
    return o
for e in E:
    for tot,meses in (("T",M26),("T25",M25),("TT",M26+M25)):
        som=collections.defaultdict(float)
        for m in meses:
            for k,v in arv(D["entities"][e],m).items(): som[k]+=v
        a=arv(D["entities"][e],tot)
        d=[k for k in set(list(a)+list(som)) if abs(R2(a.get(k,0))-R2(som.get(k,0)))>0.004]
        chk("arvore_acum", not d, "%s %s: %d linhas divergem"%(e,tot,len(d)))

print("C) resumo acumulado = soma dos meses")
for e in E:
    for tot,meses in (("T",M26),("T25",M25),("TT",M26+M25)):
        if tot not in D["resumo"][e]: continue
        for k in ("rb","ebitda","res"):
            som=R2(sum(D["resumo"][e][m][k] for m in meses if m in D["resumo"][e]))
            chk("resumo_acum", abs(som-R2(D["resumo"][e][tot][k]))<0.02, "%s %s %s soma %s x %s"%(e,tot,k,f(som),f(D["resumo"][e][tot][k])))

print("D) DFC: grupo = soma das categorias; resultado, saldo e contas fecham")
for e in E:
    for m in sorted(D["entities"][e]["dfc"]):
        md=D["entities"][e]["dfc"][m]; tot=0
        for sec in ("receitas","despesas"):
            for g,gd in (md.get(sec) or {}).items():
                s=R2(sum(cd["total"] for cd in gd["cats"].values())); tot+=s
                chk("grupo", abs(s-R2(gd["total"]))<0.005, "%s %s %s grupo %s x cats %s"%(e,m,g[:20],f(gd["total"]),f(s)))
        chk("resultado", abs(R2(tot)-R2(md.get("resultado")))<0.02, "%s %s resultado %s x cats %s"%(e,m,f(md.get("resultado")),f(tot)))
        si,ac=R2(md.get("saldo_inicial")),R2(md.get("acumulado"))
        chk("saldo", abs(si+R2(md.get("resultado"))-ac)<0.02, "%s %s si %s + res %s != ac %s"%(e,m,f(si),f(md.get("resultado")),f(ac)))
        if isinstance(md.get("contas"),list):
            chk("contas_sf", abs(R2(sum(c["sf"] for c in md["contas"]))-ac)<0.02, "%s %s contas sf %s x acumulado %s"%(e,m,f(sum(c["sf"] for c in md["contas"])),f(ac)))
            chk("contas_si", abs(R2(sum(c["si"] for c in md["contas"]))-si)<0.02 or m.startswith("25"), "%s %s contas si %s x saldo inicial %s"%(e,m,f(sum(c["si"] for c in md["contas"])),f(si)))

print("E) DFC acumulado = soma dos meses")
def cats(ent,m):
    o=collections.defaultdict(float); md=ent["dfc"].get(m) or {}
    for sec in ("receitas","despesas"):
        for g,gd in (md.get(sec) or {}).items():
            for c,cd in gd["cats"].items(): o[(sec,g,c)]+=cd["total"]
    return o
for e in E:
    for tot,meses in (("T",MD),("T25",M25),("TT",MD+M25)):
        som=collections.defaultdict(float)
        for m in meses:
            for k,v in cats(D["entities"][e],m).items(): som[k]+=v
        a=cats(D["entities"][e],tot)
        d=[k for k in set(list(a)+list(som)) if abs(R2(a.get(k,0))-R2(som.get(k,0)))>0.004]
        chk("dfc_acum", not d, "%s %s: %d categorias divergem"%(e,tot,len(d)))

print("F) saldo_contas = contas do DFC")
for e in E:
    for m in sorted(D["saldo_contas"][e].get("banco") or {}):
        a=R2(sum(c["v"] for c in D["saldo_contas"][e]["banco"][m]))
        md=D["entities"][e]["dfc"].get(m) or {}
        if isinstance(md.get("contas"),list):
            b=R2(sum(c["sf"] for c in md["contas"]))
            chk("saldo_contas", abs(a-b)<0.02, "%s %s saldo_contas %s x dfc %s"%(e,m,f(a),f(b)))

print("G) numero clicavel que abre lista vazia")
for e in E:
    for m in sorted(D["entities"][e]["dre"]):
        det=(D["entities"][e]["tx"] or {}).get(m) or {}
        for t,gs in (D["entities"][e]["dre"][m] or {}).items():
            for g,cos in gs.items():
                for co,itens in cos.items():
                    pc=collections.defaultdict(float)
                    for x in itens: pc[x["cat"]]+=x["v"]
                    for c,v in pc.items():
                        if abs(R2(v))>0.005 and not det.get(c) and c not in SEM_CLIQUE:
                            chk("lista_vazia","", "%s %s %s = %s e a lista esta vazia"%(e,m,c[:28],f(v)))
print()
print("RESUMO:",dict(falhas) if falhas else "nenhuma falha")
sys.exit(1 if falhas else 0)
