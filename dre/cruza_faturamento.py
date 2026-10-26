# -*- coding: utf-8 -*-
"""Cruza a relacao de faturamento da contabilidade (NFS-e) com os titulos do Omie,
nota a nota, agosto e setembro/2026 da Amana.
So entram as pernas de RECEITA (1.01.*); 1.04.01 'Adiantamento de Hospedagem' e conta
de controle e fica fora da DRE -- e justamente a perna que escondia receita em setembro."""
import os,json,collections
S=os.environ["S"]
REC=lambda c: (c or "").startswith("1.01.")
ORF={"70":7831.96,"112":9799.53,"117":12316.72,"126":16349.89,"127":16558.44,"139":12466.99}
ag=json.load(open(os.path.join(S,'ago_contab.json')))
st=json.load(open(os.path.join(S,'set_contab.json')))
L=json.load(open('rec_amana_atual.json'))
g=collections.defaultdict(list); adi=collections.defaultdict(float)
for t in L:
    if not t['nf'] or (t['st'] or '').upper()=='CANCELADO': continue
    for x in (t['cats'] or [{'c':t['cat'],'v':t['v']}]):
        v=round(x['v'] or 0,2)
        if REC(x['c']): g[t['nf']].append({'em':t['em'],'v':v,'cod':t['cod'],'cat':x['c'],'cli':t['cli'],'st':t['st']})
        elif x['c']=='1.04.01': adi[t['nf']]+=v
for n,v in ORF.items():
    if n not in ag: ag[n]={'sit':'Autorizada','cli':(g[n][0]['cli'] if g.get(n) else '—'),'val':v}
def md(ts):
    d=collections.defaultdict(float)
    for t in ts: d[t['em'][3:]]=round(d[t['em'][3:]]+t['v'],2)
    return dict(sorted(d.items(),key=lambda kv:(kv[0][3:],kv[0][:2])))
R={}
for rot,contab in (("08/2026",ag),("09/2026",st)):
    ln=[]
    for n in sorted(contab,key=int):
        c=contab[n]; ts=g.get(n,[]); o=round(sum(t['v'] for t in ts),2); m=md(ts)
        nm=round(m.get(rot,0.0),2)
        ln.append({"nf":n,"cli":(c['cli'] or (ts[0]['cli'] if ts else '—')),"contab":c['val'],"omie":o,
            "no_mes":nm,"fora":round(o-nm,2),"dif":round(o-c['val'],2),
            "meses":"; ".join(f"{k}: {v:,.2f}" for k,v in m.items()) or "sem titulo de receita",
            "topazio":c.get('topazio',0.0),"adiant":round(adi.get(n,0.0),2),"npar":len(ts)})
    R[rot]=ln
json.dump(R,open(os.path.join(S,'cruzamento.json'),'w'),ensure_ascii=False)
for rot,ln in R.items():
    print(f"\n===== {rot}  ({len(ln)} notas na relacao da contabilidade)")
    print(f"  contabilidade ........................ {sum(x['contab'] for x in ln):>14,.2f}")
    print(f"  Omie, receita das mesmas notas ....... {sum(x['omie'] for x in ln):>14,.2f}")
    print(f"     dentro do proprio mes ............. {sum(x['no_mes'] for x in ln):>14,.2f}")
    print(f"     em outro mes ...................... {sum(x['fora'] for x in ln):>14,.2f}")
    bad=[x for x in ln if abs(x['dif'])>0.05 or abs(x['fora'])>0.05]
    print(f"  notas com pendencia: {len(bad)}")
    for x in bad:
        print(f"    NF {x['nf']:>4} {x['cli'][:36]:<36} contab {x['contab']:>11,.2f} | Omie {x['omie']:>11,.2f} dif {x['dif']:>10,.2f} | {x['meses']}")
