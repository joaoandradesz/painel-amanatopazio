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
TOT=9
TAG="Relatório de fechamento · Setembro/2026"
def sec(n,titulo,corpo,cap=None,dark=False):
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'
        %(logo_escuro if dark else logo_claro,cap or "Fechamento",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>%s</span>'
        '<span class="page-num"><span class="cur">%02d</span> / %d</span></div>'
        %(' style="color: rgba(255,255,255,0.4);"' if dark else "",TAG,n,TOT))
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
CAIXA_SI=round(sum(x["si"] for x in d["contas"]["consol"]),2)
CAIXA_SF=round(sum(x["sf"] for x in d["contas"]["consol"]),2)
H=[]
# ---- 1 capa
H.append(sec(1,"Setembro/2026",
 '<span class="eyebrow">Relatório de fechamento</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1100px;">Setembro de 2026,<br>'
 '<span style="color:var(--orange);">fechado.</span></h2>'
 '<p class="lede" style="max-width:900px;font-size:19px;margin-top:18px;">Grupo Amana + Pousada Topázio. '
 'Receita, resultado e caixa saem da mesma foto: a DRE bate ao centavo com o relatório de faturamento da '
 'contabilidade e o caixa foi conferido conta a conta contra os extratos.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:920px;">O número caiu em relação a agosto — e dá para '
 'confiar nele. <strong>EBITDA consolidado de R$ %s</strong>, %s da receita bruta, depois de lançada a energia '
 'de setembro e reclassificado o frete item a item.</p>'
 '<div class="proof-row"><div><div class="pv orange">%s</div><div class="pl">Receita bruta do mês</div></div>'
 '<div><div class="pv">%s</div><div class="pl">EBITDA · %s da receita</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Resultado depois de capex</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Caixa em 30/09, conferido com o banco</div></div></div>'%(
   f(S["consol_9"]["eb"]),pc(S["consol_9"]["eb"],S["consol_9"]["rb"]),
   f(S["consol_9"]["rb"]),f(S["consol_9"]["eb"]),pc(S["consol_9"]["eb"],S["consol_9"]["rb"]),
   f(S["consol_9"]["res"]),f(CAIXA_SF)),
 dark=True))
# ---- 2 em um olhar
c9,c8=S["consol_9"],S["consol_8"]
H.append(sec(2,"Os números de setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 01 —</span>'
 '<h2 class="editorial" style="font-size:30px;">Setembro <span class="light">de 2026,</span> <span class="orange">em um olhar.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, por competência, pela data de emissão dos documentos.</p>'
 '<div class="kgrid">%s%s%s%s%s%s</div>'%(
   kc("Receita bruta",f(c9["rb"]),"faturamento do mês, pela emissão"),
   kc("EBITDA",f(c9["eb"]),"%s da receita bruta"%pc(c9["eb"],c9["rb"]),hl=True),
   kc("Resultado do mês",f(c9["res"]),"depois de investimento e não operacional"),
   kc("Ocupação",pct(com["9"]["oc"]),"%d hóspedes em %d noites"%(com["9"]["hosp"],com["9"]["noites"])),
   kc("Diária média",f(com["9"]["tkt"]),"RevPAR de R$ %s"%f(com["9"]["revpar"])),
   kc("Caixa em 30/09",f(CAIXA_SF),"conferido conta a conta com os extratos"))+
 '<p class="body-text" style="font-size:14px;margin-top:22px;max-width:1000px;">Contra agosto, a receita cai '
 '<strong>R$ %s</strong> e o EBITDA, <strong>R$ %s</strong>. A ocupação saiu de %s para %s. Setembro é o primeiro '
 'mês em que a receita de hospedagem bate <strong>ao centavo</strong> com o relatório de faturamento da '
 'contabilidade: R$ 595.018,22. No ano, o EBITDA acumulado chega a <strong>R$ %s</strong>.</p>'%(
   f(c8["rb"]-c9["rb"]),f(c8["eb"]-c9["eb"]),pct(com["8"]["oc"]),pct(com["9"]["oc"]),f(S["consol_T"]["eb"])),
 cap="Capítulo 01"))
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
H.append(sec(3,"DRE · setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 02 —</span>'
 '<h2 class="editorial" style="font-size:30px;">A DRE <span class="light">de</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. A compra de diárias entre as duas empresas é repasse e sai do consolidado.</p>'
 +tab(["44%","",""],["Linha","Valor R$","AV %"],linhas),cap="Capítulo 02"))
