# -*- coding: utf-8 -*-
"""Grava um mes NOVO de caixa (DFC) no painel -- so acrescenta.

Ate 25/11/2026 nao havia rotina: setembro entrou a mao (commit b20d0b8). Este
script pega a saida crua do gera_dfc.py e acrescenta o mes em D, sem tocar em
nenhum mes que ja esta publicado.

   MES=10 DFC=dfc_102026.json python3 grava_caixa_mes.py            # mostra
   MES=10 DFC=dfc_102026.json PAINEL=<pasta> GRAVA=1 python3 ...      # grava

O que ele faz, com as regras do DFC publicado (dfc_painel.py):
 1. por empresa: categoria -> (secao, grupo) herdado dos meses publicados;
    renomes; adiantamento de hospedagem colapsa em Receita de Hospedagem;
 2. continuidade: o saldo inicial de cada conta e o saldo final do mes anterior
    PUBLICADO. Conta corrente/adquirente tem de bater com o Omie (aborta se nao);
    aplicacao fecha no LIQUIDO do extrato de investimentos (DOC abaixo), com a
    diferenca numa linha propria. Aplicacao sem extrato fica com o movimento do
    Omie e e listada como SEM DOCUMENTO;
 3. consolidado: soma das duas, com o intercompany eliminado lancamento a
    lancamento (Amana paga POUSADA TOPAZIO / Topazio recebe de AMANA) -- as duas
    pontas tem de se anular, senao aborta;
 4. T e TT refeitos pela soma dos meses -- e antes de gravar, o mesmo algoritmo
    refaz o T e o TT dos meses ja publicados e tem de reproduzi-los;
 5. trava: tudo em D que nao e o mes novo (e T/TT do caixa) sai identico."""
import json,os,sys,copy,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ast
# as regras do dfc_painel.py, lidas sem executar o script (ele roda main() ao importar)
_T=ast.parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dfc_painel.py"),encoding="utf-8").read())
_V={n.targets[0].id:ast.literal_eval(n.value) for n in _T.body if isinstance(n,ast.Assign)
    and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ("RENOMES","COLAPSA_EM_HOSPEDAGEM","HOSP")}
RENOMES,COLAPSA_EM_HOSPEDAGEM,HOSP=_V["RENOMES"],_V["COLAPSA_EM_HOSPEDAGEM"],_V["HOSP"]
for _e in RENOMES: RENOMES[_e].setdefault("IR -Aplicação","IR - Aplicação")
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
M=os.environ.get("MES","10")
PAINEL=os.environ.get("PAINEL",os.path.expanduser("~/painel-amanatopazio/")).rstrip("/")+"/"
BRUTO=json.load(open(os.environ["DFC"]))
ROT={"10":"out","11":"nov","12":"dez"}
# liquido do extrato de investimentos no fim do mes (documento no Drive, pasta do mes)
DOC={"10":{
 ("amana","Santander - Aplicação"):(208986.17,"Extrato de Movimento e Posição OUT 2026 - AMANA (Santander), saldo líquido em 30/10"),
 ("amana","Bradesco - Invest Fácil"):(9878.17,"SALDO INVEST FACIL EM CCDI OUT 2026 - AMANA (Bradesco), valor líquido de outubro"),
 ("amana","Bradesco - CDB DI PJ"):(79465.25,"Extrato de Investimentos OUT 2026 AMANA (Bradesco CDB), líquido em 30/10"),
 ("topazio","Santander - Aplicação_Top_40-3"):(1357.80,"Extrato ContaMax nov/2026 (Topázio): aplicações de outubro ainda aplicadas em 31/10"),
 # SEM EXTRATO de 31/10: o saldo e o do Omie. A diferenca para o publicado em setembro
 # (3.521,49) e rendimento de setembro lancado no Omie depois do fechamento de 27/10.
 ("amana","Santander - CDB DI PJ"):(318184.84,"SEM EXTRATO DE 31/10 — saldo do Omie; inclui 3.521,49 de rendimento de setembro lançado depois do fechamento"),
}}[M]
SEM_EXTRATO={k for k,v in DOC.items() if v[1].startswith("SEM EXTRATO")}
IC_NOME={"amana":"POUSADA TOPAZIO","topazio":"AMANA EMPREENDIMENTOS"}
PRE={"amana":"Amana · ","topazio":"Topázio · "}
CAT_AJ={True:"Rendimentos Aplicações",False:"IR - Aplicação"}

