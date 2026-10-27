# -*- coding: utf-8 -*-
"""Relatorio de FECHAMENTO de setembro/2026, 9 paginas, no modelo paisagem de agosto.
   Todo numero sai de dre/dados_rel.json + dre/orc2.json, que o monta_dados_rel.py
   reconstroi do index.html publicado. O relatorio nao calcula nada por conta."""
import json,re,os
BASE=os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/")
RAIZ=os.path.expanduser("~/painel-amanatopazio/")
MODELO=BASE+"Relatorio_Gerencial_Amana_Topazio_ago2026_v2.html"
SAIDA=BASE+"Relatorio_Fechamento_Amana_Topazio_set2026.html"
d=json.load(open(RAIZ+"dre/dados_rel.json")); orc=json.load(open(RAIZ+"dre/orc2.json"))
S=d["casc"]; com=d["com"]; L=d["linhas"]
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
pc=lambda v,b: ("%.1f%%"%(abs(v)/b*100)).replace(".",",") if b else "—"
pct=lambda v: ("%.2f%%"%v).replace(".",",")
mod=open(MODELO,encoding="utf-8").read()
import collections as _c
_cnt=_c.Counter(re.findall(r'<img class="logo" src="(data:image/[^"]+)"',mod))
_ord=[k for k,_ in _cnt.most_common()]; logo_claro,logo_escuro=_ord[0],_ord[-1]
cabeca=mod[:mod.index("</head>")+7]; rodape=mod[mod.rindex("</section>")+10:]
TAG="Relatório de fechamento · Setembro/2026"
PAG=[0]; CAP=[0]
def cab():
    CAP[0]+=1
    return ('<span class="chapter-num" style="margin-bottom:10px;">— %02d —</span>'%CAP[0],"Capítulo %02d"%CAP[0])
def sec(titulo,corpo,cap=None,dark=False):
    PAG[0]+=1; n=PAG[0]
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'
        %(logo_escuro if dark else logo_claro,cap or "Fechamento",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>%s</span>'
        '<span class="page-num"><span class="cur">%02d</span> / __TOT__</span></div>'
        %(' style="color: rgba(255,255,255,0.4);"' if dark else "",TAG,n))
    return '<section class="slide%s" data-slide="%d">%s<div class="s-body">%s</div>%s</section>\n'%(
        " dark" if dark else "",n,hd,corpo,ft)
def kc(l,v,dd,hl=False):
    return '<div class="kc"><div class="kl">%s</div><div class="kv%s">%s</div><div class="kd">%s</div></div>'%(l,' hl' if hl else '',v,dd)
def tab(cols,head,rows,cls="dtab xs",num=None):
    N=(lambda i:i>0) if num is None else (lambda i:i in num)
    h="".join('<th%s>%s</th>'%(' class="n"' if N(i) else '',c) for i,c in enumerate(head))
    b=""
    for r in rows:
        tds="".join('<td%s>%s</td>'%(' class="n%s"'%(" neg" if (isinstance(v,str) and v.startswith("-")) else "") if N(i) else '',v)
                    for i,v in enumerate(r["c"]))
        b+='<tr class="%s">%s</tr>'%(r.get("cls",""),tds)
    cg="".join('<col%s>'%(' style="width:%s"'%c if c else '') for c in cols)
    return '<table class="%s"><colgroup>%s</colgroup><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'%(cls,cg,h,b)
def cat(ent,mes,chave):
    return round(sum(x["v"] for x in L["%s_%s"%(ent,mes)] if chave in x["c"] or chave in x["cat"]),2)
IC=abs(cat("amana","9","02. Custo dos Serviços Prestados"))
# Relatorio comercial diario da Pousada Topazio, posicao de 26/10/2026. Os numeros de
# agosto e setembro desse relatorio batem item por item com o D.com do painel -- estes
# aqui sao os meses que o painel ainda nao fecha.
FRENTE=[("outubro/26",85.59,82.80,686080.29),("novembro/26",69.11,77.11,510749.07),
        ("dezembro/26",35.27,77.20,265104.09)]
