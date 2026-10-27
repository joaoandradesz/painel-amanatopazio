# -*- coding: utf-8 -*-
"""Prova, direto do git, as 12 NFS-e de setembro/2026 que estavam presas em
"Adiantamento de Hospedagem" (conta de controle, fora da DRE) sem nenhuma perna
de receita -- e a NFS-e 225, que ia no sentido contrario (adiantamento lancado
NA receita, duplicando o faturamento).

Regra que identifica uma nota presa: esta na relacao de faturamento da
contabilidade (nfse_set.json, 68 notas), tem titulo no Omie, e a soma das pernas
1.01.* e zero.

Roda em qualquer maquina com o repositorio:  python3 prova_adiantamento.py
Falha (exit 1) se a conta deixar de fechar.
"""
import json,subprocess,collections,sys
ANTES,DEPOIS="4421fd4","227dc65"   # 21/10 10:14  ->  22/10 17:37
pull=lambda c: json.loads(subprocess.run(["git","show","%s:dre/set.json"%c],
    capture_output=True,text=True,cwd="..").stdout)
A,B=pull(ANTES),pull(DEPOIS)
nfse={n["nfse"] for n in json.load(open("nfse_set.json"))}   # 68 notas da contabilidade
def rec(d,nf):
    """soma das pernas de RECEITA (1.01.*) e de CONTROLE (1.04.01) da nota"""
    r=c=0.0
    for it in d["amana"]["itens"]:
        if (it.get("nf") or "").strip()!=nf or it["lado"]!="receber": continue
        if it["cat"].startswith("1.01."): r+=it["v"]
        elif it["cat"]=="1.04.01": c+=it["v"]
    return round(r,2),round(c,2)
presas=[]
for nf in sorted(nfse,key=lambda x:int(x) if x.isdigit() else 0):
    ra,ca=rec(A,nf); rb,_=rec(B,nf)
    if ra==0 and ca>0: presas.append((nf,ca,rb))
soma=round(sum(p[1] for p in presas),2)
print("%d NFS-e sem nenhuma perna de receita antes da correcao: %.2f"%(len(presas),soma))
for nf,ca,rb in presas: print("   NFS-e %-4s controle %10.2f -> receita %10.2f"%(nf,ca,rb))
d225=round(rec(A,"225")[0]-rec(B,"225")[0],2)
print("NFS-e 225 (adiantamento lancado na receita, duplicando): %+.2f"%-d225)
tot=lambda d: round(sum(i["v"] for i in d["amana"]["itens"]
                        if i["cat"]=="1.01.02" and i["lado"]=="receber"),2)
ta,tb=tot(A),tot(B)
print("\nReceita de Hospedagem setembro: %.2f -> %.2f (%+.2f)"%(ta,tb,round(tb-ta,2)))
ok=[]
ok.append(("12 notas presas",len(presas)==12))
ok.append(("somam 84.424,60",soma==84424.60))
ok.append(("225 devolve 9.849,97",d225==9849.97))
ok.append(("delta publicado 74.574,63",round(tb-ta,2)==round(soma-d225,2)==74574.63))
ok.append(("615.309,57 - 20.291,35 = 595.018,22 (contabilidade)",round(tb-20291.35,2)==595018.22))
print()
for rot,v in ok: print("  %s %s"%("OK  " if v else "FALHA",rot))
sys.exit(0 if all(v for _,v in ok) else 1)