def carrega(p):
    s=open(p,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])

def depara(D,ents):
    porcat={}
    for e in ents:
        for m,md in (D["entities"][e].get("dfc") or {}).items():
            for sec in ("receitas","despesas"):
                for g,gd in (md.get(sec) or {}).items():
                    for c in gd["cats"]: porcat.setdefault(c,(sec,g))
    return porcat

def monta(linhas,contas,porcat,ren):
    """linhas: [{d,cat,v,nome,b}] -> mes do DFC no formato do painel + detalhe"""
    cats=collections.defaultdict(float); det=collections.defaultdict(list); sem=[]
    gdre={}
    for l in linhas:
        c=ren.get(l["cat"],l["cat"]); c=HOSP if c in COLAPSA_EM_HOSPEDAGEM else c
        gdre[c]=l.get("grupo") or ""
    novas=[]
    for l in linhas:
        c=ren.get(l["cat"],l["cat"])
        if c in COLAPSA_EM_HOSPEDAGEM: c=HOSP
        cats[c]+=l["v"]
        det[c].append({"d":(l["d"] or "")[:5],"p":l["nome"],"b":l["b"],"nf":"","v":R2(l["v"])})
    out={"receitas":{},"despesas":{}}
    for c,v in cats.items():
        v=R2(v)
        if abs(v)<0.005: continue
        if c not in porcat:
            g=POS_DFC.get(c)
            if not g: sem.append((c,v,gdre.get(c))); continue
            porcat[c]=g; novas.append((c,gdre.get(c),g[1],v))
        sec,g=porcat[c]
        no=out[sec].setdefault(g,{"total":0.0,"cats":{}})
        no["cats"][c]={"total":v}; no["total"]=R2(no["total"]+v)
    out["resultado"]=R2(sum(cd["total"] for sec in ("receitas","despesas") for gd in out[sec].values() for cd in gd["cats"].values()))
    out["saldo_inicial"]=R2(sum(c["si"] for c in contas)); out["acumulado"]=R2(sum(c["sf"] for c in contas))
    out["contas"]=contas
    for n in novas: print("      categoria nova %-40s grupo DRE %-30s -> DFC %-40s %s"%(n[0][:40],n[1][:30],n[2][:40],f(n[3])))
    return out,{k:sorted(v,key=lambda x:x["d"][3:]+x["d"][:2]) for k,v in det.items() if k in cats and abs(R2(cats[k]))>=0.005},sem

def soma_meses(ent,meses):
    """T/TT: soma das categorias, saldo inicial do primeiro mes, final do ultimo"""
    dd=[ent["dfc"][m] for m in meses]; out={"receitas":{},"despesas":{}}
    for d in dd:
        for sec in ("receitas","despesas"):
            for g,gd in d[sec].items():
                no=out[sec].setdefault(g,{"total":0.0,"cats":{}})
                for c,cd in gd["cats"].items():
                    no["cats"].setdefault(c,{"total":0.0}); no["cats"][c]["total"]=R2(no["cats"][c]["total"]+cd["total"])
                no["total"]=R2(sum(x["total"] for x in no["cats"].values()))
    out["resultado"]=R2(sum(d["resultado"] for d in dd))
    out["saldo_inicial"]=dd[0]["saldo_inicial"]; out["acumulado"]=dd[-1]["acumulado"]
    si={}; sf={}
    for d in dd:
        for c in d["contas"]: si.setdefault(c["n"],c["si"]); sf[c["n"]]=c["sf"]
    out["contas"]=[{"n":n,"si":si[n],"sf":sf[n]} for n in sf]
    tx={}
    for m in meses:
        for c,l in (ent.get("txp") or {}).get(m,{}).items(): tx.setdefault(c,[]).extend(l)
    return out,tx

