# -*- coding: utf-8 -*-
"""Gerador do fluxo de caixa (DFC) por competencia de CAIXA, a partir do extrato
do Omie. Ate out/2026 o DFC do painel nao tinha gerador nenhum -- era um dado
publicado sem como refazer. Este script fecha esse buraco.

    MES=09/2026 python3 gera_dfc.py            # as duas empresas
    MES=09/2026 EMP=topazio python3 gera_dfc.py

Garantia dura: para cada conta do perimetro,
    saldo_anterior + soma dos movimentos == saldo_atual
Se uma conta nao fechar, o script aborta -- DFC so sai se o extrato fecha.

PERIMETRO (o que e "caixa"): tipos CC (corrente), CA (aplicacao), AC
(adquirente) e as contas CX listadas em CX_CAIXA. Ficam FORA: AD (adiantamento
de cliente), CR (cartao de credito) e as demais CX, que sao contas de controle
e nao dinheiro. A flag nao_fluxo do Omie NAO e usada: esta preenchida de forma
inconsistente entre as duas bases (Mercado Pago da Amana marcado S, Conta
transitoria da Topazio marcada S, Encontro de Contas marcada N).

Transferencia entre duas contas do perimetro se anula sozinha e e descartada;
transferencia para fora do perimetro e caixa de verdade e fica.
"""
import os,sys,json,re,time,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from api import call as _call

MES=os.environ.get("MES","09/2026")
EMPS=[os.environ["EMP"]] if os.environ.get("EMP") else ["amana","topazio"]
CX_CAIXA={"Caixinha","Caixinha - Financeiro"}          # CX que e dinheiro mesmo
# o extrato mistura movimento REALIZADO com PREVISTO. Previsto nao e caixa:
# na GetNet da Amana sao 30 lancamentos e R$ 277 mil que nunca entraram no mes.
REALIZADO={"Conta Paga","Conta Recebida","Débito de Transferência","Crédito de Transferência",
           "Débito em Conta Corrente","Crédito em Conta Corrente"}
TIPO_CAIXA={"CC","CA","AC"}
R2=lambda v: round((v or 0)+0.0,2)

def call(emp,ep,cn,par,tent=6):
    for i in range(tent):
        try: return _call(emp,ep,cn,par)
        except Exception:
            if i==tent-1: raise
            time.sleep(5+5*i)

def primeiro_ultimo(mes):
    m,a=mes.split("/"); import calendar
    return "01/%s/%s"%(m,a), "%02d/%s/%s"%(calendar.monthrange(int(a),int(m))[1],m,a)

RAT=re.compile(r'^\s*(.+?)\s*\((\d+),(\d+)%\)\s*$')
def pernas(desc,valor):
    """abre 'A (30,030950%); B (69,969050%)' em [(nome, valor), ...]"""
    partes=[p for p in (desc or "").split(";") if p.strip()]
    saida=[];soma=0.0
    if len(partes)<2: return [((desc or "?").strip(),R2(valor))]
    for p in partes:
        m=RAT.match(p)
        if not m: return [((desc or "?").strip(),R2(valor))]   # formato inesperado: nao abre
        pct=float("%s.%s"%(m.group(2),m.group(3)))/100.0
        v=R2(valor*pct); soma+=v; saida.append((m.group(1).strip(),v))
    saida[-1]=(saida[-1][0],R2(saida[-1][1]+(R2(valor)-R2(soma))))   # centavo de fechamento
    return saida

