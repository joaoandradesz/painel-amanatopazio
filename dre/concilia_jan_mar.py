# -*- coding: utf-8 -*-
"""Retrato da conciliacao de jan a mar/2026 nas duas empresas, conta por conta.
   E o que a contabilidade ve quando reimporta o movimento do Omie."""
import sys,json,collections
sys.path.insert(0,'.')
from api import call
CC={"amana":[(5174110361,"NF a identificar / pedido"),(5177543696,"Bradesco"),(5177546899,"Santander"),
      (5177550204,"InfinitePay"),(5186771952,"Mercado Pago"),(5196586286,"Santander - Aplicação"),
      (5196707350,"Bradesco - Invest Fácil"),(5199925490,"Santander - CDB DI PJ"),(5212185049,"Adiantamento de Cliente"),
      (5212188724,"GetNet"),(5226179398,"Bradesco - CDB DI PJ"),(5233749189,"Visa - cartão Bradesco"),
      (5233749730,"MasterCard - cartão Santander"),(5262394107,"Notas pagas pelo sócio PF"),(5272112673,"Transitória"),
      (5273930737,"Bonificações/Doações"),(5284310859,"Encontro de contas - adiantamentos"),(5291963746,"Bradesco - CDB")],
    "topazio":[(3006666402,"Caixinha"),(3016781127,"Santander conta corrente"),(3057055408,"Santander ContaMax"),
      (3076514932,"GetNet"),(3093135669,"Caixinha - Financeiro"),(3098287243,"Visa - cartão Bradesco"),
      (3102144859,"NF a identificar"),(3107193040,"Conta transitória"),(3107225344,"MasterCard - cartão Santander"),
      (3123816847,"Bonificações/Doações")]}
MESES=[("01/01/2026","31/01/2026","jan"),("01/02/2026","28/02/2026","fev"),("01/03/2026","31/03/2026","mar")]
out={}
for emp,contas in CC.items():
    print("="*4,emp.upper())
    tot=collections.Counter(); det=collections.defaultdict(list)
    for cod,nome in contas:
        linha={}
        for de,ate,m in MESES:
            r=call(emp,"financas/extrato","ListarExtrato",{"nCodCC":cod,"dPeriodoInicial":de,"dPeriodoFinal":ate})
            mv=[x for x in (r.get("listaMovimentos") or []) if not (x.get("cDesCliente") or "").startswith("SALDO")]
            c=collections.Counter(); v=collections.Counter()
            for x in mv:
                s=(x.get("cSituacao") or "sem situacao"); c[s]+=1; v[s]+=x.get("nValorDocumento") or 0
                if s!="Conciliado":
                    det[(nome,s)].append((m,x.get("dDataLancamento"),round(x.get("nValorDocumento") or 0,2),
                                          (x.get("cOrigem") or "")[:30],(x.get("cRazCliente") or x.get("cDesCliente") or "")[:28]))
            linha[m]=(c,v); 
            for s,n in c.items(): tot[s]+=n
        nc=sum(n for m,(c,v) in linha.items() for s,n in c.items() if s!="Conciliado")
        n=sum(n for m,(c,v) in linha.items() for s,n in c.items())
        if n: print("  %-34s %4d movimentos | %4d fora de conciliado"%(nome,n,nc))
    print("  TOTAL por situacao:",dict(tot))
    out[emp]={"det":{str(k):v for k,v in det.items()},"tot":dict(tot)}
json.dump(out,open("concilia_jan_mar.json","w"),ensure_ascii=False)
print("gravado concilia_jan_mar.json")