def pos_dfc(D):
    """categoria nova no caixa: vai para o grupo do DFC de mesmo nome que a sua
    posicao na arvore da DRE (DRE '13. Manutenção' -> DFC '2.1 Manutenção'),
    pela arvore publicada e pelo mapa manual MAN do publica_set.py"""
    tira=lambda x: x.split(" ",1)[1].strip().lower() if " " in x else x.lower()
    grupos={}
    for e in ("amana","topazio"):
        for m,d in D["entities"][e]["dfc"].items():
            for sec in ("receitas","despesas"):
                for g in d[sec]: grupos.setdefault(tira(g),(sec,g))
    co={}
    for e in ("amana","topazio"):
        for m,T in D["entities"][e]["dre"].items():
            for t,gs in T.items():
                for g,cos in gs.items():
                    for c,l in cos.items():
                        for x in l: co.setdefault(x["cat"],c)
    T=ast.parse(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"publica_set.py"),encoding="utf-8").read())
    MAN=next(ast.literal_eval(n.value) for n in T.body if isinstance(n,ast.Assign) and getattr(n.targets[0],"id","")=="MAN"
             and isinstance(n.value,ast.Dict))
    for e,d in MAN.items():
        for k,(alvo,pos) in d.items(): co.setdefault(k,pos[2])
    return {c:grupos[tira(x)] for c,x in co.items() if tira(x) in grupos}

def canon(x): return json.dumps(x,ensure_ascii=False,sort_keys=True)

