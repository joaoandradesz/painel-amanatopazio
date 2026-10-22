# -*- coding: utf-8 -*-
"""Publica a DRE de um mes novo no painel (setembro/2026 por padrao).
   Regras, todas ja estabelecidas e documentadas em conferencia/LEIA.md:
   - titulo entra pela data de EMISSAO, com o rateio aberto perna por perna;
   - CANCELADO fica fora; categoria sem dadosDRE fica fora (conta de controle);
   - lancamento avulso de conta corrente entra como o Omie faz na DRE;
   - o caminho na arvore vem de jan-ago, pela posicao de maior peso;
   - uma categoria, uma linha em cada no;
   - consolidado = consolida.py (soma, sufixo so na receita, elimina o IC);
   - KPI (resumo) e cascata (comp) saem dos buckets do dbucket DA PAGINA.
   python3 publica_set.py            -> mostra o que faria
   GRAVA=1 python3 publica_set.py    -> grava index.html e socios.html"""
import json,collections,unicodedata,re,os,sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from consolida import consolida,carrega

MES=os.environ.get("MES","9"); ANO="2026"
PAINEL=os.path.expanduser("~/painel-amanatopazio/")
BASE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"set.json")
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
def nz(s):
    s=unicodedata.normalize("NFKD",(s or "")).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+"," ",s).strip()

# de-para das categorias que o mes trouxe e a arvore de jan-ago nao tinha
MAN={
 "amana":{
  "Manutenção predial - materiais":(None,("1. Lucro Bruto","21. Custos","13. Manutenção")),
  "Pontuação - Equipe e Diretoria":("Pontuação e Premiação",("2. Despesas","11. Fixas","04. Despesas de Vendas e Marketing")),
  "Adiantamentos":(None,("2. Despesas","11. Fixas","01. Despesas com Pessoal")),
  "ISS":(None,("1. Lucro Bruto","01. Receita Líquida Operacional","03. Deduções de Receita")),
  "Alimentação de Colaboradores Operacional":(None,("1. Lucro Bruto","21. Custos","05. Pessoal indireto da operação")),
 },
 "topazio":{
  # decisao C do João: premiacao da equipe de operacao acompanha o salario, em custo direto
  "Premiação - equipe":(None,("1. Lucro Bruto","21. Custos","04. Pessoal direto")),
  "Gestor operacional PJ":(None,("1. Lucro Bruto","21. Custos","06. Prestação de serviços operacionais")),
  "Insumos itens para revenda":("Insumos para revenda",("1. Lucro Bruto","21. Custos","11. Insumos para revenda")),
  "Retenção de impostos federais":(None,("2. Despesas","11. Fixas","05. Outros Tributos")),
  # nome proprio de proposito: juntar com "Pagamento indevido / a maior" poria a
  # mesma categoria em duas posicoes da arvore -- e o bug que o Tiago achou
  "Devolução de pagamento indevido / a maior":(None,("2. Despesas","01. Variáveis","02. Recuperação de Despesas Variáveis")),
  "Manutenção predial":(None,("3. Investimentos","01. Investimentos","01. Ativos")),
  # decisao A do João: gestao e administrativo -- fica onde jan-ago ja punha
  "Prestadores Recorrente - Gestão":(None,("2. Despesas","11. Fixas","02. Despesa Indireta de Pessoal Indireto")),
 }}
MAN={e:{nz(k):v for k,v in d.items()} for e,d in MAN.items()}

# ---------- buckets: a mesma classificacao do dbucket() da pagina ----------
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
def buckets(arv):
    b=collections.defaultdict(float)
    for t,gs in (arv or {}).items():
        for g,cos in gs.items():
            for co,l in cos.items():
                for x in l: b[bucket(t,g,co,x["cat"])]+=x["v"]
    return b
