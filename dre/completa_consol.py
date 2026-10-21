# -*- coding: utf-8 -*-
"""No consolidado a lista de lancamentos de algumas categorias vinha so de uma
   das empresas. Onde juntar Amana + Topazio faz a soma bater com a linha, a
   lista passa a ser a das duas. A linha nao e tocada."""
import json,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
for ALVO in sys.argv[1:]:
    s=open(ALVO,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: end=k+1;break
    D=json.loads(s[j:end]); nome=ALVO.split("/")[-1]; n=0; ex=[]
    C=D["entities"]["consol"]; A=D["entities"]["amana"]; T=D["entities"]["topazio"]
    for key,arvore in (("tx","dre"),("txp","dfc")):
        for m in [str(x) for x in range(1,10)]:
            # valor da linha no consolidado
            linha=collections.defaultdict(float)
            if arvore=="dre":
                for t,gs in ((C.get("dre") or {}).get(m) or {}).items():
                    for g,cos in gs.items():
                        for co,itens in cos.items():
                            for x in itens: linha[x["cat"]]+=x["v"]
            else:
                md=(C.get("dfc") or {}).get(m) or {}
                for sec in ("receitas","despesas"):
                    for g,gd in (md.get(sec) or {}).items():
                        for c,cd in gd["cats"].items(): linha[c]+=cd["total"]
            bl=(C.get(key) or {}).setdefault(m,{})
            for c,v in linha.items():
                v=R2(v)
                if abs(R2(sum(x["v"] for x in bl.get(c,[])))-v)<=0.004: continue
                junto=[dict(x) for x in ((A.get(key) or {}).get(m) or {}).get(c,[])]+\
                      [dict(x) for x in ((T.get(key) or {}).get(m) or {}).get(c,[])]
                if abs(R2(sum(x["v"] for x in junto))-v)>0.004: continue
                bl[c]=junto; n+=1; ex.append((key,m,c,v))
    print("  %-12s listas do consolidado refeitas: %d"%(nome,n))
    for key,m,c,v in ex[:10]: print("        %-4s mes %-3s %-34s %12s"%(key,m,c[:34],format(v,",.2f")))
    open(ALVO,"w",encoding="utf-8").write(s[:j]+json.dumps(D,ensure_ascii=False)+s[end:])
