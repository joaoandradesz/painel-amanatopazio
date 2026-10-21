# -*- coding: utf-8 -*-
"""A arvore da DRE do consolidado levou meu ajuste duas vezes nas categorias que
   reclassifiquei em agosto -- uma pelo script que espelhou o Omie e outra pelo que
   arrumou o detalhe. Aqui a linha dessas categorias volta a ser exatamente a soma
   do detalhe do proprio consolidado, movendo por diferenca para o total nao mudar."""
import json,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
TOCADAS={"Prestadores OIA","Prestadores Diversos","Prestadores Recorrente - Gestão","Consultorias",
 "Serviços Extras - Op/Custos","Internet","Investimento Diversos","Pontuação e Premiação",
 "Insumos para revenda","Transportes","Frete Custos Diretos"}
for ALVO in sys.argv[1:]:
    s=open(ALVO,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: end=k+1;break
    D=json.loads(s[j:end]); nome=ALVO.split("/")[-1]; ok=pul=0
    ent=D["entities"]["consol"]
    for m,arv in (ent.get("dre") or {}).items():
        if m in ("T","TT","T25"): continue
        tx=(ent.get("tx") or {}).get(m)
        if not tx: continue
        alvo={c:R2(sum(x["v"] for x in itens)) for c,itens in tx.items() if c in TOCADAS}
        atual=collections.defaultdict(float); onde={}
        for t in arv:
            for g in arv[t]:
                for co in arv[t][g]:
                    for x in arv[t][g][co]:
                        if x["cat"] in TOCADAS: atual[x["cat"]]+=x["v"]; onde.setdefault(x["cat"],(t,g,co))
        delta={c:R2(alvo.get(c,0)-atual.get(c,0)) for c in set(atual)|set(alvo)}
        delta={c:v for c,v in delta.items() if abs(v)>0.004}
        if not delta: continue
        if abs(R2(sum(delta.values())))>0.005:
            pul+=1; print("   pulado %-3s soma das diferencas %s"%(m,R2(sum(delta.values())))); continue
        for c,v in delta.items():
            loc=onde.get(c)
            if not loc:
                irm=next((o for cc,o in onde.items()),None)
                if not irm: continue
                loc=irm
            t,g,co=loc
            linha=next((x for x in arv[t][g][co] if x["cat"]==c),None)
            if linha: linha["v"]=R2(linha["v"]+v)
            else: arv[t][g][co].append({"cat":c,"v":v})
        for t in list(arv):
            for g in list(arv[t]):
                for co in list(arv[t][g]):
                    arv[t][g][co]=[x for x in arv[t][g][co] if abs(x["v"])>0.004]
                    if not arv[t][g][co]: del arv[t][g][co]
                if not arv[t][g]: del arv[t][g]
        ok+=1
    print("  %-12s DRE do consolidado: %d meses ajustados, %d pulados"%(nome,ok,pul))
    open(ALVO,"w",encoding="utf-8").write(s[:j]+json.dumps(D,ensure_ascii=False)+s[end:])