def roda(emp,mes):
    DE,ATE=primeiro_ultimo(mes)
    cc=call(emp,"geral/contacorrente","ListarContasCorrentes",{"pagina":1,"registros_por_pagina":100})
    contas={}
    for x in (cc.get("ListarContasCorrentes") or []):
        if (x.get("inativo") or "")=="S": continue
        t=x.get("tipo_conta_corrente"); n=(x.get("descricao") or "").strip()
        if t in TIPO_CAIXA or (t=="CX" and n in CX_CAIXA): contas[x["nCodCC"]]={"nome":n,"tipo":t}
    cat={};p=1
    while True:
        r=call(emp,"geral/categorias","ListarCategorias",{"pagina":p,"registros_por_pagina":500})
        for c in (r.get("categoria_cadastro") or []):
            dd=c.get("dadosDRE") or {}
            cat[(c.get("descricao") or "").strip()]={"cod":c.get("codigo"),
                "dre":dd.get("codigoDRE"),"grupo":(dd.get("descricaoDRE") or "").strip()}
        if p>=int(r.get("total_de_paginas") or 1): break
        p+=1
    mov=[];saldos=[];falhas=[]
    for cod,meta in contas.items():
        r=call(emp,"financas/extrato","ListarExtrato",{"nCodCC":cod,"dPeriodoInicial":DE,"dPeriodoFinal":ATE})
        L=[x for x in (r.get("listaMovimentos") or [])
           if (x.get("cOrigem") in REALIZADO) and not (x.get("cDesCliente") or "").startswith("SALDO")]
        ant=R2(r.get("nSaldoAnterior")); atu=R2(r.get("nSaldoAtual"))
        soma=R2(sum(x.get("nValorDocumento") or 0 for x in L))
        if abs(R2(ant+soma)-atu)>0.01: falhas.append((cod,meta["nome"],ant,soma,atu))
        saldos.append({"cc":cod,"nome":meta["nome"],"tipo":meta["tipo"],"ini":ant,"mov":soma,"fim":atu})
        for x in L: x["_cc"]=cod; mov.append(x)
    if falhas:
        print("ABORTADO -- conta(s) que nao fecham no extrato:")
        for cod,n,a,s,f in falhas: print("   %s %-30s %12.2f + %12.2f != %12.2f"%(cod,n,a,s,f))
        sys.exit(1)
    dentro={x.get("nCodLancamento") for x in mov}
    linhas=[]
    for x in mov:
        c=(x.get("cCodCategoria") or "")
        if c.startswith("0.") and x.get("nCodLancRelac") in dentro: continue   # transferencia interna
        for nome,v in pernas(x.get("cDesCategoria"),x.get("nValorDocumento") or 0):
            g=cat.get(nome) or {}
            linhas.append({"d":x.get("dDataLancamento"),"cc":x.get("_cc"),"cat":nome,
                "cod":g.get("cod"),"grupo":g.get("grupo") or "(sem DRE)","dre":g.get("dre"),
                "v":v,"nome":(x.get("cRazCliente") or x.get("cDesCliente") or "").strip(),
                "incl":x.get("cDataInclusao"),"id":x.get("nCodLancamento")})
    return {"mes":mes,"contas":saldos,"linhas":linhas,
            "total":R2(sum(l["v"] for l in linhas)),
            "mov_saldo":R2(sum(s["mov"] for s in saldos))}

out={}
for emp in EMPS:
    d=roda(emp,MES); out[emp]=d
    print("\n===== %s — DFC %s"%(emp.upper(),MES))
    print("   %-34s %13s %13s %13s"%("conta","saldo inicial","movimento","saldo final"))
    for s in sorted(d["contas"],key=lambda s:-abs(s["mov"])):
        print("   %-34s %13.2f %13.2f %13.2f"%(s["nome"][:34],s["ini"],s["mov"],s["fim"]))
    print("   %-34s %13.2f %13.2f %13.2f"%("TOTAL",R2(sum(s["ini"] for s in d["contas"])),
          d["mov_saldo"],R2(sum(s["fim"] for s in d["contas"]))))
    print("   todas as contas fecham no extrato (inicial + movimento = final)")
    g=collections.defaultdict(float)
    for l in d["linhas"]: g[l["grupo"]]+=l["v"]
    print("\n   %-44s %13s"%("grupo da DRE","caixa do mes"))
    for k in sorted(g,key=lambda k:-abs(g[k])):
        print("   %-44s %13.2f"%(k[:44],R2(g[k])))
    print("   %-44s %13.2f   <- DFC"%("TOTAL",d["total"]))
    print("   %-44s %13.2f   <- movimento dos saldos"%("",d["mov_saldo"]))
    print("   %-44s %13.2f   <- transferencias internas eliminadas"%("",R2(d["mov_saldo"]-d["total"])))
json.dump(out,open(os.environ.get("SAIDA","dfc_%s.json"%MES.replace("/","")),"w"),ensure_ascii=False)
