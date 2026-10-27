# -*- coding: utf-8 -*-
"""Cria a categoria 'Hospedagem sem NFS-e' na Amana e move para ela o titulo da
   reserva 2082 (Aline Affonso, R$ 1.525,67, PIX de 31/08) -- hospedagem recebida
   sem nota emitida. Mesma linha de receita bruta no DRE (1.01.01), so que separada,
   para que 'Receita de Hospedagem' possa ser comparada direto com a relacao de
   faturamento da contabilidade.
   SEM retry: write que falha nao se repete em laco -- foi assim que a chave foi
   bloqueada por consumo indevido em 27/10."""
import api,json,sys,time
TIT=5299412371; VAL=1525.67
def um(ep,cn,p):                      # WRITE: uma tentativa so
    try: return api._call("amana",ep,cn,p)
    except Exception as e: print("  ERRO em %s: %s"%(cn,str(e)[:300])); sys.exit(1)
def le(ep,cn,p):                      # READ: pode repetir, o Omie pede espera
    try: return api.call("amana",ep,cn,p)
    except Exception as e: print("  ERRO em %s: %s"%(cn,str(e)[:300])); sys.exit(1)

cat=[c for c in le("geral/categorias/","ListarCategorias",{"pagina":1,"registros_por_pagina":500})
       .get("categoria_cadastro",[]) if c.get("descricao")=="Hospedagem sem NFS-e"]
if cat:
    cod=cat[0]["codigo"]; print("  categoria ja existe:",cod)
else:
    r=um("geral/categorias/","IncluirCategoria",
         {"descricao":"Hospedagem sem NFS-e","categoria_superior":"1.01","codigo_dre":"1.01.01"})
    print("  IncluirCategoria:",json.dumps(r,ensure_ascii=False)[:200])
    time.sleep(20)
    cat=[c for c in le("geral/categorias/","ListarCategorias",{"pagina":1,"registros_por_pagina":500})
           .get("categoria_cadastro",[]) if c.get("descricao")=="Hospedagem sem NFS-e"]
    if not cat: print("  a categoria nao apareceu na leitura; rode de novo em 1 minuto"); sys.exit(1)
    cod=cat[0]["codigo"]; print("  criada:",cod)

t=le("financas/contareceber/","ConsultarContaReceber",{"codigo_lancamento_omie":TIT})
assert abs(t["valor_documento"]-VAL)<0.01, "titulo nao e o esperado"
if t["codigo_categoria"]==cod:
    print("  titulo ja esta na categoria nova")
else:
    r=um("financas/contareceber/","AlterarContaReceber",
         {"codigo_lancamento_omie":TIT,"codigo_categoria":cod,
          "categorias":[{"codigo_categoria":cod,"percentual":100,"valor":VAL}]})
    print("  AlterarContaReceber:",json.dumps(r,ensure_ascii=False)[:200])
    time.sleep(40)
    t=le("financas/contareceber/","ConsultarContaReceber",{"codigo_lancamento_omie":TIT})
print("  conferido -> titulo %d | %s | %s | %.2f"%(TIT,t["data_emissao"],t["codigo_categoria"],t["valor_documento"]))
