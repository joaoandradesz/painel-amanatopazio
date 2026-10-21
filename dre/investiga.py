# -*- coding: utf-8 -*-
"""Caca os quatro apontamentos do Joao na base de titulos das duas empresas."""
import sys,json,unicodedata,re,collections
sys.path.insert(0,'.')
from api import call
def nz(s):
    s=unicodedata.normalize("NFKD",(s or "")).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+"," ",s).strip()
def tudo(emp,ep,cn,raiz):
    out=[];p=1
    while True:
        r=call(emp,ep,cn,{"pagina":p,"registros_por_pagina":500}); out+=r.get(raiz) or []
        if p>=int(r.get("total_de_paginas") or 1) or p>40: break
        p+=1
    return out
def clientes(emp):
    o={};p=1
    while True:
        r=call(emp,"geral/clientes","ListarClientesResumido",{"pagina":p,"registros_por_pagina":500})
        for c in r.get("clientes_cadastro_resumido") or []: o[c["codigo_cliente"]]=(c.get("razao_social") or c.get("nome_fantasia") or "").strip()
        if p>=int(r.get("total_de_paginas") or 1) or p>30: break
        p+=1
    return o
def cats(emp):
    o={};p=1
    while True:
        r=call(emp,"geral/categorias","ListarCategorias",{"pagina":p,"registros_por_pagina":100})
        for c in r.get("categoria_cadastro") or []: o[c.get("codigo")]=(c.get("descricao") or "").strip()
        if p>=int(r.get("total_de_paginas") or 1): break
        p+=1
    return o
BASE={}
for emp in ("amana","topazio"):
    NM=clientes(emp); CT=cats(emp)
    P=tudo(emp,"financas/contapagar","ListarContasPagar","conta_pagar_cadastro")
    R=tudo(emp,"financas/contareceber","ListarContasReceber","conta_receber_cadastro")
    BASE[emp]={"NM":NM,"CT":CT,"P":P,"R":R}
    print("%-8s %d a pagar | %d a receber"%(emp,len(P),len(R)))
json.dump({e:{"NM":{str(k):v for k,v in d["NM"].items()},"CT":d["CT"],
              "P":[{k:t.get(k) for k in ("codigo_lancamento_omie","data_emissao","data_vencimento","valor_documento","codigo_categoria","codigo_cliente_fornecedor","status_titulo","numero_parcela","categorias")} for t in d["P"]],
              "R":[{k:t.get(k) for k in ("codigo_lancamento_omie","data_emissao","data_vencimento","valor_documento","codigo_categoria","codigo_cliente_fornecedor","status_titulo","numero_parcela","categorias")} for t in d["R"]]}
           for e,d in BASE.items()},open("base_busca.json","w"),ensure_ascii=False)
print("gravado base_busca.json")
