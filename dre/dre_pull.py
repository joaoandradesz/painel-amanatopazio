# -*- coding: utf-8 -*-
"""Baixa uma vez tudo o que a DRE precisa em 2026: titulos (os dois lados) e
   lancamentos avulsos de conta corrente. Guarda em dre_base_<emp>.json."""
import json,sys
sys.path.insert(0,'.')
from api import pages,call
for emp in ("amana","topazio"):
    T=[]
    for ep,raiz,met,sinal in (("financas/contareceber","conta_receber_cadastro","ListarContasReceber",1),
                              ("financas/contapagar","conta_pagar_cadastro","ListarContasPagar",-1)):
        for t in pages(emp,ep,met,{"filtrar_por_emissao_de":"01/01/2026","filtrar_por_emissao_ate":"31/12/2026"},raiz):
            if (t.get("status_titulo") or "").upper()=="CANCELADO": continue
            cs=t.get("categorias") or ([{"codigo_categoria":t.get("codigo_categoria"),"valor":t["valor_documento"]}] if t.get("codigo_categoria") else [])
            T.append({"cod":t["codigo_lancamento_omie"],"emi":t.get("data_emissao"),"sinal":sinal,
                      "cats":[[c["codigo_categoria"],round(abs(float(c.get("valor") or 0)),2)] for c in cs],
                      "obs":(t.get("observacao") or "")[:90],"cli":t.get("codigo_cliente_fornecedor"),
                      "val":float(t["valor_documento"])})
    A=[]
    for c in pages(emp,"geral/contacorrente","ListarContasCorrentes",{"apenas_importado_api":"N"},"ListarContasCorrentes"):
        if c.get("inativo")=="S": continue
        r=call(emp,"financas/extrato","ListarExtrato",{"nCodCC":c["nCodCC"],"dPeriodoInicial":"01/01/2026","dPeriodoFinal":"31/12/2026"})
        for x in r.get("listaMovimentos",[]):
            if (x.get("cOrigem") or "") not in ("Débito em Conta Corrente","Crédito em Conta Corrente"): continue
            cod=x.get("cCodCategoria") or ""; v=round(float(x.get("nValorDocumento") or 0),2)
            if not v or not cod or cod.startswith("0.01"): continue
            A.append({"data":x.get("dDataLancamento"),"cat":cod,"v":v,"conta":c["descricao"],
                      "obs":(x.get("cObservacoes") or "")[:70],"cli":(x.get("cDesCliente") or "")[:50]})
    json.dump({"titulos":T,"avulsos":A},open(f"dre_base_{emp}.json","w"),ensure_ascii=False)
    print(emp,"títulos",len(T),"| avulsos",len(A))
