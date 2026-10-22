# -*- coding: utf-8 -*-
"""Agosto: a receita de hospedagem passa a refletir as parcelas que voltaram para
   o mes da nota. So essa linha e mexida -- valor e lista -- e os KPIs do mes sao
   recalculados pelos mesmos buckets do dbucket da pagina.
   GRAVA=1 python3 ajusta_agosto.py"""
import json,os,re,collections
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f")
PAINEL=os.path.expanduser("~/painel-amanatopazio/")
RE_NAOOP=re.compile(r"pagamento indevido|devolu[çc][aã]o de pagamento indevido|^reembolsos?$|^reembolso$|empr[ée]stimos? e financiamentos?|tarifas? banc[áa]ria",re.I)
def bucket(t,g,c,cat):
    t,g,c=t.strip(),g.strip(),c.strip()
    if re.search(r"empr[ée]stimos? e financiamentos?",cat,re.I): return "emprestimo"
    if re.search(r"^aporte|rendimentos aplica",cat,re.I): return "recnaoop"
    if RE_NAOOP.search(cat) or re.search(r"Não operacional",c,re.I): return "naoop"
    if re.search(r"Taxa de cart",cat,re.I): return "deducoes"
    if t.startswith("3."): return "investimentos"
    if re.search(r"Receita Bruta",c,re.I): return "receita"
    if re.search(r"Dedu[çc]",c,re.I) or re.search(r"Outros Tributos",c,re.I): return "deducoes"
    if re.search(r"Receitas Financeiras|Outras Receitas|Recupera[çc]",c,re.I): return "recfin"
    if g.startswith("21"): return "pessoaldir" if re.search(r"Pessoal",c,re.I) else "custos"
    if re.search(r"Financeiras",c,re.I): return "despfin"
    if re.search(r"Vendas e Marketing",c,re.I): return "comercial"
    if re.search(r"Pessoal",c,re.I): return "pessoal"
    return "admin"
def kpis(arv,oc,adr):
    b=collections.defaultdict(float)
    for t,gs in (arv or {}).items():
        for g,cos in gs.items():
            for co,l in cos.items():
                for x in l: b[bucket(t,g,co,x["cat"])]+=x["v"]
    G=lambda k: R2(b.get(k,0))
    rb=G("receita"); cvar=R2(G("deducoes")+G("comercial"))
    cfix=R2(G("custos")+G("pessoaldir")+G("admin")+G("pessoal"))
    res=R2(sum(x["v"] for t,gs in (arv or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l))
    rl=R2(rb+G("deducoes"))
    comp={"rb":rb,"rl":rl,"custos":R2(G("custos")+G("pessoaldir")),"despesas":R2(G("comercial")+G("admin")+G("pessoal")),
          "inv":R2(G("investimentos")+G("naoop")+G("recnaoop")+G("emprestimo")),"res_op":R2(rb+cvar+cfix),
          "ebitda":R2(rb+cvar+cfix),"res":res,"fininc":G("recfin"),"finexp":G("despfin"),
          "margem":round(R2(rb+cvar+cfix)/rl,2) if abs(rl)>0.005 else 0.0}
    return {"rb":rb,"cvar":cvar,"cfix":cfix,"ebitda":R2(rb+cvar+cfix),"res":res,"oc":oc,"adr":adr},comp
def carrega(p):
    s=open(p,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])
B=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"ago.json")))
cat=B["amana"]["categorias"]
itens=[x for x in B["amana"]["itens"] if (cat.get(x["cat"]) or {}).get("desc")=="Receita de Hospedagem"]
novo=R2(sum(x["v"] for x in itens))
lista=sorted([{"d":x["em"][:5],"p":x["nome"],"nf":x["nf"],"v":R2(x["v"]),"b":""} for x in itens],
             key=lambda x:(x["d"][3:],x["d"][:2]))
s,j0,j1,D=carrega(PAINEL+"index.html")
for e,nome in (("amana","Receita de Hospedagem"),("consol","Receita de Hospedagem (Amana)")):
    ent=D["entities"][e]; T=ent["dre"]["8"]
    alvo=T["1. Lucro Bruto"]["01. Receita Líquida Operacional"]["01. Receita Bruta de Vendas"]
    linha=next(x for x in alvo if x["cat"]==nome)
    velho=linha["v"]; linha["v"]=novo
    alvo.sort(key=lambda x:-abs(x["v"]))
    ent["tx"]["8"][nome]=[dict(x) for x in lista]
    oc=D["resumo"][e]["8"].get("oc"); adr=D["resumo"][e]["8"].get("adr")
    r,c=kpis(T,oc,adr); D["resumo"][e]["8"]=r; ent["comp"]["8"]=c
    ent["dre_result"]["8"]=r["res"]
    print("  %-8s %s: %s -> %s  (%s) | %d lancamentos na lista | EBITDA %s"%(
        e,nome,f(velho),f(novo),f(novo-velho),len(lista),f(r["ebitda"])))
if os.environ.get("GRAVA"):
    blob=json.dumps(D,ensure_ascii=False)
    for arq in ("index.html","socios.html"):
        t,a,b,_=carrega(PAINEL+arq)
        open(PAINEL+arq,"w",encoding="utf-8").write(t[:a]+blob+t[b:]); print("  gravado",arq)
else: print("  (nada gravado -- rode com GRAVA=1)")
