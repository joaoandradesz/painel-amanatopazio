# -*- coding: utf-8 -*-
"""Puxa tudo de setembro/2026 das duas empresas para montar a DRE:
titulos por data de EMISSAO (com rateio aberto), avulsos de conta corrente,
e o cadastro de categorias com dadosDRE."""
import sys,json,collections,datetime,os; sys.path.insert(0,'.')
from api import call
R2=lambda v: round((v or 0)+0.0,2)
MES="09/2026"
CC={"amana":[5174110361,5177543696,5177546899,5177550204,5186771952,5196586286,5196707350,5199925490,
             5212185049,5212188724,5226179398,5233749189,5233749730,5262394107,5272112673,5273930737,
             5284310859,5291963746],
    "topazio":[3006666402,3016781127,3057055408,3076514932,3093135669,3098287243,3102144859,3107193040,
               3107225344,3123816847]}
out={}
for emp in ("amana","topazio"):
    cli={};p=1
    while True:
        r=call(emp,"geral/clientes","ListarClientesResumido",{"pagina":p,"registros_por_pagina":500})
        for c in r.get("clientes_cadastro_resumido") or []:
            cli[c["codigo_cliente"]]=(c.get("razao_social") or c.get("nome_fantasia") or "—").strip()
        if p>=int(r.get("total_de_paginas") or 1) or p>30: break
        p+=1
    cat={};p=1
    while True:
        r=call(emp,"geral/categorias","ListarCategorias",{"pagina":p,"registros_por_pagina":100})
        for c in r.get("categoria_cadastro") or []:
            dd=c.get("dadosDRE") or {}
            cat[c.get("codigo")]={"desc":(c.get("descricao") or "").strip(),"dre":dd.get("codigoDRE"),
                                  "dre_desc":dd.get("descricaoDRE"),"tem_dre":bool(dd.get("codigoDRE"))}
        if p>=int(r.get("total_de_paginas") or 1): break
        p+=1
    itens=[]
    for lado,ep,cn,raiz,consulta,sg in (
        ("receber","financas/contareceber","ListarContasReceber","conta_receber_cadastro","ConsultarContaReceber",1),
        ("pagar","financas/contapagar","ListarContasPagar","conta_pagar_cadastro","ConsultarContaPagar",-1)):
        T=[];p=1
        while True:
            r=call(emp,ep,cn,{"pagina":p,"registros_por_pagina":500}); T+=r.get(raiz) or []
            if p>=int(r.get("total_de_paginas") or 1) or p>40: break
            p+=1
        for t in T:
            em=(t.get("data_emissao") or "")
            if len(em)!=10 or em[3:]!=MES: continue
            if (t.get("status_titulo") or "").upper()=="CANCELADO": continue
            pernas=t.get("categorias") or []
            if not pernas:
                pernas=[{"codigo_categoria":t.get("codigo_categoria"),"valor":t.get("valor_documento")}]
            for x in pernas:
                itens.append({"id":t.get("codigo_lancamento_omie"),"lado":lado,"em":em,
                    "venc":t.get("data_vencimento"),"cat":x.get("codigo_categoria"),
                    "v":R2(sg*(x.get("valor") or 0)),
                    "nome":cli.get(t.get("codigo_cliente_fornecedor"),"—"),
                    "nf":(t.get("numero_documento_fiscal") or t.get("numero_documento") or "").strip(),
                    "st":(t.get("status_titulo") or "").title()})
    avulsos=[]
    for cod in CC[emp]:
        r=call(emp,"financas/extrato","ListarExtrato",{"nCodCC":cod,"dPeriodoInicial":"01/09/2026","dPeriodoFinal":"30/09/2026"})
        for x in (r.get("listaMovimentos") or []):
            o=(x.get("cOrigem") or "")
            if o not in ("Débito em Conta Corrente","Crédito em Conta Corrente"): continue
            if (x.get("cDesCliente") or "").startswith("SALDO"): continue
            avulsos.append({"id":x.get("nCodLancamento"),"lado":"avulso","em":x.get("dDataLancamento"),
                "venc":x.get("dDataLancamento"),"cat":x.get("cCodCategoria"),
                "v":R2(x.get("nValorDocumento")),"nome":(x.get("cRazCliente") or x.get("cDesCliente") or "—").strip(),
                "nf":"","st":x.get("cSituacao") or ""})
    out[emp]={"clientes":len(cli),"categorias":cat,"itens":itens,"avulsos":avulsos}
    print("%-8s %4d pernas de titulo (emissao 09/2026) | %3d avulsos | %d categorias"%(
        emp,len(itens),len(avulsos),len(cat)))
json.dump(out,open(os.environ.get("SAIDA","set.json"),"w"),ensure_ascii=False)
