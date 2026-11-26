# -*- coding: utf-8 -*-
"""Converte a saida crua do gera_dfc.py (extrato do Omie) para a forma que o
   painel publica, aplicando as REGRAS que o DFC publicado usa.

   gera_dfc.py le o extrato e nao interpreta nada. O DFC do painel aplica em
   cima dele um conjunto de regras que, ate 04/11/2026, so existiam no commit
   de quem as aplicou. Este script as traz para um lugar so.

   REGRAS PORTADAS (deterministicas, reproduzem setembro):
   1. RENOMES: a mesma categoria tem nome diferente nas duas bases, ou mudou de
      nome depois que o mes foi publicado.
   2. COLAPSO DO ADIANTAMENTO: "Adiantamento de Hospedagem" (entrada) e
      "Reversao de Adiantamento" (saida) sao lancamentos de controle que se
      anulam; entram dentro de "Receita de Hospedagem", que passa a mostrar o
      caixa efetivamente recebido. Regra do commit 62cb543.
   3. DE-PARA DOS GRUPOS: o grupo do DFC do painel ("2.1 Insumos de cafe da
      manha") nao e o grupo da DRE ("Custo dos Servicos Prestados"). O mapa sai
      do proprio setembro publicado, em depara_dfc.json, com reserva pelo grupo
      da DRE quando a categoria e nova.

   NAO PORTADAS, porque nao sao regra:
   4. As linhas de aplicacao (Rendimentos, IR, IOF, IRPJ) vem do EXTRATO DE
      INVESTIMENTOS do banco, lancadas a mao -- ver ajusta_caixa_cdb.py. Sem o
      extrato do mes nao ha como reproduzi-las.
   5. Reclassificacoes parciais de lancamento feitas so no painel (parte de uma
      categoria movida para outra). Sao correcoes pontuais, nao regra.

       python3 dfc_painel.py dfc_102026.json          # mostra
       CONFERE=09 python3 dfc_painel.py dfc_092026.json   # prova contra o publicado
"""
import json,os,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
RAIZ=os.path.expanduser("~/painel-amanatopazio/")

# o renome e por empresa: "ISS | Permanencia" virou "ISS" so na Amana; na
# Topazio o painel publicou com o nome do Omie.
RENOMES={
 "amana":{"Pontuação - Equipe e Diretoria":"Variável",   # 2.02.97, nome do Omie desde out/2026
          "ISS | Permanência":"ISS"},
 "topazio":{"Premiação - equipe":"Pontuação e Premiação",
          "Devolução de pagamento indevido / a maior":"Devolução de Pagamento Indevido / A maior",
          "Insumos café da manhã":"Insumos Café da Manhã",
          "Insumos itens para revenda":"Insumos para revenda",
          "Entrada de Transferência":"Transferência · Caixinha"},
}
# regra 2: estas colapsam dentro de Receita de Hospedagem
COLAPSA_EM_HOSPEDAGEM={"Adiantamento de Hospedagem","Reversão de Adiantamento de Hospedagem",
                       "Reversão de Adiantamento"}
HOSP="Receita de Hospedagem"
# regra 4: linhas que vem do extrato de investimentos, nao do extrato de conta
APLICACAO={"Rendimentos Aplicações","Rendimentos","IR - Aplicação","IR -Aplicação","IOF","IRPJ"}

