# -*- coding: utf-8 -*-
"""Monta a DRE de setembro/2026 no painel, pelas regras ja estabelecidas:
titulos por data de EMISSAO com rateio aberto + avulsos de conta corrente,
fora as categorias sem dadosDRE, e o caminho na arvore herdado de jan-ago."""
import json,collections,unicodedata,re,sys
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
def nz(s):
    s=unicodedata.normalize("NFKD",(s or "")).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+"," ",s).strip()
B=json.load(open("set.json"))
PAINEL="/Users/joaoandrade/painel-amanatopazio/"
# de-para das categorias que setembro trouxe e a arvore nao tinha
MAN={
 "amana":{
  "Pontuação - Equipe e Diretoria":("Pontuação e Premiação",("2. Despesas","11. Fixas","04. Despesas de Vendas e Marketing")),
  "Adiantamentos":(None,("2. Despesas","11. Fixas","01. Despesas com Pessoal")),
  "ISS":(None,("1. Lucro Bruto","01. Receita Líquida Operacional","03. Deduções de Receita")),
  "Alimentação de Colaboradores Operacional":(None,("1. Lucro Bruto","21. Custos","05. Pessoal indireto da operação")),
 },
 "topazio":{
  # decisao C: premiacao de equipe de operacao acompanha o salario, em custo direto
  "Premiação - equipe":(None,("1. Lucro Bruto","21. Custos","04. Pessoal direto")),
  "Gestor operacional PJ":(None,("1. Lucro Bruto","21. Custos","06. Prestação de serviços operacionais")),
  "Insumos itens para revenda":("Insumos para revenda",("1. Lucro Bruto","21. Custos","11. Insumos para revenda")),
  "Retenção de impostos federais":(None,("2. Despesas","11. Fixas","05. Outros Tributos")),
  "Devolução de pagamento indevido / a maior":("Pagamento indevido / a maior",("2. Despesas","01. Variáveis","02. Recuperação de Despesas Variáveis")),
  "Manutenção predial":(None,("3. Investimentos","01. Investimentos","01. Ativos")),
  # decisao A: gestao e administrativo -- fica onde jan-ago ja punha
  "Prestadores Recorrente - Gestão":(None,("2. Despesas","11. Fixas","02. Despesa Indireta de Pessoal Indireto")),
 }}
MAN={e:{nz(k):v for k,v in d.items()} for e,d in MAN.items()}
def carrega(p):
    s=open(p,encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])
src,j0,j1,D=carrega(PAINEL+"index.html")
cam={}
for e in ("amana","topazio"):
    c=collections.defaultdict(collections.Counter)
    for m in [str(x) for x in range(1,9)]:
        for t,gs in ((D["entities"][e].get("dre") or {}).get(m) or {}).items():
            for g,cos in gs.items():
                for co,it in cos.items():
                    for x in it: c[x["cat"]][(t,g,co)]+=1
    cam[e]={nz(k):(k,v.most_common(1)[0][0]) for k,v in c.items()}
RES={}
for emp in ("amana","topazio"):
    cat=B[emp]["categorias"]; arv={}; tx=collections.defaultdict(list); fora=[]
    for x in B[emp]["itens"]+B[emp]["avulsos"]:
        c=cat.get(x["cat"])
        if not c or not c["tem_dre"]: continue
        d=c["desc"]
        if nz(d) in cam[emp]: nome,pos=cam[emp][nz(d)]
        elif nz(d) in MAN[emp]:
            alvo,pos=MAN[emp][nz(d)]; nome=alvo or d
        else: fora.append((x["cat"],d,x["v"])); continue
        t,g,co=pos
        arv.setdefault(t,{}).setdefault(g,{}).setdefault(co,collections.defaultdict(float))
        arv[t][g][co][nome]+=x["v"]
        tx[nome].append({"d":x["em"][:5],"p":x["nome"],"nf":x["nf"],"v":x["v"],"b":""})
    arvore={t:{g:{co:[{"cat":k,"v":R2(v)} for k,v in d.items() if abs(v)>0.0004] for co,d in cos.items()} for g,cos in gs.items()} for t,gs in arv.items()}
    RES[emp]={"arv":arvore,"tx":{k:v for k,v in tx.items()},"fora":fora,
              "total":R2(sum(x["v"] for t,gs in arv.items() for g,cos in gs.items() for co,d in cos.items() for x in [{"v":vv} for vv in d.values()]))}
    print("%-8s arvore montada | total %s | fora do mapa: %d"%(emp,f(RES[emp]["total"]),len(fora)))
    for c,d,v in fora: print("    FORA %-9s %-38s %s"%(c,d[:38],f(v)))
json.dump(RES,open("set_arvore.json","w"),ensure_ascii=False)