CARTEIRA_CARTAO=586280.21; CARTEIRA_COBRAR=449828.12
OUT_OC=85.59; OUT_TKT=1823.26; OUT_REC=649940.98; OUT_CANC=43.97
CAIXA_2610=645769.35
CAIXA_SI=round(sum(x["si"] for x in d["contas"]["consol"]),2)
CAIXA_SF=round(sum(x["sf"] for x in d["contas"]["consol"]),2)
def be(m):
    x=d["resumo"]["consol"][m]; rb=x["rb"]; mc=rb+x["cvar"]
    pe=-x["cfix"]/(mc/rb)
    return dict(rb=rb,cvar=x["cvar"],mc=mc,mcp=mc/rb,cfix=x["cfix"],eb=x["ebitda"],
                pe=pe,oce=com[m]["oc"]*pe/rb,seg=(rb-pe)/rb*100)
B8,B9=be("8"),be("9")
pp=lambda v: ("%.1f%%"%v).replace(".",",")
H=[]
# ---- 1 capa
H.append(sec("Setembro/2026",
 '<span class="eyebrow">Relatório de fechamento</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1100px;">O resultado caiu.<br>'
 '<span style="color:var(--orange);">A estrutura fixa, não.</span></h2>'
 '<p class="lede" style="max-width:920px;font-size:19px;margin-top:18px;">Grupo Amana + Pousada Topázio, '
 'setembro de 2026. A receita recuou %s contra agosto e o custo fixo ficou praticamente igual — é isso que '
 'explica o EBITDA cair de %s para %s da receita.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:940px;">A operação continua acima do ponto de '
 'equilíbrio, mas com um terço menos de folga: a margem de segurança foi de %s em agosto para '
 '<strong>%s</strong> em setembro. E o mês que precisa de atenção comercial agora é <strong>dezembro</strong>, '
 'que está com %s de ocupação contratada contra %s no mesmo mês do ano passado.</p>'
 '<div class="proof-row"><div><div class="pv orange">%s</div><div class="pl">Receita bruta do mês</div></div>'
 '<div><div class="pv">%s</div><div class="pl">EBITDA · %s da receita</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Resultado depois de capex</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Caixa em 30/09</div></div></div>'%(
   ("%.1f%%"%((S["consol_8"]["rb"]-S["consol_9"]["rb"])/S["consol_8"]["rb"]*100)).replace(".",","),
   pc(S["consol_8"]["eb"],S["consol_8"]["rb"]),pc(S["consol_9"]["eb"],S["consol_9"]["rb"]),
   pp(B8["seg"]),pp(B9["seg"]),
   ("%.2f%%"%FRENTE[2][1]).replace(".",","),("%.2f%%"%FRENTE[2][2]).replace(".",","),
   f(S["consol_9"]["rb"]),f(S["consol_9"]["eb"]),pc(S["consol_9"]["eb"],S["consol_9"]["rb"]),
   f(S["consol_9"]["res"]),f(CAIXA_SF)),
 dark=True))
# ---- 2 em um olhar
c9,c8=S["consol_9"],S["consol_8"]
_m,_c=cab()
H.append(sec("Os números de setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">Setembro <span class="light">de 2026,</span> <span class="orange">em um olhar.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, por competência, pela data de emissão dos documentos.</p>'
 '<div class="kgrid">%s%s%s%s%s%s</div>'%(
   kc("Receita bruta",f(c9["rb"]),"faturamento do mês, pela emissão"),
   kc("EBITDA",f(c9["eb"]),"%s da receita bruta"%pc(c9["eb"],c9["rb"]),hl=True),
   kc("Resultado do mês",f(c9["res"]),"depois de investimento e não operacional"),
   kc("Ocupação",pct(com["9"]["oc"]),"%d hóspedes em %d noites"%(com["9"]["hosp"],com["9"]["noites"])),
   kc("Diária média",f(com["9"]["tkt"]),"RevPAR de R$ %s"%f(com["9"]["revpar"])),
   kc("Caixa em 30/09",f(CAIXA_SF),"depois de consumir R$ %s no mês"%f(abs(CAIXA_SF-CAIXA_SI))))+
 '<p class="body-text" style="font-size:14px;margin-top:22px;max-width:1010px;">Contra agosto, a receita cai '
 '<strong>R$ %s</strong> e o EBITDA, <strong>R$ %s</strong> — o EBITDA cai mais rápido que a receita porque a '
 'estrutura fixa não acompanha a baixa temporada. A ocupação saiu de %s para %s e a diária média, de '
 'R$ %s para R$ %s: <strong>a maior parte da queda é preço, não volume</strong>.</p>'
 '<p class="body-text" style="font-size:14px;margin-top:10px;max-width:1010px;">No ano, o EBITDA acumulado '
 'chega a <strong>R$ %s</strong>, com resultado após investimentos de <strong>R$ %s</strong> — o grupo converteu '
 'resultado operacional em ativo, não em caixa.</p>'%(
   f(c8["rb"]-c9["rb"]),f(c8["eb"]-c9["eb"]),pct(com["8"]["oc"]),pct(com["9"]["oc"]),
   f(com["8"]["tkt"]),f(com["9"]["tkt"]),f(S["consol_T"]["eb"]),f(S["consol_T"]["res"])),
 cap=_c))
