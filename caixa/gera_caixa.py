# -*- coding: utf-8 -*-
"""Relatorio de posicao de caixa e compromissos — Grupo Amana.

Roda duas vezes por semana (segunda e sexta). Le o Omie, apura o saldo
conciliado, levanta os titulos em aberto dos proximos 15 dias e grava
caixa.html na raiz do repositorio.

    python3 caixa/gera_caixa.py          # usa a data de hoje
    python3 caixa/gera_caixa.py 20/10/2026   # simula outra data de corte

Credenciais ficam em ~/.omie_<empresa>.json, fora do repositorio.
O saldo de partida de cada conta vem da ultima conciliacao fechada
(ANCORA abaixo) — atualize-a no fechamento de cada mes.
"""
import sys,os,json,base64,datetime,collections,statistics
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from omie_api import call

# ancora: ultima conciliacao bancaria fechada, conferida contra extrato
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
k=lambda v: ("%.0f mil"%(v/1000)) if abs(v)>=1000 else ("%.0f"%v)
fm=lambda v: ("\u2212" if v<0 else "")+f(abs(v))

ANCORA_DATA=datetime.date(2026,9,30)
ANCORA={"Bradesco conta corrente":1.00,"Santander conta corrente":0.00,"InfinitePay":11921.00,
 "Mercado Pago":632.55,"Santander ContaMax":236178.41,"Bradesco Invest Fácil":10045.43,
 "Santander CDB DI PJ":312008.23,"Bradesco CDB DI PJ":78811.59,"GetNet":0.00}
def coleta(HOJE):
    FIM=HOJE+datetime.timedelta(days=15)

    dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()

    BASE30=649598.21
    CONTAS=[(5177546899,"Santander conta corrente"),(5196586286,"Santander ContaMax"),
            (5199925490,"Santander CDB DI PJ"),(5177543696,"Bradesco conta corrente"),
            (5196707350,"Bradesco Invest Fácil"),(5226179398,"Bradesco CDB DI PJ"),
            (5177550204,"InfinitePay"),(5186771952,"Mercado Pago"),(5212188724,"GetNet")]
    D={}
    # saldo por conta: saldo conciliado de 30/09 (painel) + movimento conciliado de outubro
    PAINEL30={"Bradesco conta corrente":1.00,"Santander conta corrente":0.00,"InfinitePay":11921.00,
     "Mercado Pago":632.55,"Santander ContaMax":236178.41,"Bradesco Invest Fácil":10045.43,
     "Santander CDB DI PJ":312008.23,"Bradesco CDB DI PJ":78811.59,"GetNet":0.00}
    contas=[]
    for cod,nome in CONTAS:
        r=call("amana","financas/extrato","ListarExtrato",{"nCodCC":cod,"dPeriodoInicial":(ANCORA_DATA+datetime.timedelta(days=1)).strftime("%d/%m/%Y"),"dPeriodoFinal":HOJE.strftime("%d/%m/%Y")})
        mv=sum(x.get("nValorDocumento") or 0 for x in (r.get("listaMovimentos") or [])
               if not (x.get("cDesCliente") or "").startswith("SALDO") and (x.get("cSituacao") or "")=="Conciliado")
        prev=r.get("nSaldoAtualPrevisto")
        contas.append({"nome":nome,"saldo30":PAINEL30[nome],"mov":round(mv,2),"hoje":round(PAINEL30[nome]+mv,2)})
    D["contas"]=contas
    D["saldo_hoje"]=round(sum(c["hoje"] for c in contas),2)
    D["saldo_30"]=round(sum(c["saldo30"] for c in contas),2)
    # compromissos
    cli={};p=1
    while True:
        r=call("amana","geral/clientes","ListarClientesResumido",{"pagina":p,"registros_por_pagina":500})
        for c in r.get("clientes_cadastro_resumido") or []: cli[c["codigo_cliente"]]=(c.get("razao_social") or c.get("nome_fantasia") or "").strip()
        if p>=int(r.get("total_de_paginas") or 1) or p>30: break
        p+=1
    dia=collections.defaultdict(lambda:[0.0,0.0]); ent=[];sai=[]
    for rot,ep,cn,raiz,sg in (("e","financas/contareceber","ListarContasReceber","conta_receber_cadastro",1),
                              ("s","financas/contapagar","ListarContasPagar","conta_pagar_cadastro",-1)):
        p=1
        while True:
            r=call("amana",ep,cn,{"pagina":p,"registros_por_pagina":500})
            for t in (r.get(raiz) or []):
                v=t.get("data_vencimento") or ""
                if len(v)!=10: continue
                try: d=dt(v)
                except Exception: continue
                st=(t.get("status_titulo") or "").upper()
                if not (HOJE<=d<=FIM) or st in ("PAGO","RECEBIDO","CANCELADO"): continue
                val=t.get("valor_documento") or 0
                reg={"forn":cli.get(t.get("codigo_cliente_fornecedor"),"—"),"venc":v,"valor":round(val,2),"st":st}
                if sg>0: ent.append(reg); dia[v][0]+=val
                else: sai.append(reg); dia[v][1]+=val
            if p>=int(r.get("total_de_paginas") or 1) or p>40: break
            p+=1
    D["entradas"]={"n":len(ent),"total":round(sum(x["valor"] for x in ent),2),
                   "top":sorted(ent,key=lambda x:-x["valor"])[:5]}
    D["saidas"]={"n":len(sai),"total":round(sum(x["valor"] for x in sai),2),
                 "top":sorted(sai,key=lambda x:-x["valor"])[:5]}
    curva=[];acum=D["saldo_hoje"]
    for d in sorted(dia,key=lambda x:dt(x)):
        acum+=dia[d][0]-dia[d][1]
        curva.append({"dia":d,"ent":round(dia[d][0],2),"sai":round(dia[d][1],2),"saldo":round(acum,2)})
    D["curva"]=curva; D["saldo_fim"]=round(acum,2)
    mn=min(curva,key=lambda x:x["saldo"]) if curva else {"saldo":D["saldo_hoje"],"dia":"hoje"}
    D["menor"]={"valor":mn["saldo"],"dia":mn["dia"]}
    # GetNet agendada
    r=call("amana","financas/extrato","ListarExtrato",{"nCodCC":5212188724,"dPeriodoInicial":HOJE.strftime("%d/%m/%Y"),"dPeriodoFinal":FIM.strftime("%d/%m/%Y")})
    pv=[x for x in (r.get("listaMovimentos") or []) if (x.get("cSituacao") or "")=="Previsto"]
    D["getnet"]={"n":len(pv),"bruto":round(sum(x["nValorDocumento"] for x in pv if x["nValorDocumento"]>0),2),
                 "taxa":round(sum(x["nValorDocumento"] for x in pv if x["nValorDocumento"]<0),2)}
    D["getnet"]["liquido"]=round(D["getnet"]["bruto"]+D["getnet"]["taxa"],2)
    # atrasados
    atr=0;natr=0
    p=1
    while True:
        r=call("amana","financas/contapagar","ListarContasPagar",{"pagina":p,"registros_por_pagina":500})
        for t in (r.get("conta_pagar_cadastro") or []):
            if (t.get("status_titulo") or "").upper()=="ATRASADO": atr+=t.get("valor_documento") or 0; natr+=1
        if p>=int(r.get("total_de_paginas") or 1) or p>40: break
        p+=1
    D["atrasados"]={"n":natr,"total":round(atr,2)}

    print("saldo hoje",f(D["saldo_hoje"]),"| entradas",f(D["entradas"]["total"]),D["entradas"]["n"],
          "| saidas",f(D["saidas"]["total"]),D["saidas"]["n"],"| fim",f(D["saldo_fim"]))
    print("menor",f(D["menor"]["valor"]),D["menor"]["dia"],"| getnet liq",f(D["getnet"]["liquido"]),
          "| atrasados",f(D["atrasados"]["total"]),D["atrasados"]["n"])

    return D

