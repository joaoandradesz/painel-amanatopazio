# -*- coding: utf-8 -*-
"""Reconstroi dre/dados_rel.json e dre/orc2.json A PARTIR DO PAINEL PUBLICADO.
   O relatorio nao pode ter numero proprio: tudo o que ele mostra sai do
   index.html que esta no ar. Espelha dbucket() da pagina -- se a classificacao
   da arvore mudar lah, muda aqui, e o assert no fim acusa."""
import re,json,os,sys
RAIZ=os.path.expanduser("~/painel-amanatopazio")
s=open(RAIZ+"/index.html",encoding="utf-8").read()
i=s.index("const D=");j=s.index("{",i);dep=0;fim=0
for k in range(j,len(s)):
    if s[k]=="{":dep+=1
    elif s[k]=="}":
        dep-=1
        if dep==0:fim=k+1;break
D=json.loads(s[j:fim])
R2=lambda v: round((v or 0)+0.0,2)

NAOOP=re.compile(r"pagamento indevido|devolu[çc][aã]o de pagamento indevido|^reembolsos?$|^reembolso$|empr[ée]stimos? e financiamentos?|tarifas? banc[áa]ria",re.I)
def dbucket(t,g,c,cat):
    if re.search(r"empr[ée]stimos? e financiamentos?",cat,re.I): return "emprestimo"
    if re.search(r"^aporte|rendimentos aplica",cat,re.I): return "recnaoop"
    if NAOOP.search(cat) or re.search(r"Não operacional",c,re.I): return "naoop"
    if re.search(r"Taxa de cart",cat,re.I): return "deducoes"
    if t.startswith("3."): return "investimentos"
    if re.search(r"Receita Bruta",c,re.I): return "receita"
    if re.search(r"Dedu[çc]",c,re.I) or re.search(r"Outros Tributos",c,re.I): return "deducoes"
    if re.search(r"Receitas Financeiras|Outras Receitas|Recupera[çc]",c,re.I): return "recfin"
    if g.strip().startswith("21"): return "pessoaldir" if re.search(r"Pessoal",c,re.I) else "custos"
    if re.search(r"Financeiras",c,re.I): return "despfin"
    if re.search(r"Vendas e Marketing",c,re.I): return "comercial"
    if re.search(r"Pessoal",c,re.I): return "pessoal"
    return "admin"

def buckets(e,m):
    b={}
    tree=D["entities"][e]["dre"].get(m) or {}
    for t in tree:
        for g in tree[t]:
            for c in tree[t][g]:
                for x in tree[t][g][c]:
                    k=dbucket(t,g,c,x["cat"]); b[k]=b.get(k,0)+x["v"]
    return {k:R2(v) for k,v in b.items()}

def casc(e,m):
    b=buckets(e,m); G=lambda k: R2(b.get(k,0))
    rb,ded=G("receita"),G("deducoes"); rl=R2(rb+ded)
    cus,pdir=G("custos"),G("pessoaldir"); lb=R2(rl+cus+pdir)
    com,adm,pind=G("comercial"),G("admin"),G("pessoal"); eb=R2(lb+com+adm+pind)
    rf=R2(G("recfin")+G("despfin")); ll=R2(eb+rf)
    inv,recnop=G("investimentos"),G("recnaoop"); nop=R2(G("naoop")+G("emprestimo"))
    return dict(rb=rb,ded=ded,rl=rl,cus=cus,pdir=pdir,lb=lb,com=com,adm=adm,pind=pind,
                eb=eb,rf=rf,ll=ll,inv=inv,recnop=recnop,nop=nop,res=R2(ll+inv+recnop+nop))

MESES=[str(m) for m in range(1,10)]+["T","T25","TT"]
d={"casc":{},"com":D["com"],"contas":{},"linhas":{},"resumo":D["resumo"],
   "gerado_de":D.get("gerado_em"),"fonte":D.get("fonte")}
erros=[]
for e in ("amana","topazio","consol"):
    for m in MESES:
        if m not in D["entities"][e]["dre"]: continue
        c=casc(e,m); d["casc"]["%s_%s"%(e,m)]=c
        r=D["resumo"].get(e,{}).get(m)
        if r:
            if abs(c["eb"]-R2(r["ebitda"]))>0.02: erros.append("EBITDA %s/%s arvore %.2f x KPI %.2f"%(e,m,c["eb"],r["ebitda"]))
            if abs(c["rb"]-R2(r["rb"]))>0.02:     erros.append("RECEITA %s/%s arvore %.2f x KPI %.2f"%(e,m,c["rb"],r["rb"]))
            if abs(c["res"]-R2(r["res"]))>0.02:   erros.append("RESULTADO %s/%s arvore %.2f x KPI %.2f"%(e,m,c["res"],r["res"]))
    sc=D["saldo_contas"][e]["banco"]
    ant={x["n"]:x["v"] for x in sc.get("8",[])}
    d["contas"][e]=[{"n":x["n"],"t":x["t"],"si":R2(ant.get(x["n"],0)),"sf":R2(x["v"])} for x in sc.get("9",[])]
    tree=D["entities"][e]["dre"].get("9") or {}
    d["linhas"]["%s_9"%e]=[{"t":t,"g":g,"c":c,"cat":x["cat"],"v":x["v"]}
        for t in tree for g in tree[t] for c in tree[t][g] for x in tree[t][g][c]]
    d["dfc_"+e]=D["entities"][e].get("dfc",{}).get("9")