def kpis(arv,oc=None,adr=None):
    b=buckets(arv); G=lambda k: R2(b.get(k,0))
    rb=G("receita"); cvar=R2(G("deducoes")+G("comercial"))
    cfix=R2(G("custos")+G("pessoaldir")+G("admin")+G("pessoal"))
    res=R2(sum(x["v"] for t,gs in (arv or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l))
    rl=R2(rb+G("deducoes"))
    comp={"rb":rb,"rl":rl,"custos":R2(G("custos")+G("pessoaldir")),
          "despesas":R2(G("comercial")+G("admin")+G("pessoal")),
          "inv":R2(G("investimentos")+G("naoop")+G("recnaoop")+G("emprestimo")),
          "res_op":R2(rb+cvar+cfix),"ebitda":R2(rb+cvar+cfix),"res":res,
          "fininc":G("recfin"),"finexp":G("despfin"),
          "margem":round(R2(rb+cvar+cfix)/rl,2) if abs(rl)>0.005 else 0.0}
    resumo={"rb":rb,"cvar":cvar,"cfix":cfix,"ebitda":R2(rb+cvar+cfix),"res":res,"oc":oc,"adr":adr}
    return resumo,comp

# ---------- arvore do mes, por empresa ----------
def arvore_mes(D):
    B=json.load(open(BASE))
    meses_ant=[str(x) for x in D["anos"][ANO]["meses"]]
    out={}
    for emp in ("amana","topazio"):
        peso=collections.defaultdict(lambda: collections.defaultdict(float)); nome_of={}
        for m in meses_ant:
            for t,gs in ((D["entities"][emp].get("dre") or {}).get(m) or {}).items():
                for g,cos in gs.items():
                    for co,l in cos.items():
                        for x in l:
                            peso[nz(x["cat"])][(t,g,co)]+=abs(x["v"]); nome_of[nz(x["cat"])]=x["cat"]
        cam={k:(nome_of[k],max(v.items(),key=lambda kv:kv[1])[0]) for k,v in peso.items()}
        cat=B[emp]["categorias"]; arv={}; tx=collections.defaultdict(list); fora=[]
        for x in B[emp]["itens"]+B[emp]["avulsos"]:
            c=cat.get(x["cat"])
            if not c or not c["tem_dre"]: continue
            d=c["desc"]; k=nz(d)
            if k in cam: nome,pos=cam[k]
            elif k in MAN[emp]:
                alvo,pos=MAN[emp][k]; nome=alvo or d
            else: fora.append((x["cat"],d,x["v"])); continue
            t,g,co=pos
            arv.setdefault(t,{}).setdefault(g,{}).setdefault(co,collections.defaultdict(float))
            arv[t][g][co][nome]+=x["v"]
            tx[nome].append({"d":x["em"][:5],"p":x["nome"],"nf":x["nf"],"v":R2(x["v"]),"b":""})
        A={t:{g:{co:sorted([{"cat":k,"v":R2(v)} for k,v in d.items() if abs(R2(v))>0.004],key=lambda x:-abs(x["v"]))
                for co,d in cos.items()} for g,cos in gs.items()} for t,gs in arv.items()}
        A={t:{g:{co:l for co,l in cos.items() if l} for g,cos in gs.items()} for t,gs in A.items()}
        A={t:{g:cos for g,cos in gs.items() if cos} for t,gs in A.items()}
        X={k:sorted(v,key=lambda x:(x["d"][3:],x["d"][:2])) for k,v in tx.items()}
        tot=R2(sum(x["v"] for t,gs in A.items() for g,cos in gs.items() for co,l in cos.items() for x in l))
        print("  %-8s arvore do mes %s: resultado %14s | %3d categorias | fora do mapa: %d"%(emp,MES,f(tot),len(X),len(fora)))
        for cc,dd,vv in fora: print("      FORA %-9s %-38s %s"%(cc,dd[:38],f(vv)))
        out[emp]=(A,X)
    return out

# ---------- utilitarios de arvore ----------
def soma_em(dest,arv):
    """soma arv dentro de dest, uma categoria uma linha"""
    for t,gs in (arv or {}).items():
        for g,cos in gs.items():
            for co,l in cos.items():
                no=dest.setdefault(t,{}).setdefault(g,{}).setdefault(co,[])
                for x in l:
                    ex=next((y for y in no if y["cat"]==x["cat"]),None)
                    if ex: ex["v"]=R2(ex["v"]+x["v"])
                    else: no.append({"cat":x["cat"],"v":R2(x["v"])})
def ordena(arv):
    for t in list(arv):
        for g in list(arv[t]):
            for co in list(arv[t][g]):
                arv[t][g][co]=sorted([x for x in arv[t][g][co] if abs(R2(x["v"]))>0.004],key=lambda x:-abs(x["v"]))
                if not arv[t][g][co]: del arv[t][g][co]
            if not arv[t][g]: del arv[t][g]
        if not arv[t]: del arv[t]
def cats_do_mes(arv):
    return {x["cat"] for t,gs in (arv or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l}

def limpa_duplicadas(D):
    """uma categoria, uma linha: funde linhas repetidas no mesmo no. Nao muda total."""
    n=0
    for e in ("amana","topazio","consol"):
        for m,T in (D["entities"][e].get("dre") or {}).items():
            for t,gs in T.items():
                for g,cos in gs.items():
                    for co,l in cos.items():
                        c=collections.Counter(x["cat"] for x in l)
                        if any(v>1 for v in c.values()):
                            agg=collections.OrderedDict()
                            for x in l: agg[x["cat"]]=R2(agg.get(x["cat"],0)+x["v"])
                            novo=sorted([{"cat":k,"v":v} for k,v in agg.items() if abs(v)>0.004],key=lambda x:-abs(x["v"]))
                            print("      funde %-8s %-4s %-32s %d -> %d linhas"%(e,m,co[:32],len(l),len(novo)))
                            cos[co]=novo; n+=1
    print("  nos com linha repetida corrigidos: %d"%n)

# ---------- publicacao ----------
def main():
    s,j0,j1,D=carrega(PAINEL+"index.html")
    print("== antes: meses com DRE %s | sem_dre %s"%(sorted((D["entities"]["amana"].get("dre") or {}).keys(),key=str),D.get("sem_dre")))
    antes={(e,m):R2(sum(x["v"] for t,gs in (T or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l))
           for e in ("amana","topazio","consol") for m,T in (D["entities"][e].get("dre") or {}).items()}
    print("\n== limpeza: linhas repetidas no mesmo no")
    limpa_duplicadas(D)
    depois={(e,m):R2(sum(x["v"] for t,gs in (T or {}).items() for g,cos in gs.items() for co,l in cos.items() for x in l))
            for e in ("amana","topazio","consol") for m,T in (D["entities"][e].get("dre") or {}).items()}
    mex=[k for k in antes if abs(antes[k]-depois.get(k,0))>0.004]
    print("  totais alterados pela limpeza: %d %s"%(len(mex),mex))
    assert not mex, "a limpeza nao pode mexer em total"

    print("\n== arvore de %s/%s"%(MES,ANO))
    por_emp=arvore_mes(D)
    arvC,txC=consolida({e:por_emp[e][0] for e in por_emp},{e:por_emp[e][1] for e in por_emp})
    ordena(arvC)
    totC=R2(sum(x["v"] for t,gs in arvC.items() for g,cos in gs.items() for co,l in cos.items() for x in l))
    soma=R2(sum(R2(sum(x["v"] for t,gs in por_emp[e][0].items() for g,cos in gs.items() for co,l in cos.items() for x in l)) for e in por_emp))
    print("  consol    arvore do mes %s: resultado %14s | soma simples %s | IC eliminado %s"%(MES,f(totC),f(soma),f(totC-soma)))

    novo={"amana":por_emp["amana"],"topazio":por_emp["topazio"],"consol":(arvC,txC)}
    OC=(D["com"].get(MES) or {}).get("oc"); ADR=(D["com"].get(MES) or {}).get("tkt")
    print()
    for e in ("amana","topazio","consol"):
        ent=D["entities"][e]; A,X=novo[e]
        ent["dre"][MES]=A; ent["tx"][MES]=X
        ent["dre_result"][MES]=R2(sum(x["v"] for t,gs in A.items() for g,cos in gs.items() for co,l in cos.items() for x in l))
        ent["acq"][MES]={}
        r,c=kpis(A,None if e=="amana" else OC,None if e=="amana" else ADR)
        D["resumo"][e][MES]=r; ent["comp"][MES]=c
        # acumulados REFEITOS a partir dos meses (idempotente: rodar de novo nao dobra)
        m26=[str(x) for x in D["anos"][ANO]["meses"]]+([MES] if MES not in [str(x) for x in D["anos"][ANO]["meses"]] else [])
        m25=[str(x) for x in D["anos"]["2025"]["meses"]]
        for tot,meses in (("T",m26),("TT",m26+m25)):
            arv={}; txa={}
            for m in meses:
                Am=ent["dre"].get(m) or {}
                soma_em(arv,Am)
                Xm=(ent.get("tx") or {}).get(m) or {}
                for cat in cats_do_mes(Am):
                    if cat in Xm: txa.setdefault(cat,[]).extend(Xm[cat])
            ordena(arv)
            ent["dre"][tot]=arv; ent["tx"][tot]=txa
            ent["dre_result"][tot]=R2(sum(x["v"] for t,gs in ent["dre"][tot].items() for g,cos in gs.items() for co,l in cos.items() for x in l))
            rt,ct=kpis(ent["dre"][tot],(D["com"].get("T") or {}).get("oc") if e!="amana" else None,
                                        (D["com"].get("T") or {}).get("tkt") if e!="amana" else None)
            if tot=="TT": rt["oc"]=D["resumo"][e]["TT"].get("oc"); rt["adr"]=D["resumo"][e]["TT"].get("adr")
            D["resumo"][e][tot]=rt; ent["comp"][tot]=ct
        print("  %-8s mes %s: receita %14s  EBITDA %14s  resultado %14s | ano: EBITDA %14s resultado %14s"%(
            e,MES,f(r["rb"]),f(r["ebitda"]),f(r["res"]),f(D["resumo"][e]["T"]["ebitda"]),f(D["resumo"][e]["T"]["res"])))
    # trava: uma categoria nunca em duas posicoes da arvore (mes e acumulados)
    ruim=[]
    for e in ("amana","topazio","consol"):
        for m in (MES,"T","TT"):
            pos=collections.defaultdict(set)
            for t,gs in (D["entities"][e]["dre"].get(m) or {}).items():
                for g,cos in gs.items():
                    for co in cos: 
                        for x in cos[co]: pos[x["cat"]].add((t,g,co))
            for c,ps in pos.items():
                if len(ps)>1: ruim.append((e,m,c,sorted(ps)))
    for r in ruim: print("  DUAS POSICOES:",r[0],r[1],r[2],r[3])
    assert not ruim, "categoria em mais de uma posicao da arvore"
    print("  trava: nenhuma categoria em duas posicoes")
    D["sem_dre"]=[m for m in (D.get("sem_dre") or []) if str(m)!=MES]
    if int(MES) not in D["anos"][ANO]["meses"]: D["anos"][ANO]["meses"]=sorted(D["anos"][ANO]["meses"]+[int(MES)])
    D["fonte"]=("DFC pelo extrato do Omie (jan/26 a 30/09/26 e ago–dez/25) · DRE pelos relatórios oficiais do Omie "
                "(jan a jul/26), pela base de títulos do Omie (ago e set/26) e pela base caixa em 2025")
    D["gerado_em"]="20/10/2026"
    if os.environ.get("GRAVA"):
        blob=json.dumps(D,ensure_ascii=False)
        for arq in ("index.html","socios.html"):
            t,a,b,_=carrega(PAINEL+arq)
            open(PAINEL+arq,"w",encoding="utf-8").write(t[:a]+blob+t[b:])
            print("  gravado",arq)
    else: print("\n  (nada gravado -- rode com GRAVA=1)")
main()