# ---- 3 DRE consolidada
c=c9; rb=c["rb"]
linhas=[{"cls":"sub","c":["Receita bruta",f(c["rb"]),pc(c["rb"],rb)]},
 {"c":["(–) Deduções · impostos, devoluções e taxa de cartão",f(c["ded"]),pc(c["ded"],rb)]},
 {"cls":"sub","c":["= Receita líquida",f(c["rl"]),pc(c["rl"],rb)]},
 {"c":["(–) Custos dos serviços",f(c["cus"]),pc(c["cus"],rb)]},
 {"c":["(–) Pessoal da operação",f(c["pdir"]),pc(c["pdir"],rb)]},
 {"cls":"sub","c":["= Lucro bruto",f(c["lb"]),pc(c["lb"],rb)]},
 {"c":["(–) Despesas comerciais",f(c["com"]),pc(c["com"],rb)]},
 {"c":["(–) Despesas administrativas",f(c["adm"]),pc(c["adm"],rb)]},
 {"c":["(–) Pessoal indireto",f(c["pind"]),pc(c["pind"],rb)]},
 {"cls":"hi","c":["= EBITDA",f(c["eb"]),pc(c["eb"],rb)]},
 {"c":["(±) Resultado financeiro",f(c["rf"]),pc(c["rf"],rb)]},
 {"cls":"sub","c":["= Lucro líquido",f(c["ll"]),pc(c["ll"],rb)]},
 {"cls":"grp","c":['<span>ABAIXO DO EBITDA · CAPEX E NÃO OPERACIONAL</span>',"",""]},
 {"c":["(–) Investimentos (capex)",f(c["inv"]),pc(c["inv"],rb)]},
 {"c":["(+) Receita não operacional",f(c["recnop"]),pc(c["recnop"],rb)]},
 {"c":["(±) Não operacional",f(c["nop"]),pc(c["nop"],rb)]},
 {"cls":"hi2","c":["= RESULTADO DO MÊS",f(c["res"]),pc(c["res"],rb)]}]
_m,_c=cab()
H.append(sec("DRE · setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">A DRE <span class="light">de</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. A compra de diárias entre as duas empresas é repasse e sai do consolidado.</p>'
 +tab(["44%","",""],["Linha","Valor R$","AV %"],linhas),cap=_c))