# cascata do caixa, mes a mes, pelos prefixos dos grupos do DFC.  1.* entra, 2.1 e 2.6
# sao custo da operacao, 2.2 e 2.3 sao despesa, 2.7 e investimento e emprestimo, o resto
# e nao operacional.  Trava: saldo inicial + resultado = acumulado.
def cascata(e,m):
    g=D["entities"][e].get("dfc",{}).get(m)
    if not g: return None
    b={}
    for lado in ("receitas","despesas"):
        for nome,v in g[lado].items():
            p=nome.split()[0]
            k=("rec" if p.startswith("1.") else "cus" if p in ("2.1","2.6") else
               "des" if p in ("2.2","2.3") else "inv" if p=="2.7" else "nop")
            b[k]=R2(b.get(k,0)+v["total"])
    b={k:b.get(k,0.0) for k in ("rec","cus","des","inv","nop")}
    b["ger_op"]=R2(b["rec"]+b["cus"]+b["des"])
    b["ger_fim"]=R2(b["ger_op"]+b["inv"]+b["nop"])
    b["si"]=R2(g["saldo_inicial"]); b["sf"]=R2(g["acumulado"])
    if abs(R2(b["si"]+b["ger_fim"])-b["sf"])>0.02:
        erros.append("CAIXA %s/%s %.2f + %.2f != %.2f"%(e,m,b["si"],b["ger_fim"],b["sf"]))
    return b
d["caixa"]={m:cascata("consol",m) for m in [str(x) for x in range(1,10)]}

# receita de hospedagem da Amana mes a mes -- a linha que o relatorio confere
#              contra o relatorio de NFS-e da contabilidade
d["hospedagem"]={m:R2(sum(x["v"] for t in D["entities"]["amana"]["dre"].get(m,{})
   for g in D["entities"]["amana"]["dre"][m][t] for c in D["entities"]["amana"]["dre"][m][t][g]
   for x in D["entities"]["amana"]["dre"][m][t][g][c] if x["cat"]=="Receita de Hospedagem"))
   for m in map(str,range(1,10))}

# orcamento: orcado da rev 15.09 x realizado consolidado, linha a linha (nivel 'c')
IDX=8  # setembro, ano civil
real={}; fora_ebitda=set()
tree=D["entities"]["consol"]["dre"]["9"]
for t in tree:
    for g in tree[t]:
        for c in tree[t][g]:
            real[c]=R2(real.get(c,0)+sum(x["v"] for x in tree[t][g][c]))
            if t.startswith("3."): fora_ebitda.add(c)   # capex nao entra na ponte do EBITDA
lin=[]
for nome,serie in D["orc"]["linhas"].items():
    o=R2(serie[IDX]); r=R2(real.get(nome,0))
    lin.append({"l":nome,"o":o,"r":r,"d":R2(r-o)})
for nome,v in real.items():                      # realizado sem linha no orcamento
    if nome not in D["orc"]["linhas"] and nome not in fora_ebitda:
        lin.append({"l":nome,"o":0,"r":R2(v),"d":R2(v)})
lin.sort(key=lambda x:-abs(x["d"]))
os_=R2(sum(x["o"] for x in lin)); rs=d["casc"]["consol_9"]["eb"]
oa=R2(sum(sum(v[:IDX+1]) for v in D["orc"]["linhas"].values()))
ra=R2(sum(D["resumo"]["consol"][str(m)]["ebitda"] for m in range(1,10)))
# mesma confronto, mas acumulado jan-set: orcado soma os 9 meses, realizado vem da
# arvore do acumulado do ano
realT={}
treeT=D["entities"]["consol"]["dre"]["T"]
for t in treeT:
    for g in treeT[t]:
        for c in treeT[t][g]:
            realT[c]=R2(realT.get(c,0)+sum(x["v"] for x in treeT[t][g][c]))
            if t.startswith("3."): fora_ebitda.add(c)
linT=[]
for nome,serie in D["orc"]["linhas"].items():
    o=R2(sum(serie[:IDX+1])); r=R2(realT.get(nome,0))
    linT.append({"l":nome,"o":o,"r":r,"d":R2(r-o)})
for nome,v in realT.items():
    if nome not in D["orc"]["linhas"] and nome not in fora_ebitda:
        linT.append({"l":nome,"o":0,"r":R2(v),"d":R2(v)})
orc={"os":os_,"rs":rs,"oa":oa,"ra":ra,"linhas":lin,"linhas_ano":linT}

if erros:
    print("ABORTADO -- painel e relatorio contam coisas diferentes:");[print("  "+x) for x in erros];sys.exit(1)
json.dump(d,open("dados_rel.json","w"),ensure_ascii=False)
json.dump(orc,open("orc2.json","w"),ensure_ascii=False)
print("ok. painel gerado em %s"%D.get("gerado_em"))
for k in ("amana_9","topazio_9","consol_9","consol_8"):
    c=d["casc"][k];print("  %-11s rb %12.2f  ebitda %12.2f  res %12.2f"%(k,c["rb"],c["eb"],c["res"]))
print("  orcamento set: orcado %.2f x realizado %.2f | ano: %.2f x %.2f"%(os_,rs,oa,ra))
