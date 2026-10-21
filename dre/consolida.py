# -*- coding: utf-8 -*-
"""Consolidacao da DRE do painel -- a regra que jan-ago publicou.
   Resgatada de consol_ago.py em 20/10/2026; aqui generalizada para qualquer mes.
   1. soma Amana + Topazio categoria a categoria;
   2. sufixa com (Amana)/(Topázio) SO as linhas de receita, que nao podem se somar;
   3. elimina o intercompany pela perna de custo da Amana (Compra de Diarias a Topazio).
   CONFERE=1 python3 consolida.py 1 2 3 ...   -> compara com o que esta publicado
   python3 consolida.py 9                     -> imprime a arvore do mes (json em stdout)"""
import json,os,sys
R2=lambda v: round((v or 0)+0.0,2)
IC="Compra de Diarias a Topazio"
COM_SUFIXO=("01. Receita Bruta de Vendas","01. Outras Receitas")
SUF={"amana":" (Amana)","topazio":" (Topázio)"}

def consolida(tree_por_emp,tx_por_emp=None):
    """tree_por_emp = {'amana':arvore,'topazio':arvore}; arvore = {t:{g:{co:[{cat,v}]}}}"""
    arv={}; txc={}
    for emp in ("amana","topazio"):
        for g1,d1 in (tree_por_emp.get(emp) or {}).items():
            for g2,d2 in d1.items():
                for g3,lst in d2.items():
                    for it in lst:
                        if emp=="amana" and it["cat"]==IC: continue
                        nome=it["cat"]+SUF[emp] if g3 in COM_SUFIXO else it["cat"]
                        no=arv.setdefault(g1,{}).setdefault(g2,{}).setdefault(g3,{})
                        no[nome]=R2(no.get(nome,0)+it["v"])
                        tx=(tx_por_emp or {}).get(emp) or {}
                        if it["cat"] in tx: txc.setdefault(nome,[]).extend(tx[it["cat"]])
    for g1 in arv:
        for g2 in arv[g1]:
            for g3 in arv[g1][g2]:
                arv[g1][g2][g3]=sorted([{"cat":k,"v":v} for k,v in arv[g1][g2][g3].items()],key=lambda x:-abs(x["v"]))
    for k in txc: txc[k]=sorted(txc[k],key=lambda x:x.get("d") or "")
    return arv,txc

def carrega(p):
    s=open(p,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: return s,j,k+1,json.loads(s[j:k+1])

def linhas(arv):
    return {(t,g,co,x["cat"]):x["v"] for t,gs in (arv or {}).items() for g,cos in gs.items() for co,it in cos.items() for x in it}

if __name__=="__main__":
    s,j0,j1,D=carrega(os.path.expanduser("~/painel-amanatopazio/index.html"))
    E=D["entities"]
    for m in sys.argv[1:]:
        arv,txc=consolida({e:(E[e].get("dre") or {}).get(m) for e in ("amana","topazio")},
                          {e:(E[e].get("tx")  or {}).get(m) for e in ("amana","topazio")})
        if os.environ.get("CONFERE"):
            pub=linhas((E["consol"].get("dre") or {}).get(m)); novo=linhas(arv)
            dif=[(k,pub.get(k),novo.get(k)) for k in set(pub)|set(novo) if abs(R2((novo.get(k) or 0)-(pub.get(k) or 0)))>0.004]
            tp=R2(sum(pub.values())); tn=R2(sum(novo.values()))
            print("mes %-4s publicado %12s | regra %12s | linhas %d vs %d | divergencias %d"%(m,format(tp,",.2f"),format(tn,",.2f"),len(pub),len(novo),len(dif)))
            for k,a,b in sorted(dif)[:12]: print("      %-58s pub %12s regra %12s"%(" / ".join(k[1:])[:58],format(a or 0,",.2f"),format(b or 0,",.2f")))
        else:
            print(json.dumps({"dre":arv,"tx":txc},ensure_ascii=False))
