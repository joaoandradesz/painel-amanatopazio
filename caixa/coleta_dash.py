# -*- coding: utf-8 -*-
"""Coleta do dashboard de caixa: saldo por conta, titulos em aberto dos
proximos 15 dias e cobertura, para Amana, Topazio e consolidado."""
import sys,os,json,datetime,collections
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from omie_api import call
R2=lambda v: round((v or 0)+0.0,2)
dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()

# ancora 31/10/2026 = saldo final de outubro do DFC publicado, que fecha com o documento
# de cada conta (OFX da conta corrente; extrato de investimento no LIQUIDO: CDB Santander
# 318.184,84, CDB Bradesco 79.465,25, Invest Facil 9.878,17, ContaMax 208.986,17).
# Caixinhas da Topazio sem documento: saldo do Omie em 31/10.
ANCORA_DATA=datetime.date(2026,10,31)
EMP={
 "amana":{"nome":"Amana","ancora":{
    "Bradesco conta corrente":1.00,"Santander conta corrente":0.00,"InfinitePay":23366.03,
    "Mercado Pago":256.46,"Santander ContaMax":208986.17,"Bradesco Invest Fácil":9878.17,
    "Santander CDB DI PJ":318184.84,"Bradesco CDB DI PJ":79465.25,"GetNet":0.00},
  "contas":[(5177546899,"Santander conta corrente"),(5196586286,"Santander ContaMax"),
    (5199925490,"Santander CDB DI PJ"),(5177543696,"Bradesco conta corrente"),
    (5196707350,"Bradesco Invest Fácil"),(5226179398,"Bradesco CDB DI PJ"),
    (5177550204,"InfinitePay"),(5186771952,"Mercado Pago"),(5212188724,"GetNet")],
  "getnet":5212188724},
 "topazio":{"nome":"Topázio","ancora":{
    "Santander conta corrente":0.00,"Santander ContaMax":1357.80,"GetNet":0.00,
    "Caixinha":154.00,"Caixinha Financeiro":0.00},
  "contas":[(3016781127,"Santander conta corrente"),(3057055408,"Santander ContaMax"),
    (3076514932,"GetNet"),(3006666402,"Caixinha"),(3093135669,"Caixinha Financeiro")],
  "getnet":3076514932}}

def nomes(emp):
    o={};p=1
    while True:
        r=call(emp,"geral/clientes","ListarClientesResumido",{"pagina":p,"registros_por_pagina":500})
        for c in r.get("clientes_cadastro_resumido") or []:
            o[c["codigo_cliente"]]=(c.get("razao_social") or c.get("nome_fantasia") or "—").strip()
        if p>=int(r.get("total_de_paginas") or 1) or p>30: break
        p+=1
    return o
def cats(emp):
    o={};p=1
    while True:
        r=call(emp,"geral/categorias","ListarCategorias",{"pagina":p,"registros_por_pagina":100})
        for c in r.get("categoria_cadastro") or []: o[c.get("codigo")]=c.get("descricao")
        if p>=int(r.get("total_de_paginas") or 1): break
        p+=1
    return o
def titulos(emp,ep,cn,raiz):
    out=[];p=1
    while True:
        r=call(emp,ep,cn,{"pagina":p,"registros_por_pagina":500})
        out+=r.get(raiz) or []
        if p>=int(r.get("total_de_paginas") or 1) or p>40: break
        p+=1
    return out

HORIZONTE=90   # dias de titulos carregados; a tela filtra dentro disso

def agenda_getnet(emp,cc,HOJE,FIM,itens):
    """Previsto da GetNet que NAO e titulo: 'Previsao de Reservas' e parcela de
    'Adiantamento de Venda' sem titulo a receber. Em 27/11/2026 eram R$ 176.872,42
    de previsao de reservas e 20 parcelas de adiantamento fora da tela: o painel so
    lia titulo. 'Conta a Receber'/'Conta a Pagar' ja vem como titulo; o resto casa
    com titulo por valor e data proxima e so entra o que sobra."""
    g=call(emp,"financas/extrato","ListarExtrato",
           {"nCodCC":cc,"dPeriodoInicial":HOJE.strftime("%d/%m/%Y"),"dPeriodoFinal":FIM.strftime("%d/%m/%Y")})
    # a parcela da GetNet cai no dia util seguinte ao vencimento do titulo
    # (titulo no domingo 13/12, agenda na segunda 14/12): casa por valor com ate
    # 4 dias de folga, e cada titulo casa uma vez so
    tit=[[dt(i["d"]),round(i["v"],2)] for i in itens if i["lado"]=="receber"]
    out=[]
    for x in g.get("listaMovimentos") or []:
        v=x.get("nValorDocumento") or 0
        if x.get("cSituacao")!="Previsto" or v<=0 or x.get("cOrigem") in ("Conta a Receber","Conta a Pagar"): continue
        d=dt(x.get("dDataLancamento"))
        par=next((t for t in tit if abs(t[1]-v)<=0.02 and abs((t[0]-d).days)<=4),None)
        if par: tit.remove(par); continue
        out.append({"lado":"receber","d":x.get("dDataLancamento"),"nome":x.get("cDesCliente") or "—",
                    "cat":x.get("cDesCategoria") or "—","v":R2(v),"conta":"GetNet","doc":"",
                    "st":"Previsto","fonte":"agenda","origem":x.get("cOrigem")})
    return out