def main():
    s,a,b,D=carrega(PAINEL+"index.html"); D0=copy.deepcopy(D)
    global POS_DFC; POS_DFC=pos_dfc(D)
    meses=[str(x) for x in D["months"]]; m25=[str(x) for x in D["months_25"]]
    assert M not in meses, "mes %s ja esta no caixa do painel"%M
    ant=meses[-1]
    # --- 0. o algoritmo do T/TT reproduz o que esta publicado?
    for e in ("amana","topazio","consol"):
        for tot,ms in (("T",meses),("TT",m25+meses)):
            o,_=soma_meses(D["entities"][e],ms); p=D["entities"][e]["dfc"][tot]
            for k in ("resultado","saldo_inicial","acumulado"):
                assert abs(o[k]-p[k])<0.02, "%s %s %s: refeito %s publicado %s"%(e,tot,k,o[k],p[k])
    print("== T e TT dos meses publicados reproduzidos pelo algoritmo")
    novo={}; sem_doc=[]; ajustes=[]
    linhas_c=[]; contas_c=[]; ic={}
    for e in ("amana","topazio"):
        Bq=BRUTO[e]; nome_cc={c["cc"]:c["nome"] for c in Bq["contas"]}
        L=[dict(l,b=nome_cc.get(l["cc"],"")) for l in Bq["linhas"]]
        pan={c["n"]:c["sf"] for c in D["entities"][e]["dfc"][ant]["contas"]}
        contas=[]
        for c in Bq["contas"]:
            si=pan.get(c["nome"])
            assert si is not None, "%s: conta %s nao existe no mes %s publicado"%(e,c["nome"],ant)
            sf=R2(si+c["mov"])
            if c["tipo"]=="CA":
                alvo=DOC.get((e,c["nome"]))
                if alvo:
                    aj=R2(alvo[0]-sf)
                    if abs(aj)>=0.005:
                        L.append({"d":"31/%s"%M.zfill(2),"cat":CAT_AJ[aj>0],"v":aj,"b":c["nome"],
                                  "nome":"Ajuste ao líquido do extrato de investimentos — "+alvo[1]})
                        ajustes.append((e,c["nome"],aj))
                    if (e,c["nome"]) in SEM_EXTRATO: sem_doc.append((e,c["nome"],alvo[0],c["fim"]))
                    sf=alvo[0]
                elif abs(c["fim"])>0.005: sem_doc.append((e,c["nome"],sf,c["fim"]))
            else:
                assert abs(si-c["ini"])<0.01, "%s %s: saldo publicado %s x Omie %s"%(e,c["nome"],si,c["ini"])
                assert abs(sf-c["fim"])<0.01
            contas.append({"n":c["nome"],"si":R2(si),"sf":R2(sf),"t":c["tipo"]})
        porcat=depara(D,[e])
        mes,det,sem=monta(L,[{k:v for k,v in c.items() if k!="t"} for c in contas],porcat,RENOMES.get(e,{}))
        assert not sem, "%s: categoria sem grupo no de-para: %s"%(e,sem)
        assert abs(R2(mes["saldo_inicial"]+mes["resultado"])-mes["acumulado"])<0.02, "%s: si+res != acumulado"%e
        novo[e]=(mes,det,contas)
        icl=[l for l in L if l["nome"].upper().startswith(IC_NOME[e])]; ic[e]=R2(sum(l["v"] for l in icl))
        linhas_c+=[dict(l,b=PRE[e]+l["b"]) for l in L if l not in icl]
        contas_c+=[{"n":PRE[e]+c["n"],"si":c["si"],"sf":c["sf"],"t":c["t"]} for c in contas]
        print("  %-8s resultado %14s | saldo %14s -> %14s | intercompany %s"%(e,f(mes["resultado"]),f(mes["saldo_inicial"]),f(mes["acumulado"]),f(ic[e])))
    assert abs(ic["amana"]+ic["topazio"])<0.01, "intercompany nao se anula: %s"%ic
    renc={}
    for e in ("amana","topazio"): renc.update(RENOMES.get(e,{}))
    mesc,detc,semc=monta(linhas_c,[{k:v for k,v in c.items() if k!="t"} for c in contas_c],depara(D,["consol","amana","topazio"]),renc)
    assert not semc, "consol: categoria sem grupo: %s"%semc
    soma=R2(novo["amana"][0]["resultado"]+novo["topazio"][0]["resultado"])
    assert abs(mesc["resultado"]-soma)<0.02, "consolidado %s != soma %s"%(mesc["resultado"],soma)
    novo["consol"]=(mesc,detc,contas_c)
    print("  %-8s resultado %14s | saldo %14s -> %14s"%("consol",f(mesc["resultado"]),f(mesc["saldo_inicial"]),f(mesc["acumulado"])))
    for x in ajustes: print("  ajuste ao extrato:  %-8s %-32s %s"%(x[0],x[1],f(x[2])))
    for x in sem_doc: print("  SEM DOCUMENTO:      %-8s %-32s publica %s (Omie bruto %s)"%(x[0],x[1],f(x[2]),f(x[3])))
    # --- grava em D
    for e,(mes,det,contas) in novo.items():
        ent=D["entities"][e]; ent["dfc"][M]=mes; ent["txp"][M]=det
        for tot,ms in (("T",meses+[M]),("TT",m25+meses+[M])):
            o,tx=soma_meses(ent,ms)
            # contas do acumulado: as publicadas, com o saldo final do mes novo
            sfm={c["n"]:c["sf"] for c in mes["contas"]}; velho=ent["dfc"][tot]["contas"]
            assert set(sfm)<=set(c["n"] for c in velho), "%s %s: conta nova no mes"%(e,tot)
            o["contas"]=[{"n":c["n"],"si":c["si"],"sf":sfm.get(c["n"],c["sf"])} for c in velho]
            ent["dfc"][tot]=o; ent["txp"][tot]=tx
        sc=D["saldo_contas"][e]
        banco=[{"n":c["n"],"v":c["sf"],"t":c["t"]} for c in contas if c["t"] in ("CC","CA")]
        fora=[{"n":c["n"],"v":c["sf"],"t":c["t"]} for c in contas if c["t"]=="AC"]
        for k in (M,"T","TT"):
            sc["banco"][k]=copy.deepcopy(banco); sc["fora"][k]=copy.deepcopy(fora); sc["comp"][k]=[]
    D["months"]=D["months"]+[int(M)]; D["mes_labels"][M]=ROT[M]
    # --- trava: nada fora do mes novo mudou
    def tira(X):
        X=copy.deepcopy(X); X["months"]=None; X["mes_labels"].pop(M,None)
        for e in ("amana","topazio","consol"):
            for k in (M,"T","TT"):
                X["entities"][e]["dfc"].pop(k,None); X["entities"][e]["txp"].pop(k,None)
                for t in ("banco","fora","comp"): X["saldo_contas"][e][t].pop(k,None)
        return canon(X)
    assert tira(D)==tira(D0), "algo fora do mes novo mudou -- abortado"
    assert D0["months"]+[int(M)]==D["months"]
    print("  trava: fora do mes %s e de T/TT do caixa, D saiu identico"%M)
    for e in ("amana","topazio","consol"):
        t=D["entities"][e]["dfc"]["T"]
        print("  %-8s ano: resultado %14s | saldo %14s -> %14s"%(e,f(t["resultado"]),f(t["saldo_inicial"]),f(t["acumulado"])))
    if os.environ.get("GRAVA"):
        blob=json.dumps(D,ensure_ascii=False)
        for arq in ("index.html","socios.html"):
            t,x,y,_=carrega(PAINEL+arq)
            open(PAINEL+arq,"w",encoding="utf-8").write(t[:x]+blob+t[y:]); print("  gravado",PAINEL+arq)
    else: print("\n  (nada gravado -- rode com GRAVA=1)")
main()