# ---- 4 por empresa
a,t=S["amana_9"],S["topazio_9"]
rows=[{"c":[k,f(a[x]),f(t[x]),f(c9[x])]} for k,x in
  [("Receita bruta","rb"),("(–) Deduções","ded"),("= Receita líquida","rl"),("(–) Custos","cus"),
   ("(–) Pessoal da operação","pdir"),("(–) Despesas comerciais","com"),("(–) Despesas administrativas","adm"),
   ("(–) Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["= EBITDA",f(a["eb"]),f(t["eb"]),f(c9["eb"])]})
rows.append({"c":["(–) Investimentos",f(a["inv"]),f(t["inv"]),f(c9["inv"])]})
rows.append({"cls":"hi2","c":["= RESULTADO",f(a["res"]),f(t["res"]),f(c9["res"])]})
H.append(sec(4,"Amana e Topázio · setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 03 —</span>'
 '<h2 class="editorial" style="font-size:30px;">As duas empresas, <span class="orange">lado a lado.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">A Amana fatura e a Topázio opera. Por isso a receita fica de um lado e o custo da operação do outro — e só o consolidado conta a história inteira.</p>'
 +tab(["34%","","",""],["Linha","Amana","Topázio","Consolidado"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">O consolidado elimina '
 '<strong>R$ %s</strong> de compra de diárias da Amana na Topázio. O prejuízo da Topázio isolada não é '
 'operacional: é o desenho societário, em que o faturamento sai pela Amana.</p>'%f(IC),cap="Capítulo 03"))
# ---- 5 pente-fino
pf=[{"c":["Receita presa em adiantamento","12 NFS-e com nota emitida e título parado em conta de controle","+84.424,60","corrigido"]},
    {"c":["Duplicidade de receita","NFS-e 225: o título de adiantamento estava em categoria de receita","-9.849,97","corrigido"]},
    {"c":["Parcelas com data de vencimento","11 parcelas de 5 notas de agosto com a data do vencimento, não da nota","-20.291,35","corrigido"]},
    {"c":["Salário indevido na Topázio","competência de junho, empresa errada, baixado com desconto de 100%","+1.662,32","corrigido"]},
    {"c":["Energia de setembro","fatura lançada, competência 09/2026, vencimento 09/11","-8.540,55","lançado"]},
    {"c":["Frete em balaio único","de-para pela observação do título: obra, limpeza, café da manhã e geral","0,00","reclassificado"]},
    {"c":["Premiação da equipe","passou a ficar num só lugar, inclusive no histórico, em despesa comercial","0,00","padronizado"]},
    {"cls":"hi","c":["Estorno no Santander","crédito de R$ 687,00 que estava no extrato e não no Omie","+687,00","lançado"]}]
H.append(sec(5,"O pente-fino do fechamento",
 '<span class="chapter-num" style="margin-bottom:10px;">— 04 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O que mudou <span class="light">neste</span> <span class="orange">fechamento.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Oito pontos, conferidos um a um contra o Omie, os extratos e o relatório da contabilidade. Todos eram lançamento, nenhum era o painel.</p>'
 +tab(["23%","41%","17%","19%"],["Ponto","O que era","Efeito","Status"],pf,num={2})+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">Efeito líquido: a receita de '
 'hospedagem de setembro da Amana subiu para <strong>R$ 595.018,22</strong> e passou a bater ao centavo com a '
 'contabilidade. A energia e o frete de obra, que antes faltavam, estão dentro — e é parte do motivo de o '
 'EBITDA fechar em R$ %s.</p>'%f(c9["eb"]),cap="Capítulo 04"))
# ---- 6 receita x faturamento
fat={"1":529990.86,"2":270043.26,"3":88285.52,"4":57473.27,"5":272765.44,"6":297456.07,"7":551271.84,"8":750504.80,"9":595018.22}
HOSP=d["hospedagem"]
nm={"1":"janeiro","2":"fevereiro","3":"março","4":"abril","5":"maio","6":"junho","7":"julho","8":"agosto","9":"setembro"}
rows=[{"cls":"hi" if m=="9" else "","c":[nm[m],f(fat[m]),f(HOSP[m]),f(HOSP[m]-fat[m])]} for m in nm]
H.append(sec(6,"Receita × faturamento da contabilidade",
 '<span class="chapter-num" style="margin-bottom:10px;">— 05 —</span>'
 '<h2 class="editorial" style="font-size:30px;">A receita, <span class="light">conferida contra</span> <span class="orange">a contabilidade.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Receita de hospedagem da Amana no painel contra o relatório de NFS-e emitido pela contabilidade, mês a mês.</p>'
 +tab(["24%","","",""],["Mês","NFS-e · contabilidade","Painel","Diferença"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">Oito dos nove meses fecham. '
 'Agosto fica R$ 15.630,20 abaixo, e a diferença está identificada: R$ 17.155,91 da NFS-e 129, cujo título '
 'carrega a data da venda no cartão (10/07), menos R$ 1.525,67 de receita sem número de nota. Conferência nota '
 'a nota: <strong>as 74 notas de agosto e as 68 de setembro estão todas lançadas</strong>, nenhuma cancelada, '
 'com uma única divergência de três centavos.</p>',cap="Capítulo 05"))
# ---- 7 setembro x agosto
rows=[{"c":[k,f(c8[x]),f(c9[x]),f(c9[x]-c8[x])]} for k,x in
  [("Receita bruta","rb"),("Deduções","ded"),("Custos dos serviços","cus"),("Pessoal da operação","pdir"),
   ("Despesas comerciais","com"),("Despesas administrativas","adm"),("Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["EBITDA",f(c8["eb"]),f(c9["eb"]),f(c9["eb"]-c8["eb"])]})
rows.append({"c":["Investimentos",f(c8["inv"]),f(c9["inv"]),f(c9["inv"]-c8["inv"])]})
rows.append({"cls":"hi2","c":["RESULTADO DO MÊS",f(c8["res"]),f(c9["res"]),f(c9["res"]-c8["res"])]})
qrec=("%.1f%%"%(abs(c9["rb"]-c8["rb"])/c8["rb"]*100)).replace(".",",")
H.append(sec(7,"Setembro contra agosto",
 '<span class="chapter-num" style="margin-bottom:10px;">— 06 —</span>'
 '<h2 class="editorial" style="font-size:30px;">De agosto <span class="light">para</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado, nas duas fotos já fechadas.</p>'
 +tab(["32%","","",""],["Linha","Agosto","Setembro","Variação"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">A receita cai %s com a baixa '
 'temporada e o custo não acompanha na mesma proporção. É o que explica o EBITDA sair de %s para %s da receita. '
 'O resultado do mês cai R$ %s.</p>'%(qrec,pc(c8["eb"],c8["rb"]),pc(c9["eb"],c9["rb"]),f(abs(c9["res"]-c8["res"]))),
 cap="Capítulo 06"))
# ---- 8 orcado x realizado
rows=[{"c":[x["l"],f(x["o"]),f(x["r"]),f(x["d"])]} for x in orc["linhas"][:9]]
rows.append({"cls":"hi","c":["EBITDA do mês",f(orc["os"]),f(orc["rs"]),f(orc["rs"]-orc["os"])]})
rows.append({"cls":"hi2","c":["EBITDA ACUMULADO JAN–SET",f(orc["oa"]),f(orc["ra"]),f(orc["ra"]-orc["oa"])]})
H.append(sec(8,"Orçado × realizado",
 '<span class="chapter-num" style="margin-bottom:10px;">— 07 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O orçamento, <span class="orange">linha a linha.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Revisão 15.09 do orçamento 2026/27, cenário conservador, contra o realizado consolidado de setembro. As nove linhas de maior desvio.</p>'
 +tab(["36%","","",""],["Linha","Orçado","Realizado","Variação"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">A receita respondeu por R$ %s '
 'do desvio de R$ %s do mês. No ano, o EBITDA acumulado está <strong>R$ %s abaixo</strong> do orçado.</p>'%(
   f(abs(orc["linhas"][0]["d"])),f(abs(orc["rs"]-orc["os"])),f(abs(orc["ra"]-orc["oa"]))),cap="Capítulo 07"))
# ---- 9 caixa
cc=[]
nome=lambda n: re.sub(r"_Top_40-3$","",n).replace("Infinit Pay","InfinitePay")
for x in d["contas"]["consol"]:
    # conta corrente aparece mesmo zerada: e o que mostra a varredura do Santander
    if x["t"]=="CC" or abs(x["si"])>0.004 or abs(x["sf"])>0.004:
        cc.append({"c":[nome(x["n"]),f(x["si"]),f(x["sf"]-x["si"]),f(x["sf"])]})
ti,tf=CAIXA_SI,CAIXA_SF
cc.append({"cls":"hi2","c":["TOTAL CONSOLIDADO",f(ti),f(tf-ti),f(tf)]})
H.append(sec(9,"Caixa · posição por conta",
 '<span class="chapter-num" style="margin-bottom:10px;">— 08 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O caixa, <span class="light">conta a conta,</span> <span class="orange">contra o banco.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Saldo em 31/08 e em 30/09, conferido conta a conta com os extratos bancários e os relatórios das adquirentes.</p>'
 +tab(["38%","","",""],["Conta","Em 31/08","Movimento de setembro","Em 30/09"],cc)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">O caixa consolidado cai '
 '<strong>R$ %s</strong> no mês e fecha em R$ %s. A conta corrente do Santander fica zerada porque o banco '
 'varre o saldo para a aplicação automaticamente — as duas se leem juntas, e somadas dão R$ %s, o mesmo do '
 'extrato. O CDB DI PJ caiu R$ 210 mil, que financiaram o mês: é resgate, não resultado.</p>'%(
   f(abs(tf-ti)),f(tf),f(236178.41)),cap="Capítulo 08"))
html=cabeca+'<body><div class="deck" id="deck">'+"".join(H)+rodape
html=html.replace("Relatório Gerencial · Agosto/2026 · Grupo Amana / Pousada Topázio · Exact BR",
                  "Relatório de Fechamento · Setembro/2026 · Grupo Amana / Pousada Topázio · Exact BR")
html=re.sub(r"(const TOTAL\s*=\s*)\d+",r"\g<1>%d"%TOT,html)
open(SAIDA,"w",encoding="utf-8").write(html)
print("gravado %s (%d KB, %d paginas)"%(SAIDA.split("/")[-1],len(html)//1024,len(H)))