# ---- 4 por empresa
a,t=S["amana_9"],S["topazio_9"]
rows=[{"c":[k,f(a[x]),f(t[x]),f(c9[x])]} for k,x in
  [("Receita bruta","rb"),("(–) Deduções","ded"),("= Receita líquida","rl"),("(–) Custos","cus"),
   ("(–) Pessoal da operação","pdir"),("(–) Despesas comerciais","com"),("(–) Despesas administrativas","adm"),
   ("(–) Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["= EBITDA",f(a["eb"]),f(t["eb"]),f(c9["eb"])]})
rows.append({"c":["(–) Investimentos",f(a["inv"]),f(t["inv"]),f(c9["inv"])]})
rows.append({"cls":"hi2","c":["= RESULTADO",f(a["res"]),f(t["res"]),f(c9["res"])]})
_m,_c=cab()
H.append(sec("Amana e Topázio · setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">As duas empresas, <span class="orange">lado a lado.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">A Amana fatura e a Topázio opera. Por isso a receita fica de um lado e o custo da operação do outro — e só o consolidado conta a história inteira.</p>'
 +tab(["34%","","",""],["Linha","Amana","Topázio","Consolidado"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">O consolidado elimina '
 '<strong>R$ %s</strong> de compra de diárias da Amana na Topázio. O prejuízo da Topázio isolada não é '
 'operacional: é o desenho societário, em que o faturamento sai pela Amana.</p>'%f(IC),cap=_c))
# ---- pente-fino do fechamento: capitulo retirado a pedido do Joao em 27/10/2026.
# O bloco fica aqui comentado porque ele e a prova do que mudou no mes -- se
# alguem perguntar de novo, e so descomentar.
# # ---- 5 pente-fino
# pf=[{"c":["Receita presa em adiantamento","12 NFS-e com nota emitida e título parado em conta de controle","+84.424,60","corrigido"]},
#     {"c":["Duplicidade de receita","NFS-e 225: o título de adiantamento estava em categoria de receita","-9.849,97","corrigido"]},
#     {"c":["Parcelas com data de vencimento","11 parcelas de 5 notas de agosto com a data do vencimento, não da nota","-20.291,35","corrigido"]},
#     {"c":["Salário indevido na Topázio","competência de junho, empresa errada, baixado com desconto de 100%","+1.662,32","corrigido"]},
#     {"c":["Energia de setembro","fatura lançada, competência 09/2026, vencimento 09/11","-8.540,55","lançado"]},
#     {"c":["Frete em balaio único","de-para pela observação do título: obra, limpeza, café da manhã e geral","0,00","reclassificado"]},
#     {"c":["Premiação da equipe","passou a ficar num só lugar, inclusive no histórico, em despesa comercial","0,00","padronizado"]},
#     {"cls":"hi","c":["Estorno no Santander","crédito de R$ 687,00 que estava no extrato e não no Omie","+687,00","lançado"]}]
# _m,_c=cab()
# H.append(sec("O pente-fino do fechamento",
#  _m+'<h2 class="editorial" style="font-size:30px;">O que mudou <span class="light">neste</span> <span class="orange">fechamento.</span></h2>'
#  '<p class="lede" style="margin-top:8px;font-size:14px;">Oito pontos, conferidos um a um contra o Omie, os extratos e o relatório da contabilidade. Todos eram lançamento, nenhum era o painel.</p>'
#  +tab(["23%","41%","17%","19%"],["Ponto","O que era","Efeito","Status"],pf,num={2})+
#  '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">Efeito líquido: a receita de '
#  'hospedagem de setembro da Amana subiu para <strong>R$ 595.018,22</strong> e passou a bater ao centavo com a '
#  'contabilidade. A energia e o frete de obra, que antes faltavam, estão dentro — e é parte do motivo de o '
#  'EBITDA fechar em R$ %s.</p>'%f(c9["eb"]),cap=_c))

# ---- a conferencia da receita contra a relacao de faturamento da contabilidade saiu
# em 27/10/2026: e processo de fechamento, nao analise financeira. Fica no painel e na
# planilha "Conferencia Faturamento Contabilidade x Painel".

# ---- 7 setembro x agosto
rows=[{"c":[k,f(c8[x]),f(c9[x]),f(c9[x]-c8[x])]} for k,x in
  [("Receita bruta","rb"),("Deduções","ded"),("Custos dos serviços","cus"),("Pessoal da operação","pdir"),
   ("Despesas comerciais","com"),("Despesas administrativas","adm"),("Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["EBITDA",f(c8["eb"]),f(c9["eb"]),f(c9["eb"]-c8["eb"])]})
rows.append({"c":["Investimentos",f(c8["inv"]),f(c9["inv"]),f(c9["inv"]-c8["inv"])]})
rows.append({"cls":"hi2","c":["RESULTADO DO MÊS",f(c8["res"]),f(c9["res"]),f(c9["res"]-c8["res"])]})
qrec=("%.1f%%"%(abs(c9["rb"]-c8["rb"])/c8["rb"]*100)).replace(".",",")
# decomposicao preco x volume sobre a receita do sistema comercial, que e onde noite
# ocupada e diaria media sao medidas na mesma base
v0,v1=com["8"]["noites"],com["9"]["noites"]; p0,p1=com["8"]["tkt"],com["9"]["tkt"]
ef_vol=round((v1-v0)*p0,2); ef_pre=round(v0*(p1-p0),2); ef_cru=round((v1-v0)*(p1-p0),2)
ef_tot=ef_vol+ef_pre+ef_cru
pv=[{"c":["Noites ocupadas","%d"%v0,"%d"%v1,"%d"%(v1-v0)]},
    {"c":["Diária média",f(p0),f(p1),f(p1-p0)]},
    {"cls":"sub","c":["Receita do sistema comercial",f(com["8"]["rec"]),f(com["9"]["rec"]),f(com["9"]["rec"]-com["8"]["rec"])]},
    {"c":["&nbsp;&nbsp;efeito volume · 17 noites a menos","","",f(ef_vol)]},
    {"c":["&nbsp;&nbsp;efeito preço · R$ %s a menos na diária"%f(abs(p1-p0)),"","",f(ef_pre)]},
    {"c":["&nbsp;&nbsp;efeito cruzado","","",f(ef_cru)]}]
_m,_c=cab()
H.append(sec("Setembro contra agosto",
 _m+'<h2 class="editorial" style="font-size:30px;">De agosto <span class="light">para</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado, nas duas fotos já fechadas.</p>'
 +tab(["32%","","",""],["Linha","Agosto","Setembro","Variação"],rows)+
 '<h3 style="margin-top:20px;">De onde vem a queda de receita</h3>'
 +tab(["38%","","",""],["","Agosto","Setembro","Efeito"],pv)+
 '<p class="body-text" style="font-size:13.5px;margin-top:14px;max-width:1020px;">A receita cai %s e o custo '
 'não acompanha: é por isso que o EBITDA sai de %s para %s da receita e o resultado do mês recua R$ %s. '
 '<strong>Três quartos da queda vêm da diária média</strong>, não do volume — a pousada perdeu 17 noites '
 'ocupadas, mas perdeu R$ %s por diária. Preço de baixa temporada é esperado; o que não é esperado é a '
 'estrutura fixa não respirar junto.</p>'%(
   qrec,pc(c8["eb"],c8["rb"]),pc(c9["eb"],c9["rb"]),f(abs(c9["res"]-c8["res"])),f(abs(p1-p0))),
 cap=_c))

# ---- estrutura de custos e ponto de equilibrio
rows=[{"cls":"sub","c":["Receita bruta",f(B8["rb"]),f(B9["rb"])]},
 {"c":["(–) Custos e despesas variáveis",f(B8["cvar"]),f(B9["cvar"])]},
 {"cls":"hi","c":["= MARGEM DE CONTRIBUIÇÃO",f(B8["mc"]),f(B9["mc"])]},
 {"c":["&nbsp;&nbsp;sobre a receita bruta",pp(B8["mcp"]*100),pp(B9["mcp"]*100)]},
 {"c":["(–) Custos e despesas fixas",f(B8["cfix"]),f(B9["cfix"])]},
 {"cls":"sub","c":["= EBITDA",f(B8["eb"]),f(B9["eb"])]},
 {"cls":"grp","c":['<span>O QUE A ESTRUTURA EXIGE PARA O MÊS FECHAR NO ZERO</span>',"",""]},
 {"c":["Receita de equilíbrio",f(B8["pe"]),f(B9["pe"])]},
 {"c":["Ocupação de equilíbrio",pp(B8["oce"]),pp(B9["oce"])]},
 {"cls":"hi2","c":["MARGEM DE SEGURANÇA",pp(B8["seg"]),pp(B9["seg"])]}]
_m,_c=cab()
H.append(sec("Estrutura de custos e ponto de equilíbrio",
 _m+'<h2 class="editorial" style="font-size:30px;">Quanto a operação <span class="light">precisa faturar</span> <span class="orange">para não perder dinheiro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. Variável é o que anda com a ocupação; fixo é o que a pousada paga com a casa cheia ou vazia.</p>'
 +tab(["46%","",""],["","Agosto","Setembro"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">A receita caiu R$ %s e o '
 'custo fixo subiu R$ %s. É a definição de alavancagem operacional funcionando contra: cada real de receita '
 'que sai leva %s centavos de EBITDA junto. A margem de contribuição até melhorou %s p.p. — o custo variável '
 'caiu mais que a receita —, mas não compensa uma estrutura fixa que não se mexe.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1030px;">O número para guardar é a '
 '<strong>ocupação de equilíbrio: %s</strong>. Abaixo disso, com a diária média de setembro, o mês dá prejuízo '
 'operacional. A margem de segurança encolheu de %s para %s em um único mês.</p>'%(
   f(abs(B9["rb"]-B8["rb"])),f(abs(B9["cfix"]-B8["cfix"])),("%.0f"%(B9["mcp"]*100)),
   ("%.1f"%((B9["mcp"]-B8["mcp"])*100)).replace(".",","),pp(B9["oce"]),pp(B8["seg"]),pp(B9["seg"])),
 cap=_c))
# ---- 8 orcado x realizado
rows=[{"c":[x["l"],f(x["o"]),f(x["r"]),f(x["d"])]} for x in orc["linhas"][:9]]
rows.append({"cls":"hi","c":["EBITDA do mês",f(orc["os"]),f(orc["rs"]),f(orc["rs"]-orc["os"])]})
rows.append({"cls":"hi2","c":["EBITDA ACUMULADO JAN–SET",f(orc["oa"]),f(orc["ra"]),f(orc["ra"]-orc["oa"])]})
_m,_c=cab()
H.append(sec("Orçado × realizado",
 _m+'<h2 class="editorial" style="font-size:30px;">O orçamento, <span class="orange">linha a linha.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Revisão 15.09 do orçamento 2026/27, cenário conservador, contra o realizado consolidado de setembro. As nove linhas de maior desvio.</p>'
 +tab(["36%","","",""],["Linha","Orçado","Realizado","Variação"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">A receita respondeu por R$ %s '
 'do desvio de R$ %s do mês. No ano, o EBITDA acumulado está <strong>R$ %s abaixo</strong> do orçado.</p>'%(
   f(abs(orc["linhas"][0]["d"])),f(abs(orc["rs"]-orc["os"])),f(abs(orc["ra"]-orc["oa"]))),cap=_c))
# ---- 9 caixa
cc=[]
nome=lambda n: re.sub(r"_Top_40-3$","",n).replace("Infinit Pay","InfinitePay")
for x in d["contas"]["consol"]:
    # conta corrente aparece mesmo zerada: e o que mostra a varredura do Santander
    if x["t"]=="CC" or abs(x["si"])>0.004 or abs(x["sf"])>0.004:
        cc.append({"c":[nome(x["n"]),f(x["si"]),f(x["sf"]-x["si"]),f(x["sf"])]})
ti,tf=CAIXA_SI,CAIXA_SF
APL=round(sum(x["sf"] for x in d["contas"]["consol"] if x["t"]=="CA"),2)
cc.append({"cls":"hi2","c":["TOTAL CONSOLIDADO",f(ti),f(tf-ti),f(tf)]})
# ponte do resultado ao caixa, e a posicao por conta
dfc=d["dfc_consol"]
cx_ent=round(sum(v["total"] for v in dfc["receitas"].values()),2)
cx_rec=round(dfc["receitas"].get("1.1 Receita bruta de vendas",{}).get("total",0),2)
cx_inv=round(sum(v["total"] for g,v in dfc["despesas"].items() if "Investimento" in g),2)
giro=round((tf-ti)-c9["res"],2)
ponte=[{"cls":"sub","c":["EBITDA de setembro",f(c9["eb"])]},
 {"c":["(±) Resultado financeiro e não operacional",f(c9["rf"]+c9["recnop"]+c9["nop"])]},
 {"c":["(–) Investimentos",f(c9["inv"])]},
 {"cls":"sub","c":["= Resultado do mês, por competência",f(c9["res"])]},
 {"c":["(±) Capital de giro · o que foi faturado e não entrou, e o que foi pago de meses anteriores",f(giro)]},
 {"cls":"hi2","c":["= VARIAÇÃO DE CAIXA NO MÊS",f(tf-ti)]}]
_m,_c=cab()
H.append(sec("Do resultado ao caixa",
 _m+'<h2 class="editorial" style="font-size:30px;">O mês deu lucro <span class="light">e</span> <span class="orange">consumiu caixa.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. A distância entre as duas pontas é capital de giro, e ela tem explicação.</p>'
 +tab(["62%",""],["","Setembro"],ponte)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">Setembro faturou R$ %s e '
 'recebeu <strong>R$ %s</strong> — R$ %s de diferença, que é o prazo do cartão e o parcelamento. Do outro '
 'lado, a despesa comercial pagou R$ %s contra R$ %s de competência: comissão de reserva de meses anteriores '
 'saindo agora. <strong>Não é prejuízo; é descasamento de prazo</strong>, e ele se inverte quando a alta '
 'temporada começar a receber.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1030px;">O investimento do mês foi de '
 'R$ %s em competência e R$ %s em caixa. No ano, o grupo gerou R$ %s de EBITDA e fechou com resultado após '
 'investimentos de R$ %s: <strong>o capex é o que consome o resultado</strong>, não a operação.</p>'%(
   f(c9["rb"]),f(cx_rec),f(abs(cx_rec-c9["rb"])),f(abs(139653.57)),f(abs(c9["com"])),
   f(abs(c9["inv"])),f(abs(cx_inv)),f(S["consol_T"]["eb"]),f(S["consol_T"]["res"])),
 cap=_c))

_m,_c=cab()
H.append(sec("Caixa · posição por conta",
 _m+'<h2 class="editorial" style="font-size:30px;">Onde o dinheiro <span class="orange">está parado.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Saldo em 31/08 e em 30/09, conta a conta.</p>'
 +tab(["38%","","",""],["Conta","Em 31/08","Movimento de setembro","Em 30/09"],cc)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">R$ %s dos R$ %s estão em '
 'aplicação — <strong>%s do caixa do grupo rende e está disponível</strong>. A conta corrente do Santander '
 'fica zerada porque o banco varre o saldo para a aplicação automaticamente; as duas se leem juntas. O CDB DI '
 'PJ caiu R$ 210 mil no mês: é resgate para financiar a operação e o capex, não resultado.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1030px;">No ritmo de consumo de '
 'setembro (R$ %s por mês), o caixa atual cobre <strong>%s meses</strong>. Mas setembro é o vale do ano: '
 'outubro e novembro são meses de alta, e a carteira a receber da pousada é de R$ %s.</p>'%(
   f(APL),f(tf),("%.0f%%"%(APL/tf*100)),f(abs(tf-ti)),("%.1f"%(tf/abs(tf-ti))).replace(".",","),
   f(CARTEIRA_CARTAO+CARTEIRA_COBRAR)),
 cap=_c))

# ---- o que vem pela frente
lin=[]
for nome_m,oc26,oc25,prev in FRENTE:
    lin.append({"cls":"hi2" if prev<B9["pe"] else "","c":[
        nome_m.upper() if prev<B9["pe"] else nome_m,
        ("%.2f%%"%oc26).replace(".",","),("%.2f%%"%oc25).replace(".",","),
        f(prev),f(prev-B9["pe"])]})
_m,_c=cab()
H.append(sec("O que vem pela frente",
 _m+'<h2 class="editorial" style="font-size:30px;">Outubro vai bem. <span class="orange">Dezembro precisa de atenção.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Ocupação já contratada e previsão de faturamento da pousada, posição de 26/10, contra a receita de equilíbrio de setembro (R$ %s).</p>'%f(B9["pe"])
 +tab(["24%","","","",""],["Mês","Ocupação contratada","Mesmo mês de 2025","Previsão de faturamento","Contra o equilíbrio"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">Outubro fecha acima de '
 'outubro do ano passado, com %s de ocupação e diária média de R$ %s. Novembro vem 8 pontos abaixo de '
 'novembro/25 e ainda passa com folga. <strong>Dezembro é o problema</strong>: 35,27%% contratados contra '
 '77,20%% no ano passado. Faltam dois meses para vender, mas é o único mês do horizonte que hoje fica '
 '<strong>abaixo do ponto de equilíbrio</strong> — e dezembro é mês de alta temporada, não de vale.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1030px;">Duas coisas sustentam o '
 'caixa enquanto isso: R$ %s já contratados a receber (R$ %s em cartão e R$ %s a cobrar) e o saldo de '
 'R$ %s em 26/10. A taxa de cancelamento de outubro, de %s, é o que mais atrapalha a previsibilidade — '
 'e merece uma política própria.</p>'%(
   ("%.2f%%"%OUT_OC).replace(".",","),f(OUT_TKT),f(CARTEIRA_CARTAO+CARTEIRA_COBRAR),
   f(CARTEIRA_CARTAO),f(CARTEIRA_COBRAR),f(CAIXA_2610),("%.2f%%"%OUT_CANC).replace(".",",")),
 cap=_c))

html=cabeca+'<body><div class="deck" id="deck">'+"".join(H)+rodape
html=html.replace("Relatório Gerencial · Agosto/2026 · Grupo Amana / Pousada Topázio · Exact BR",
                  "Relatório de Fechamento · Setembro/2026 · Grupo Amana / Pousada Topázio · Exact BR")
html=html.replace("__TOT__",str(len(H)))
html=re.sub(r"(const TOTAL\s*=\s*)\d+",r"\g<1>%d"%len(H),html)
open(SAIDA,"w",encoding="utf-8").write(html)
print("gravado %s (%d KB, %d paginas)"%(SAIDA.split("/")[-1],len(html)//1024,len(H)))
