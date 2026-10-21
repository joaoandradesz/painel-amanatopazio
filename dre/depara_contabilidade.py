# -*- coding: utf-8 -*-
"""De-para linha a linha: DRE da contabilidade (JC Buarque) x painel, Amana, jan a mar/26.
   A contabilidade fecha pelo razao dela; o painel fecha pela arvore do Omie.
   Aqui cada bloco e comparado e as diferencas de criterio entram numa ponte."""
import json,os
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
PAINEL=os.path.expanduser("~/painel-amanatopazio/index.html")
# --- lado da contabilidade, lido dos tres PDFs
CONT={
 "1":{"rb":529990.86,"imp":-54545.15,"cus":-360428.16,"vendas":-34943.66,
      "adm":{"pessoal":-5298.19,"ocupacao":-6900.00,"utilidades":-55.90,"gerais":-23899.28,"pj":-22676.15},
      "trib":-1235.29,"fin":-11045.31,"res":8963.77},
 "2":{"rb":270043.26,"imp":-34293.99,"cus":-157106.64,"vendas":-57902.45,
      "adm":{"pessoal":-10616.48,"ocupacao":-1000.00,"utilidades":-584.94,"gerais":-25761.90,"pj":-22279.60},
      "trib":-878.43,"fin":-15154.77,"res":-55535.94},
 "3":{"rb":88285.52,"imp":-11794.70,"cus":-283726.88,"vendas":-33916.47,
      "adm":{"pessoal":-12620.26,"ocupacao":-6000.00,"utilidades":-55.90,"gerais":-54812.76,"pj":-17323.93},
      "trib":-822.37,"fin":-11956.71,"res":-344744.46}}
def carrega():
    s=open(PAINEL,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return json.loads(s[j:k+1])
D=carrega()
def linhas(m):
    T=D["entities"]["amana"]["dre"][m]
    out=[]
    for t,gs in T.items():
        for g,cos in gs.items():
            for co,l in cos.items():
                for x in l: out.append((t,g,co,x["cat"],x["v"]))
    return out
def soma(L,**kw):
    r=0
    for t,g,co,cat,v in L:
        if kw.get("co") and co!=kw["co"]: continue
        if kw.get("g") and g!=kw["g"]: continue
        if kw.get("t") and t!=kw["t"]: continue
        if kw.get("cat") and cat not in kw["cat"]: continue
        if kw.get("excat") and cat in kw["excat"]: continue
        r+=v
    return R2(r)
print("DE-PARA — AMANA — DRE da contabilidade (JC Buarque) x painel\n")
for m,nome in (("1","janeiro/26"),("2","fevereiro/26"),("3","março/26")):
    L=linhas(m); c=CONT[m]
    rb=soma(L,co="01. Receita Bruta de Vendas")
    hosp=soma(L,co="01. Receita Bruta de Vendas",cat={"Receita de Hospedagem"})
    outras_rec=R2(rb-hosp)
    ded=soma(L,co="03. Deduções de Receita")
    das=soma(L,co="03. Deduções de Receita",cat={"Simples Nacional (DAS)"})
    outras_ded=R2(ded-das)
    custos=soma(L,g="21. Custos")
    vendas=soma(L,co="04. Despesas de Vendas e Marketing")
    adm=R2(soma(L,co="01. Despesas com Pessoal")+soma(L,co="02. Despesa Indireta de Pessoal Indireto")+soma(L,co="03. Despesas Administrativas"))
    trib=soma(L,co="05. Outros Tributos")
    fin=R2(soma(L,co="02. Receitas Financeiras")+soma(L,co="05. Despesas Financeiras"))
    recup=soma(L,co="02. Recuperação de Despesas Variáveis")
    inv=soma(L,t="3. Investimentos")
    res=R2(sum(v for _,_,_,_,v in L))
    cadm=R2(sum(c["adm"].values()))
    print("="*86); print(nome.upper())
    print("%-42s %14s %14s %13s"%("bloco","painel","contabilidade","diferença"))
    def lin(n,p,q): print("%-42s %14s %14s %13s"%(n,f(p),f(q),f(p-q)))
    lin("Receita bruta",rb,c["rb"])
    print("%-42s %14s %14s"%("   · receita de hospedagem",f(hosp),f(c["rb"])))
    print("%-42s %14s %14s"%("   · serviços extras + frigobar",f(outras_rec),"—"))
    lin("Impostos sobre vendas / deduções",ded,c["imp"])
    if abs(outras_ded)>0.004: print("%-42s %14s %14s"%("   · devoluções de vendas (só no painel)",f(outras_ded),"—"))
    lin("Custos",custos,c["cus"])
    print("%-42s %14s %14s"%("   · compra de diárias (intercompany)","—",f(c["cus"]-0)))
    lin("Despesas de vendas",vendas,c["vendas"])
    lin("Despesas administrativas",adm,cadm)
    lin("Despesas tributárias",trib,c["trib"])
    lin("Resultado financeiro",fin,c["fin"])
    print("%-42s %14s %14s"%("Recuperação de despesas (só no painel)",f(recup),"—"))
    print("%-42s %14s %14s"%("Investimentos (painel põe na DRE)",f(inv),"—"))
    print("-"*86)
    lin("RESULTADO",res,c["res"])
    print()
    print("PONTE do painel para a contabilidade:")
    p=res; print("   %-54s %14s"%("resultado do painel",f(p)))
    p=R2(p+c["cus"]); print("   %-54s %14s  -> %s"%("(−) custo intercompany que a contabilidade lança",f(c["cus"]),f(p)))
    p=R2(p-inv);      print("   %-54s %14s  -> %s"%("(+) investimentos que a contabilidade capitaliza",f(-inv),f(p)))
    p=R2(p-outras_rec);print("   %-54s %14s  -> %s"%("(−) receita que a contabilidade não reconhece",f(-outras_rec),f(p)))
    p=R2(p-outras_ded);print("   %-54s %14s  -> %s"%("(+) deduções só do painel",f(-outras_ded),f(p)))
    print("   %-54s %14s"%("resultado da contabilidade",f(c["res"])))
    print("   %-54s %14s"%("RESÍDUO a explicar",f(c["res"]-p)))
    print()