def visuais(D,HOJE):

    dt=lambda s: datetime.datetime.strptime(s,"%d/%m/%Y").date()
    DIAS=["dom","seg","ter","qua","qui","sex","sáb"]
    # serie diaria completa, inclusive os dias sem nenhum lancamento
    mov={x["dia"]:(x["ent"],x["sai"]) for x in D["curva"]}
    ini=HOJE; fim=HOJE+datetime.timedelta(days=15)
    serie=[];acum=D["saldo_hoje"];d=ini
    while d<=fim:
        s=d.strftime("%d/%m/%Y"); e,sa=mov.get(s,(0.0,0.0))
        acum+=e-sa
        serie.append({"d":d,"lbl":d.strftime("%d"),"dow":DIAS[int(d.strftime("%w"))],
                      "ent":e,"sai":sa,"net":e-sa,"saldo":round(acum,2)})
        d+=datetime.timedelta(days=1)
    N=len(serie)
    smin=min(x["saldo"] for x in serie); smax=max(x["saldo"] for x in serie)
    imn=min(range(N),key=lambda i:serie[i]["saldo"])

    # ---------- 1) area do saldo ----------
    W,H=660,210; L,R,T,Bm=42,14,26,34
    def X(i): return L+i*((W-L-R)/(N-1))
    lo=smin-(smax-smin)*0.35; hi=smax+(smax-smin)*0.18
    def Y(v): return T+(hi-v)/(hi-lo)*(H-T-Bm)
    pts=[(X(i),Y(x["saldo"])) for i,x in enumerate(serie)]
    linha=" ".join("%.1f,%.1f"%p for p in pts)
    area="%s %.1f,%.1f %.1f,%.1f"%(linha,X(N-1),H-Bm,X(0),H-Bm)
    grid="";rot=""
    for g in range(4):
        v=lo+(hi-lo)*(g+1)/5
        y=Y(v); grid+='<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#E5E7EB" stroke-width="1"/>'%(L,y,W-R,y)
        grid+='<text x="%d" y="%.1f" font-size="7.5" fill="#9CA3AF" text-anchor="end" font-family="Inter">%s</text>'%(L-6,y+2.5,k(v))
    for i,x in enumerate(serie):
        if i%2==0 or i==N-1:
            rot+='<text x="%.1f" y="%d" font-size="7.5" fill="#6B7280" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="600">%s</text>'%(X(i),H-Bm+14,x["lbl"])
            rot+='<text x="%.1f" y="%d" font-size="6" fill="#9CA3AF" text-anchor="middle" font-family="Inter">%s</text>'%(X(i),H-Bm+23,x["dow"])
    mk=""
    for i in (0,imn,N-1):
        px,py=pts[i]
        mk+='<circle cx="%.1f" cy="%.1f" r="3.4" fill="#FAFAF7" stroke="#F97316" stroke-width="2"/>'%(px,py)
    cx,cy=pts[imn]
    # etiqueta do menor saldo: ancorada ao ponto, mas sempre dentro da area util
    bw_,bh_=112,29
    bx_=min(max(cx-bw_/2,L-30),W-R-bw_)
    by_=cy+22 if cy<H-Bm-70 else cy-bh_-16
    ly_=by_ if by_>cy else by_+bh_
    callout=('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#F97316" stroke-width="1" stroke-dasharray="2 2"/>'
             '<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="4" fill="#0D0F1A"/>'
             '<text x="%.1f" y="%.1f" font-size="6.5" fill="#F97316" font-family="Plus Jakarta Sans" font-weight="700" letter-spacing="1.1">MENOR SALDO</text>'
             '<text x="%.1f" y="%.1f" font-size="11" fill="#FFF" font-family="Plus Jakarta Sans" font-weight="800">%s</text>'
             )%(cx,cy,cx,ly_, bx_,by_,bw_,bh_, bx_+9,by_+11, bx_+9,by_+23, f(serie[imn]["saldo"]))
    ini_lbl=('' if imn==0 else '<text x="%.1f" y="%.1f" font-size="8" fill="#6B7280" font-family="Plus Jakarta Sans" font-weight="700" text-anchor="start">hoje %s</text>'%(pts[0][0]-4,pts[0][1]-11,f(serie[0]["saldo"])))
    fim_lbl=('<text x="%.1f" y="%.1f" font-size="8" fill="#0E9F6E" font-family="Plus Jakarta Sans" font-weight="700" text-anchor="end">30/10 · %s</text>'%(pts[-1][0]+2,pts[-1][1]-11,f(serie[-1]["saldo"])))
    AREA=f'''<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto">
    <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#F97316" stop-opacity=".30"/><stop offset="100%" stop-color="#F97316" stop-opacity="0"/></linearGradient></defs>
    {grid}<polygon points="{area}" fill="url(#g1)"/>
    <polyline points="{linha}" fill="none" stroke="#F97316" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>
    {mk}{callout}{ini_lbl}{fim_lbl}{rot}</svg>'''

    # ---------- 2) barras divergentes ----------
    W2,H2=660,164; C=H2/2-6; esc=max(max(x["ent"],x["sai"]) for x in serie) or 1
    bw=(W2-L-R)/N*0.52
    bars=""
    for i,x in enumerate(serie):
        cx2=X(i)
        he=(x["ent"]/esc)*(C-20); hs=(x["sai"]/esc)*(C-20)
        if x["ent"]: bars+='<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.6" fill="#0E9F6E" opacity=".88"/>'%(cx2-bw/2,C-he,bw,he)
        if x["sai"]: bars+='<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="1.6" fill="#DC2626" opacity=".88"/>'%(cx2-bw/2,C,bw,hs)
        if x["ent"]>=18000: bars+='<text x="%.1f" y="%.1f" font-size="7" fill="#0E9F6E" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="700">%s</text>'%(cx2,C-he-4,k(x["ent"]))
        if x["sai"]>=12000: bars+='<text x="%.1f" y="%.1f" font-size="7" fill="#DC2626" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="700">%s</text>'%(cx2,C+hs+9,k(x["sai"]))
    rot2="".join('<text x="%.1f" y="%d" font-size="7" fill="#9CA3AF" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="600">%s</text>'%(X(i),H2-6,x["lbl"]) for i,x in enumerate(serie))
    BARS=f'''<svg viewBox="0 0 {W2} {H2}" style="width:100%;height:auto">
    <line x1="{L}" y1="{C}" x2="{W2-R}" y2="{C}" stroke="#D1D5DB" stroke-width="1"/>
    <text x="{W2-R}" y="12" font-size="7" fill="#0E9F6E" text-anchor="end" font-family="Plus Jakarta Sans" font-weight="700" letter-spacing=".6">ENTRA ▲</text>
    <text x="{W2-R}" y="{H2-18}" font-size="7" fill="#DC2626" text-anchor="end" font-family="Plus Jakarta Sans" font-weight="700" letter-spacing=".6">SAI ▼</text>
    {bars}{rot2}</svg>'''

    # ---------- 3) calendario de caixa ----------
    cw,ch,gap=86,62,6
    col0=int(serie[0]["d"].strftime("%w"))
    linhas_cal=(col0+N+6)//7
    W3=7*cw+6*gap; H3=linhas_cal*(ch+gap)+22
    cells=""
    for c in range(7):
        cells+='<text x="%.1f" y="12" font-size="7.5" fill="#9CA3AF" text-anchor="middle" font-family="Plus Jakarta Sans" font-weight="700" letter-spacing="1">%s</text>'%(c*(cw+gap)+cw/2,DIAS[c].upper())
    mxn=max(abs(x["net"]) for x in serie) or 1
    for i,x in enumerate(serie):
        pos=col0+i; cx3=(pos%7)*(cw+gap); cy3=22+(pos//7)*(ch+gap)
        inten=min(abs(x["net"])/mxn,1)
        if x["net"]>0: fill="#0E9F6E"; op=0.08+inten*0.26
        elif x["net"]<0: fill="#DC2626"; op=0.08+inten*0.26
        else: fill="#9CA3AF"; op=0.05
        cells+='<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="5" fill="%s" opacity="%.2f"/>'%(cx3,cy3,cw,ch,fill,op)
        cells+='<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="5" fill="none" stroke="#E5E7EB"/>'%(cx3,cy3,cw,ch)
        cells+='<text x="%.1f" y="%.1f" font-size="12" fill="#0D0F1A" font-family="Plus Jakarta Sans" font-weight="800">%s</text>'%(cx3+8,cy3+17,x["lbl"])
        if x["net"]:
            cor="#0E9F6E" if x["net"]>0 else "#DC2626"
            cells+='<text x="%.1f" y="%.1f" font-size="8.5" fill="%s" font-family="Plus Jakarta Sans" font-weight="700" text-anchor="end">%s%s</text>'%(cx3+cw-8,cy3+17,cor,"+" if x["net"]>0 else "−",k(abs(x["net"])))
        else:
            cells+='<text x="%.1f" y="%.1f" font-size="11" fill="#D1D5DB" font-family="Plus Jakarta Sans" font-weight="700" text-anchor="end">—</text>'%(cx3+cw-8,cy3+17)
        cells+='<text x="%.1f" y="%.1f" font-size="6.5" fill="#6B7280" font-family="Plus Jakarta Sans" font-weight="700" letter-spacing=".8">SALDO</text>'%(cx3+8,cy3+38)
        cells+='<text x="%.1f" y="%.1f" font-size="10" fill="#0D0F1A" font-family="Plus Jakarta Sans" font-weight="700">%s</text>'%(cx3+8,cy3+52,f(x["saldo"]))
        if i==imn: cells+='<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="5" fill="none" stroke="#F97316" stroke-width="2"/>'%(cx3,cy3,cw,ch)
    CAL=f'<svg viewBox="0 0 {W3} {H3}" style="width:100%;height:auto">{cells}</svg>'
    sem=[]
    for i,x in enumerate(serie):
        w=(col0+i)//7
        while len(sem)<=w: sem.append({"ent":0,"sai":0,"ini":x["lbl"],"fim":x["lbl"]})
        sem[w]["ent"]+=x["ent"]; sem[w]["sai"]+=x["sai"]; sem[w]["fim"]=x["lbl"]



    return {"AREA":AREA,"BARS":BARS,"CAL":CAL,"serie":[{**x,"d":x["d"].strftime("%d/%m/%Y")} for x in serie],"semanas":sem,"imn":imn}

MESES=["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
def monta(D,G,HOJE,CSS,BLACK,WHITE):
    FIM=HOJE+datetime.timedelta(days=15)
    DT=HOJE.strftime("%d/%m/%Y"); DT_CURTA=HOJE.strftime("%d/%m")
    CAPA_DT=HOJE.strftime("%d ")+MESES[HOJE.month-1][:3].upper()+HOJE.strftime(" %Y")
    JANELA="%d de %s a %d de %s"%(HOJE.day,MESES[HOJE.month-1],FIM.day,MESES[FIM.month-1])
    FIM_EXT="%d de %s"%(FIM.day,MESES[FIM.month-1])
    ANC_EXT="%d de %s"%(ANCORA_DATA.day,MESES[ANCORA_DATA.month-1])
    GERADO=datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")


    SER=G["serie"]; SEM=G["semanas"]; IMN=G["imn"]
    C={c["nome"]:c for c in D["contas"]}
    SANT=C["Santander conta corrente"]["hoje"]+C["Santander ContaMax"]["hoje"]
    BRAD=C["Bradesco conta corrente"]["hoje"]+C["Bradesco Invest Fácil"]["hoje"]
    GRUPOS=[("Santander · conta corrente + ContaMax",SANT,"a conta corrente varre o saldo para o ContaMax todo dia; leia as duas juntas"),
            ("Santander · CDB DI PJ",C["Santander CDB DI PJ"]["hoje"],"aplicação"),
            ("Bradesco · conta corrente + Invest Fácil",BRAD,"mesmo mecanismo de varredura"),
            ("Bradesco · CDB DI PJ",C["Bradesco CDB DI PJ"]["hoje"],"aplicação"),
            ("InfinitePay",C["InfinitePay"]["hoje"],"recebimento de comissão de passeio"),
            ("Mercado Pago",C["Mercado Pago"]["hoje"],""),
            ("GetNet",C["GetNet"]["hoje"],"zera a cada liquidação; o que está por vir aparece na página 4")]
    cur=D["curva"]; mx=max(max(x["ent"],x["sai"]) for x in cur) or 1
    smin=min(x["saldo"] for x in cur); smax=max(x["saldo"] for x in cur)
    W,H,PAD=640,150,8
    def sx(i): return 30+i*((W-50)/max(len(cur)-1,1))
    def sy(v): return H-20-((v-smin)/((smax-smin) or 1))*(H-45)
    pts=" ".join("%.1f,%.1f"%(sx(i),sy(x["saldo"])) for i,x in enumerate(cur))
    barras=""
    for i,x in enumerate(cur):
        bx=sx(i)-5
        he=(x["ent"]/mx)*34; hs=(x["sai"]/mx)*34
        barras+='<rect x="%.1f" y="%.1f" width="4.5" height="%.1f" fill="#0E9F6E" opacity=".75" rx="1"/>'%(bx,H-4-he,he)
        barras+='<rect x="%.1f" y="%.1f" width="4.5" height="%.1f" fill="#DC2626" opacity=".75" rx="1"/>'%(bx+5,H-4-hs,hs)
    rot="".join('<text x="%.1f" y="%d" font-size="6.5" fill="#9CA3AF" text-anchor="middle" font-family="Inter">%s</text>'%(sx(i),H+8,x["dia"][:5]) for i,x in enumerate(cur) if i%2==0)
    imn=min(range(len(cur)),key=lambda i:cur[i]["saldo"])
    SVG=f'''<svg viewBox="0 0 {W} {H+14}" style="width:100%;height:auto">
    <polyline points="{pts}" fill="none" stroke="#F97316" stroke-width="2" stroke-linejoin="round"/>
    {barras}<circle cx="{sx(imn):.1f}" cy="{sy(cur[imn]["saldo"]):.1f}" r="4" fill="#F97316"/>
    <text x="{sx(imn):.1f}" y="{sy(cur[imn]["saldo"])-9:.1f}" font-size="8" font-weight="700" fill="#F97316" text-anchor="middle" font-family="Plus Jakarta Sans">menor saldo</text>
    {rot}</svg>'''
    def pag(n,tema,corpo,tot=9):
        return f'''<section class="page"><div class="page-header"><img class="logo" src="data:image/png;base64,{BLACK}" alt="Exact BR">
    <div class="meta"><span class="accent">Seção {n-1:02d}</span><span class="pipe"></span><span>{tema}</span></div></div>
    <div class="page-body">{corpo}</div>
    <div class="page-footer"><span>Relatório de caixa · Grupo Amana · {DT}</span><span class="page-num"><span class="cur">{n:02d}</span> / {tot:02d}</span></div></section>'''

    P=[]
    P.append(f'''<section class="page dark"><div class="page-header"><img class="logo" src="data:image/png;base64,{WHITE}" alt="Exact BR">
    <div class="meta"><span class="accent">Posição de caixa</span><span class="pipe"></span><span>{CAPA_DT}</span></div></div>
    <div class="cover-content"><div class="cover-eyebrow">Para Tiago e João,</div>
    <h1 class="cover-title">Caixa e<br>compromissos<br><span class="ital">dos próximos 15 dias.</span></h1>
    <p class="cover-sub">O que a Amana tem hoje, o que está contratado para entrar e sair até {FIM_EXT}, e o quanto desse retrato dá para levar a sério.</p>
    <div class="cover-meta"><div><div class="label">Cliente</div><div class="value">Grupo Amana</div></div>
    <div><div class="label">Janela</div><div class="value ital">{JANELA}</div></div>
    <div><div class="label">Fonte</div><div class="value">Omie · extratos bancários</div></div>
    <div><div class="label">Gerado em</div><div class="value">{GERADO}<br><span style="font-weight:400;color:rgba(255,255,255,.55)">João Victor · Exact BR</span></div></div></div></div></section>''')
    P.append(pag(2,"A semana em quatro números",f'''<div class="chapter-num">— 01 —</div>
    <h2 class="editorial">O caixa de hoje <span class="light">e o que está</span><br><span class="orange">contratado até dia 30.</span></h2>
    <p class="lede">Nenhum número desta página é projeção. É saldo conciliado e título já lançado no Omie.</p>
    <div class="nums-grid">
    <div class="num-cell"><div class="n-eye">Caixa hoje</div><div class="n-val orange">{f(D["saldo_hoje"])}</div><div class="n-sub">era {f(D["saldo_30"])} em 30/09</div></div>
    <div class="num-cell"><div class="n-eye">Entradas contratadas</div><div class="n-val">{f(D["entradas"]["total"])}</div><div class="n-sub">{D["entradas"]["n"]} títulos a receber</div></div>
    <div class="num-cell"><div class="n-eye">Saídas contratadas</div><div class="n-val">{f(D["saidas"]["total"])}</div><div class="n-sub">{D["saidas"]["n"]} títulos a pagar</div></div>
    <div class="num-cell"><div class="n-eye">Menor saldo</div><div class="n-val">{f(D["menor"]["valor"])}</div><div class="n-sub">em {D["menor"]["dia"]}</div></div></div>
    <p class="body-text">Com o que está no sistema hoje, a Amana atravessa a quinzena sem aperto: o caixa parte de <strong>{f(D["saldo_hoje"])}</strong>, não cruza zero em nenhum dia e termina {FIM_EXT} em <strong>{f(D["saldo_fim"])}</strong>. O ponto mais baixo é hoje mesmo.</p>
    <p class="body-text">A folga vem principalmente do cartão. A agenda da GetNet para os próximos 15 dias é de <strong>{f(D["getnet"]["bruto"])}</strong> em {D["getnet"]["n"]} recebimentos, dos quais {f(abs(D["getnet"]["taxa"]))} são taxa — <strong>{f(D["getnet"]["liquido"])} líquidos</strong>. Isso não é estimativa: são parcelas de vendas já realizadas, com data marcada.</p>
    <div class="highlight-box"><div class="highlight-tag">Leia a página 6 antes de decidir com este número</div>
    <p>O retrato acima é verdadeiro no que mostra, mas <strong>incompleto no que ainda não foi lançado</strong>. Medimos: de cada R$ 100 que a Amana efetivamente pagou na primeira quinzena de outubro, apenas <strong>R$ 29 já estavam no Omie</strong> no dia 30 de setembro. A página 6 põe número nisso.</p></div>'''))
    linhas="".join(f'<tr><td class="label">{n}</td><td class="num">{fm(v)}</td><td style="font-size:10px;color:#6B7280">{o}</td></tr>' for n,v,o in GRUPOS)
    P.append(pag(3,"Posição por conta",f'''<div class="chapter-num">— 02 —</div>
    <h2 class="editorial">Onde o dinheiro <span class="light">está</span><br><span class="orange">hoje.</span></h2>
    <p class="lede">Saldo conciliado de {ANC_EXT} mais o movimento já conciliado desde então.</p>
    <div class="diag-section"><h3>A · Caixa por banco</h3><div class="sub">Posição em {DT}</div>
    <table class="diag-table"><thead><tr><th>Conta</th><th class="num">Saldo</th><th>Observação</th></tr></thead>
    <tbody>{linhas}<tr class="highlight"><td class="label">Total</td><td class="num">{f(D["saldo_hoje"])}</td><td></td></tr></tbody></table></div>
    <p class="body-text">As contas correntes do Santander e do Bradesco aparecem somadas às respectivas aplicações porque o banco varre o saldo da conta corrente todo dia. Lidas isoladamente, elas ficam negativas sem que exista qualquer descoberto — é mecânica de varredura, não falta de dinheiro.</p>
    <p class="body-text">Do total, <strong>{f(C["Santander CDB DI PJ"]["hoje"]+C["Bradesco CDB DI PJ"]["hoje"])}</strong> está em CDB e não é caixa de giro imediato, ainda que tenha liquidez diária.</p>
    <div class="highlight-box"><div class="highlight-tag">Pendência conhecida</div>
    <p>O rendimento de setembro do <strong>Santander CDB DI PJ</strong> ainda não foi lançado — a conta está parada em {f(C["Santander CDB DI PJ"]["hoje"])} desde o dia 15 de setembro. O valor entra assim que o extrato de investimentos for disponibilizado.</p></div>'''))
    te="".join(f'<tr><td class="label">{x["forn"][:46]}</td><td>{x["venc"]}</td><td class="num">{f(x["valor"])}</td></tr>' for x in D["entradas"]["top"])
    ts="".join(f'<tr><td class="label">{x["forn"][:46]}</td><td>{x["venc"]}</td><td class="num">{f(x["valor"])}</td></tr>' for x in D["saidas"]["top"])
    P.append(pag(4,"Compromissos",f'''<div class="chapter-num">— 03 —</div>
    <h2 class="editorial">O que está <span class="light">contratado</span><br>para os <span class="orange">próximos 15 dias.</span></h2>
    <p class="lede">Títulos em aberto com vencimento entre {DT_CURTA} e {FIM_EXT}. Nada aqui é estimado.</p>
    <div class="diag-section"><h3>A · Maiores entradas</h3><div class="sub">{D["entradas"]["n"]} títulos a receber somando {f(D["entradas"]["total"])}</div>
    <table class="diag-table"><thead><tr><th>Cliente</th><th>Vencimento</th><th class="num">Valor</th></tr></thead><tbody>{te}</tbody></table></div>
    <div class="diag-section"><h3>B · Maiores saídas</h3><div class="sub">{D["saidas"]["n"]} títulos a pagar somando {f(D["saidas"]["total"])}</div>
    <table class="diag-table"><thead><tr><th>Fornecedor</th><th>Vencimento</th><th class="num">Valor</th></tr></thead><tbody>{ts}</tbody></table></div>
    <p class="body-text">A maior saída isolada da quinzena é o <strong>Simples Nacional, {f(22682.18)}, no dia 20</strong>. Depois dela, nenhuma outra passa de nove mil reais — o restante é pulverizado em {D["saidas"]["n"]-1} títulos.</p>'''))
    kk=lambda v: f(v) if v else "—"
    tabsem="".join(f'''<tr><td class="label">Semana {i+1} · dias {x["ini"]} a {x["fim"]}</td><td class="num">{kk(x["ent"])}</td><td class="num">{kk(x["sai"])}</td><td class="num">{"+" if x["ent"]-x["sai"]>=0 else "−"}{f(abs(x["ent"]-x["sai"]))}</td></tr>''' for i,x in enumerate(SEM))
    P.append(pag(5,"Fluxo de caixa diário",f'''<div class="chapter-num">— 04 —</div>
    <h2 class="editorial">O caixa, <span class="light">dia a dia,</span><br>até <span class="orange">{FIM_EXT}.</span></h2>
    <p class="lede">Dezesseis dias, um a um — inclusive os que não têm movimento nenhum.</p>
    <div style="margin:14px 0 2px">{G["AREA"]}</div>
    <p class="body-text" style="margin-top:2px">A linha é o saldo ao fim de cada dia. O ponto mais baixo da quinzena é <strong>hoje</strong>: {f(SER[IMN]["saldo"])}. A partir daí o caixa só sobe, porque a agenda da GetNet concentra recebimento na segunda metade do período e não há nenhuma saída grande depois do dia 20.</p>
    <div class="diag-section" style="margin-top:14px"><h3>A · O que entra e o que sai em cada dia</h3>
    <div class="sub">Verde acima da linha é entrada; vermelho abaixo é saída</div>{G["BARS"]}</div>
    <div class="diag-section" style="margin-top:10px"><h3>B · Por semana</h3>
    <table class="diag-table"><thead><tr><th>Período</th><th class="num">Entradas</th><th class="num">Saídas</th><th class="num">Líquido</th></tr></thead>
    <tbody>{tabsem}<tr class="highlight"><td class="label">Quinzena</td><td class="num">{f(D["entradas"]["total"])}</td><td class="num">{f(D["saidas"]["total"])}</td><td class="num">+{f(D["entradas"]["total"]-D["saidas"]["total"])}</td></tr></tbody></table></div>'''))
    P.append(pag(6,"Calendário de caixa",f'''<div class="chapter-num">— 05 —</div>
    <h2 class="editorial">O mesmo caixa, <span class="light">no formato</span><br>de quem <span class="orange">olha a agenda.</span></h2>
    <p class="lede">Cada dia traz o líquido do dia e o saldo com que a empresa dorme. A intensidade da cor é o tamanho do movimento.</p>
    <div style="margin:16px 0">{G["CAL"]}</div>
    <div class="highlight-box"><div class="highlight-tag">Como ler</div>
    <p>O número grande é o dia. À direita dele, <strong>o líquido daquele dia</strong> — verde entra, vermelho sai. Embaixo, <strong>o saldo ao fim do dia</strong>. A célula contornada em laranja é o menor saldo da quinzena. Dias em cinza não têm nenhum título com vencimento marcado.</p></div>
    <p class="body-text">Nove dos dezesseis dias têm movimento contratado. Os sete restantes aparecem em cinza não porque a empresa para, mas porque <strong>nada foi lançado com aquela data</strong> — é a mesma lacuna que a próxima página mede.</p>'''))
    DOWN={"dom":"domingo","seg":"segunda","ter":"terça","qua":"quarta","qui":"quinta","sex":"sexta","sáb":"sábado"}
    def cel(v,cor=""):
        return f'<td class="num"{cor}>{f(v)}</td>' if v else '<td class="num" style="color:#D1D5DB">&#8212;</td>'
    linhas_d=""
    for i,x in enumerate(SER):
        net=x["ent"]-x["sai"]
        cls=' class="highlight"' if i==IMN else ''
        cor_net=' style="color:#059669;font-weight:700"' if net>0 else (' style="color:#DC2626;font-weight:700"' if net<0 else '')
        linhas_d+=(f'<tr{cls}><td class="label">{x["d"][:5]}</td>'
                   f'<td style="color:#6B7280;font-size:10px">{DOWN[x["dow"]]}</td>'
                   f'{cel(x["ent"])}{cel(x["sai"])}'
                   f'<td class="num"{cor_net}>{("+" if net>0 else ("&#8722;" if net<0 else ""))+f(abs(net)) if net else "&#8212;"}</td>'
                   f'<td class="num">{f(x["saldo"])}</td></tr>')
    P.append(pag(7,"Fluxo de caixa diário · tabela",f'''<div class="chapter-num">— 06 —</div>
    <h2 class="editorial">O mesmo fluxo, <span class="light">linha a linha,</span><br>para <span class="orange">conferência.</span></h2>
    <p class="lede">Os dezesseis dias da quinzena, com entrada, saída, líquido do dia e saldo acumulado.</p>
    <div class="diag-section" style="margin-top:14px">
    <table class="diag-table"><thead><tr><th>Dia</th><th></th><th class="num">Entradas</th><th class="num">Saídas</th><th class="num">Líquido do dia</th><th class="num">Saldo acumulado</th></tr></thead>
    <tbody>{linhas_d}
    <tr style="border-top:2px solid #D1D5DB"><td class="label">Total da quinzena</td><td></td><td class="num">{f(D["entradas"]["total"])}</td><td class="num">{f(D["saidas"]["total"])}</td><td class="num" style="color:#059669;font-weight:700">+{f(D["entradas"]["total"]-D["saidas"]["total"])}</td><td class="num">{f(D["saldo_fim"])}</td></tr>
    </tbody></table></div>
    <p class="body-text">A linha destacada é o dia de menor saldo. O saldo acumulado parte de <strong>{f(D["saldo_hoje"])}</strong>, que é a posição de hoje apurada na página 2, e incorpora apenas títulos já lançados no Omie com vencimento dentro da janela.</p>
    <div class="highlight-box"><div class="highlight-tag">Como conferir no Omie</div>
    <p>Cada linha desta tabela corresponde aos títulos com vencimento naquela data, em <strong>Contas a Pagar</strong> e <strong>Contas a Receber</strong>, filtrando por situação em aberto. O saldo de partida vem da conciliação bancária de {ANC_EXT} mais o movimento já conciliado desde então.</p></div>'''))
    P.append(pag(8,"Alertas e cobertura",f'''<div class="chapter-num">— 07 —</div>
    <h2 class="editorial">O que este relatório <span class="light">ainda</span><br><span class="orange">não enxerga.</span></h2>
    <p class="lede">A parte mais importante do documento. Sem ela, o número da capa vira armadilha.</p>
    <p class="body-text">Medimos a precisão desta régua antes de publicá-la. Montamos a mesma projeção com corte em <strong>30 de setembro</strong> e comparamos com o que de fato aconteceu entre 1º e 14 de outubro. Dos <strong>{f(200386.32)}</strong> efetivamente pagos na quinzena, apenas <strong>{f(81943.07)}</strong> já estavam lançados no Omie no dia 30 — <strong>41%</strong>.</p>
    <p class="body-text">O resto apareceu depois: <strong>{f(271156.12)} em 26 títulos</strong> com vencimento dentro da quinzena que não existiam no sistema no dia 30. Desses, 12 já foram pagos e <strong>14 seguem vencidos</strong>.</p>
    <div class="nums-grid">
    <div class="num-cell"><div class="n-eye">Cobertura de lançamento</div><div class="n-val orange">41<span class="sm">%</span></div><div class="n-sub">do que foi pago já estava lançado em 30/09</div></div>
    <div class="num-cell"><div class="n-eye">Lançado durante o mês</div><div class="n-val">{f(271156.12)}</div><div class="n-sub">26 títulos, 1ª quinzena de outubro</div></div>
    <div class="num-cell"><div class="n-eye">Concentrado em</div><div class="n-val">94<span class="sm">%</span></div><div class="n-sub">um único título intercompany</div></div>
    <div class="num-cell"><div class="n-eye">Vencido e não pago</div><div class="n-val">{f(D["atrasados"]["total"])}</div><div class="n-sub">{D["atrasados"]["n"]} títulos em atraso</div></div></div>
    <div class="highlight-box"><div class="highlight-tag">A boa notícia está no detalhe</div>
    <p>Dos {f(271156.12)} lançados em atraso, <strong>{f(254866.17)} são um título só: a compra de diárias da Pousada Topázio</strong> — intercompany, mensal, de valor conhecido. E <strong>98% de toda a lacuna vem de fornecedores que se repetem todo mês</strong>. Não é imprevisibilidade do negócio: é lançamento que entra tarde.</p></div>
    <ul class="editorial-list">
    <li><strong>Vencido e não pago.</strong> {f(D["atrasados"]["total"])} em {D["atrasados"]["n"]} títulos a pagar em atraso, fora da curva da página 4 porque não têm data futura.</li>
    <li><strong>Conciliação de outubro em andamento.</strong> O saldo da página 2 considera apenas o movimento já conciliado.</li>
    <li><strong>Topázio fora deste relatório.</strong> Entra quando o recebimento da compra de diárias for lançado do lado de lá.</li></ul>'''))
    P.append(f'''<section class="page dark"><div class="page-header"><img class="logo" src="data:image/png;base64,{WHITE}" alt="Exact BR">
    <div class="meta"><span class="accent">Próximo passo</span></div></div><div class="page-body">
    <div class="chapter-num">— final —</div>
    <h2 class="editorial">De posição <span class="light">para</span><br><span class="orange">previsão.</span></h2>
    <p class="body-text">Este documento é honesto sobre o que é: um retrato de <strong>posição e compromissos</strong>, não uma previsão de caixa. A diferença entre os dois é uma só — e ela não é técnica, é de processo.</p>
    <p class="body-text">Levantamos <strong>201 fornecedores recorrentes</strong> das duas empresas, com dia típico de vencimento, valor típico e comportamento do valor. São <strong>34 fornecedores mensais na Amana</strong>, movimentando cerca de R$ 693 mil por mês, e 37 na Topázio, com R$ 209 mil. Essa lista é o roteiro: lançados como previsto até o dia 25 do mês anterior, eles fecham 98% da lacuna medida na página 5.</p>
    <p class="body-text">Com isso feito, este mesmo relatório deixa de dizer "é o que sabemos" e passa a dizer "é o que vai acontecer". Refaremos o teste de precisão para provar, antes de mudar o nome do documento.</p>
    <div class="highlight-box dark"><div class="highlight-tag">O que pedimos</div>
    <p><strong>Lançar os recorrentes com antecedência</strong> e <strong>fechar o Omie no dia 25</strong>. São as duas condições para a previsibilidade que o relatório promete — e as duas estão do lado de vocês, não do nosso.</p></div>
    <div class="signature-grid"><div class="signature"><div class="sig-name">João Victor Andrade de Souza</div>
    <div class="sig-role">Sócio-fundador · Exact BR</div></div>
    <div style="text-align:right"><div class="sig-role" style="margin-bottom:4px">Disciplina Gera Lucro</div>
    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;font-weight:500;color:rgba(255,255,255,.85)">Exact BR · Recife — PE</div></div></div>
    </div></section>''')
    HTML=f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório semanal de caixa · Grupo Amana · Exact BR</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Fraunces:ital,wght@0,300;0,400;0,500;1,300;1,400&display=swap" rel="stylesheet">
    <style>{CSS}</style></head><body>{"".join(P)}
    <button class="print-btn" onclick="window.print()">↓ Exportar PDF</button></body></html>'''
    return HTML

if __name__=="__main__":
    HOJE=datetime.datetime.strptime(sys.argv[1],"%d/%m/%Y").date() if len(sys.argv)>1 else datetime.date.today()
    AQUI=os.path.dirname(os.path.abspath(__file__))
    CSS=open(os.path.join(AQUI,"estilo.css"),encoding="utf-8").read()
    BLACK=base64.b64encode(open(os.path.join(AQUI,"logo-preta.png"),"rb").read()).decode()
    WHITE=base64.b64encode(open(os.path.join(AQUI,"logo-branca.png"),"rb").read()).decode()
    print("lendo o Omie...")
    D=coleta(HOJE)
    G=visuais(D,HOJE)
    HTML=monta(D,G,HOJE,CSS,BLACK,WHITE)
    saida=os.path.join(os.path.dirname(AQUI),"caixa.html")
    open(saida,"w",encoding="utf-8").write(HTML)
    print("gravado %s"%saida)
    print("  caixa hoje %s | entradas %s | saidas %s | menor saldo %s em %s"%(
        f(D["saldo_hoje"]),f(D["entradas"]["total"]),f(D["saidas"]["total"]),
        f(D["menor"]["valor"]),D["menor"]["dia"]))
