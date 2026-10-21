# -*- coding: utf-8 -*-
"""O caixa do consolidado nao e soma simples de Amana + Topazio: ele elimina o
   intercompany (compra de diarias, adiantamento de reservas). Entao aqui nao da
   para refazer a linha a partir do detalhe como fiz nas duas empresas.
   O que da, e e seguro, e mover POR DIFERENCA nas categorias que eu reclassifiquei:
   se a soma das diferencas der zero, e so remanejamento e o total do mes nao muda."""
import json,sys,collections
R2=lambda v: round((v or 0)+0.0,2)
TOCADAS={"Prestadores OIA","Prestadores Diversos","Prestadores Recorrente - Gestão","Consultorias",
 "Serviços Extras - Op/Custos","Internet","Investimento Diversos","Pontuação e Premiação","Premiação",
 "Pontuação - Equipe e Diretoria","Premiação - equipe","Insumos para revenda","Insumos Frigobar (Revenda)",
 "Insumos itens para revenda","Transportes","Transportes SCS","Frete Custos Diretos",
 "Frete Manutenção Operacional","Frete marítimo*","Frete aéreo - pessoal","Serviços Extras","Serviços extras",
 "Insumos Café da Manhã","Insumos café da manhã","IR - Aplicação","IR -Aplicação",
 "Outras despesas administrativas","Outras despesas administrativas**"}
for ALVO in sys.argv[1:]:
    s=open(ALVO,encoding="utf-8").read(); i=s.index("const D=");j=s.index("{",i);dep=0
    for k in range(j,len(s)):
        if s[k]=="{":dep+=1
        elif s[k]=="}":
            dep-=1
            if dep==0: end=k+1;break
    D=json.loads(s[j:end]); nome=ALVO.split("/")[-1]
    onde=collections.Counter()
    for ent in D["entities"].values():
        for m,md in (ent.get("dfc") or {}).items():
            for sec in ("receitas","despesas"):
                for g,gd in (md.get(sec) or {}).items():
                    for c in gd["cats"]: onde[(c,sec,g)]+=1
    grupo={}
    for (c,sec,g),n in onde.most_common():
        if c not in grupo: grupo[c]=(sec,g)
    ent=D["entities"]["consol"]; ok=0; pul=0
    for m,md in (ent.get("dfc") or {}).items():
        if m in ("T","TT","T25"): continue
        txp=(ent.get("txp") or {}).get(m)
        if not txp: continue
        atual={}
        for sec in ("receitas","despesas"):
            for g,gd in (md.get(sec) or {}).items():
                for c,cd in gd["cats"].items():
                    if c in TOCADAS: atual[c]=cd["total"]
        alvo={c:R2(sum(x["v"] for x in itens)) for c,itens in txp.items() if c in TOCADAS}
        delta={c:R2(alvo.get(c,0)-atual.get(c,0)) for c in set(atual)|set(alvo)}
        delta={c:v for c,v in delta.items() if abs(v)>0.004}
        if not delta: continue
        if abs(R2(sum(delta.values())))>0.005:
            pul+=1; print("   pulado consol %-3s soma das diferencas %s (nao e so remanejamento)"%(m,R2(sum(delta.values())))); continue
        for c,v in delta.items():
            g=grupo.get(c)
            if not g: print("   sem grupo:",c); continue
            sec,gr=g
            md.setdefault(sec,{}).setdefault(gr,{"total":0.0,"cats":{}})
            cd=md[sec][gr]["cats"].setdefault(c,{"total":0.0})
            cd["total"]=R2(cd["total"]+v)
        for sec in ("receitas","despesas"):
            for gr in list(md.get(sec) or {}):
                md[sec][gr]["cats"]={c:cd for c,cd in md[sec][gr]["cats"].items() if abs(cd["total"])>0.004}
                md[sec][gr]["total"]=R2(sum(cd["total"] for cd in md[sec][gr]["cats"].values()))
                if not md[sec][gr]["cats"]: del md[sec][gr]
        ok+=1
    print("  %-12s consolidado: %d meses ajustados, %d pulados"%(nome,ok,pul))
    open(ALVO,"w",encoding="utf-8").write(s[:j]+json.dumps(D,ensure_ascii=False)+s[end:])
