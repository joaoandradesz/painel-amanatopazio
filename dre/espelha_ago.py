# -*- coding: utf-8 -*-
"""Espelha no painel as reclassificacoes feitas no Omie (Topazio, agosto):
   Prestadores Recorrente vira OIA/Diversos dentro de 'Prestacao de servicos
   operacionais' (custo direto) e a Internet do Mauro vai para Investimentos.
   EBITDA sobe 5.560,00 em agosto; o resultado final nao muda, porque o que sai
   de despesa entra como investimento logo abaixo."""
import json,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
SERV="06. Prestação de serviços operacionais"
for ALVO in sys.argv[1:]:
    s=open(ALVO,encoding="utf-8").read()
    i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: end=k+1;break
    D=json.loads(s[j:end]); nome=ALVO.split("/")[-1]; rel=collections.defaultdict(float)
    for en in ("topazio","consol"):
        arv=(D["entities"][en].get("dre") or {}).get("8")
        if not arv: continue
        for t in list(arv):
            for g in list(arv[t]):
                for co in list(arv[t][g]):
                    fica=[]
                    for x in arv[t][g][co]:
                        c=x["cat"]
                        if c=="Prestadores Recorrente - Gestão":
                            # 900 do Maximillian viram OIA; 10.550 viram Prestadores Diversos
                            arv[t]["21. Custos"]=arv[t].get("21. Custos",{})
                            d=arv[t]["21. Custos"].setdefault(SERV,[])
                            for nc,v in (("Prestadores OIA",-900.0),("Prestadores Diversos",R2(x["v"]+900.0))):
                                if abs(v)<0.005: continue
                                ex=next((y for y in d if y["cat"]==nc),None)
                                if ex: ex["v"]=R2(ex["v"]+v)
                                else: d.append({"cat":nc,"v":R2(v)})
                            rel["prestadores "+en]+=x["v"]
                        elif c=="Internet" and en in ("topazio","consol") and abs(x["v"]+5560.0)<0.01:
                            inv=arv.setdefault("3. Investimentos",{}).setdefault("31. Investimentos",{}).setdefault("01. Investimentos",[])
                            ex=next((y for y in inv if y["cat"]=="Investimento Diversos"),None)
                            if ex: ex["v"]=R2(ex["v"]+x["v"])
                            else: inv.append({"cat":"Investimento Diversos","v":R2(x["v"])})
                            rel["internet "+en]+=x["v"]
                        else: fica.append(x)
                    arv[t][g][co]=fica
                    if not fica: del arv[t][g][co]
                if not arv[t][g]: del arv[t][g]
    print("  %-12s %s"%(nome," | ".join("%s %s"%(k,format(R2(v),",.2f")) for k,v in sorted(rel.items()))))
    open(ALVO,"w",encoding="utf-8").write(s[:j]+json.dumps(D,ensure_ascii=False)+s[end:])