def coleta(HOJE):
    FIM=HOJE+datetime.timedelta(days=HORIZONTE)
    # CORTE_SALDO=dd/mm/aaaa: saldo ate o ultimo dia com a varredura lancada
    # (26/11/2026: novembro sem os resgates da ContaMax). Titulos seguem de HOJE.
    _c=os.environ.get("CORTE_SALDO")
    CORTE=min(HOJE,datetime.datetime.strptime(_c,"%d/%m/%Y").date()) if _c else HOJE
    out={"corte":CORTE.strftime("%d/%m/%Y") if CORTE<HOJE else None,"hoje":HOJE.strftime("%d/%m/%Y"),"fim":FIM.strftime("%d/%m/%Y"),"horizonte":HORIZONTE,
         "ancora":ANCORA_DATA.strftime("%d/%m/%Y"),
         "gerado":datetime.datetime.now().strftime("%d/%m/%Y às %H:%M"),"ents":{}}
    for emp,cfg in EMP.items():
        NM=nomes(emp); CT=cats(emp)
        contas=[]
        for cod,nome in cfg["contas"]:
            r=call(emp,"financas/extrato","ListarExtrato",
                   {"nCodCC":cod,"dPeriodoInicial":(ANCORA_DATA+datetime.timedelta(days=1)).strftime("%d/%m/%Y"),
                    "dPeriodoFinal":CORTE.strftime("%d/%m/%Y")})
            L=[x for x in (r.get("listaMovimentos") or []) if not (x.get("cDesCliente") or "").startswith("SALDO")]
            sit=lambda x:(x.get("cSituacao") or "")
            mv=sum(x.get("nValorDocumento") or 0 for x in L if sit(x)=="Conciliado")
            # "Previsto" e projecao de titulo futuro dentro da conta, nao movimento
            # pendente de conciliacao: contar os dois juntos inflava o alerta.
            nc=sum(1 for x in L if sit(x)=="Não conciliado")
            pv=sum(1 for x in L if sit(x)=="Previsto")
            a=cfg["ancora"].get(nome,0.0)
            contas.append({"n":nome,"ini":R2(a),"mov":R2(mv),"hoje":R2(a+mv),"naoconc":nc,"previsto":pv})
        itens=[];atr=[];desfecho={}
        for lado,ep,cn,raiz in (("receber","financas/contareceber","ListarContasReceber","conta_receber_cadastro"),
                                ("pagar","financas/contapagar","ListarContasPagar","conta_pagar_cadastro")):
            for t in titulos(emp,ep,cn,raiz):
                v=t.get("data_vencimento") or ""
                if len(v)!=10: continue
                try: d=dt(v)
                except Exception: continue
                st=(t.get("status_titulo") or "").upper()
                if st in ("PAGO","RECEBIDO","CANCELADO"):
                    # guardamos o desfecho para o de-para previsto x realizado
                    desfecho[t.get("codigo_lancamento_omie")]={"st":st.title(),"v":R2(t.get("valor_documento")),"d":v,
                        "nome":NM.get(t.get("codigo_cliente_fornecedor"),"—"),"lado":lado}
                    continue
                reg={"id":t.get("codigo_lancamento_omie"),"lado":lado,"d":v,
                     "nome":NM.get(t.get("codigo_cliente_fornecedor"),"—"),
                     "cat":CT.get(t.get("codigo_categoria")) or ("rateio" if not t.get("codigo_categoria") else t.get("codigo_categoria")),
                     "v":R2(t.get("valor_documento")),"doc":(t.get("numero_documento") or "").strip(),
                     "st":st.title()}
                if HOJE<=d<=FIM: itens.append(reg)
                elif d<HOJE: atr.append(reg)
        g=call(emp,"financas/extrato","ListarExtrato",
               {"nCodCC":cfg["getnet"],"dPeriodoInicial":HOJE.strftime("%d/%m/%Y"),"dPeriodoFinal":FIM.strftime("%d/%m/%Y")})
        pv=[x for x in (g.get("listaMovimentos") or []) if (x.get("cSituacao") or "")=="Previsto"]
        out["ents"][emp]={"nome":cfg["nome"],"contas":contas,"itens":itens,"desfecho":desfecho,
            "agenda":agenda_getnet(emp,cfg["getnet"],HOJE,FIM,itens),
            "atrasados":{"n":len(atr),"receber":R2(sum(x["v"] for x in atr if x["lado"]=="receber")),
                         "pagar":R2(sum(x["v"] for x in atr if x["lado"]=="pagar")),
                         "ids":[x["id"] for x in atr]},
            "getnet":{"n":len(pv),"bruto":R2(sum(x["nValorDocumento"] for x in pv if x["nValorDocumento"]>0)),
                      "taxa":R2(sum(x["nValorDocumento"] for x in pv if x["nValorDocumento"]<0))}}
        print("  %-8s contas %d | titulos na janela %d | atrasados %d"%(emp,len(contas),len(itens),len(atr)))
    return out

if __name__=="__main__":
    import historia
    H=datetime.datetime.strptime(sys.argv[1],"%d/%m/%Y").date() if len(sys.argv)>1 else datetime.date.today()
    D=coleta(H)
    # compara com o retrato da rodada anterior ANTES de gravar o de hoje
    D["deparar"]=historia.compara(D)
    foto=historia.salva(D)
    print("  retrato guardado: historico/%s%s"%(foto,"" if D["deparar"] else "  (primeira rodada, nada a comparar)"))
    json.dump(D,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"dados_caixa.json"),"w"),ensure_ascii=False)
    f=lambda v: format(R2(v),",.2f").replace(",","@").replace(".",",").replace("@",".")
    for e,x in D["ents"].items():
        s=sum(c["hoje"] for c in x["contas"]); r=sum(i["v"] for i in x["itens"] if i["lado"]=="receber")
        p=sum(i["v"] for i in x["itens"] if i["lado"]=="pagar")
        print("%-8s saldo %14s | a receber %13s | a pagar %13s | nao conciliados %d"%(
            x["nome"],f(s),f(r),f(p),sum(c["naoconc"] for c in x["contas"])))