def carrega_painel():
    s=open(RAIZ+"index.html",encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return json.loads(s[j:k+1])

def depara(D):
    """cat -> (secao, grupo) a partir dos meses ja publicados; e grupo da DRE -> grupo do DFC"""
    porcat={}; pordre=collections.defaultdict(collections.Counter)
    for e in ("amana","topazio"):
        for m,md in (D["entities"][e].get("dfc") or {}).items():
            for sec in ("receitas","despesas"):
                for g,gd in (md.get(sec) or {}).items():
                    for c in gd["cats"]: porcat[c]=(sec,g)
    return porcat,pordre

def converte(bruto,porcat,pordre_dre,emp):
    cats=collections.defaultdict(float); det=collections.defaultdict(list)
    for l in bruto["linhas"]:
        c=RENOMES.get(emp,{}).get(l["cat"],l["cat"])
        if c in COLAPSA_EM_HOSPEDAGEM: c=HOSP
        cats[c]+=l["v"]
        det[c].append({"d":(l["d"] or "")[:5],"p":l["nome"],"b":"","nf":"","v":R2(l["v"])})
    out={"receitas":{},"despesas":{},"contas":[{"n":s["nome"],"si":s["ini"],"sf":s["fim"]} for s in bruto["contas"]]}
    for c,v in cats.items():
        v=R2(v)
        sec,g=porcat.get(c) or (("receitas" if v>0 else "despesas"),pordre_dre.get(c) or "(a classificar)")
        no=out[sec].setdefault(g,{"total":0.0,"cats":{}})
        no["cats"][c]={"total":v}; no["total"]=R2(no["total"]+v)
    out["resultado"]=R2(sum(cd["total"] for sec in ("receitas","despesas") for gd in out[sec].values() for cd in gd["cats"].values()))
    out["saldo_inicial"]=R2(sum(s["ini"] for s in bruto["contas"]))
    out["acumulado"]=R2(sum(s["fim"] for s in bruto["contas"]))
    return out,dict(det)

def main():
    arq=sys.argv[1] if len(sys.argv)>1 else "dfc_102026.json"
    bruto=json.load(open(arq))
    D=carrega_painel(); porcat,_=depara(D)
    pordre={}
    conf=os.environ.get("CONFERE")
    for emp in bruto:
        novo,det=converte(bruto[emp],porcat,pordre,emp)
        print("\n===== %s   resultado %s   saldo %s -> %s"%(
            emp.upper(),f(novo["resultado"]),f(novo["saldo_inicial"]),f(novo["acumulado"])))
        if not conf:
            print("   %d categorias em %d grupos"%(
                sum(len(gd["cats"]) for sec in ("receitas","despesas") for gd in novo[sec].values()),
                len(novo["receitas"])+len(novo["despesas"])))
            sc=[c for sec in ("receitas","despesas") for g,gd in novo[sec].items() for c in gd["cats"] if g=="(a classificar)"]
            if sc: print("   categorias sem grupo no de-para: %s"%sc)
            continue
        pan=D["entities"][emp]["dfc"][conf]
        P={c:R2(cd["total"]) for sec in ("receitas","despesas") for gd in pan[sec].values() for c,cd in gd["cats"].items()}
        N={c:R2(cd["total"]) for sec in ("receitas","despesas") for gd in novo[sec].values() for c,cd in gd["cats"].items()}
        print("   publicado %s   reproduzido %s   resta %s"%(
            f(pan["resultado"]),f(novo["resultado"]),f(R2(pan["resultado"]-novo["resultado"]))))
        apl=0.0; rec=0.0; linhas=[]
        for c in sorted(set(P)|set(N)):
            d=R2(P.get(c,0)-N.get(c,0))
            if abs(d)<0.005: continue
            fam="APLICAÇÃO (extrato do banco)" if c in APLICACAO else "reclassificação pontual"
            if c in APLICACAO: apl+=d
            else: rec+=d
            linhas.append((fam,c,P.get(c),N.get(c),d))
        print("   categorias que batem ao centavo: %d de %d"%(len(set(P)&set(N))-len([1 for _,c,_,_,_ in linhas if c in P and c in N]),len(set(P)|set(N))))
        for fam,c,p,n,d in sorted(linhas):
            print("     %-28s %-40s pub %12s  nosso %12s  %12s"%(
                fam,c[:40],("%s"%f(p)) if p is not None else "—",("%s"%f(n)) if n is not None else "—",f(d)))
        print("     %-28s %40s %40s"%("soma: aplicação",f(apl),""))
        print("     %-28s %40s %40s"%("soma: reclassificação",f(rec),""))
main()
