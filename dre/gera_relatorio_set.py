# -*- coding: utf-8 -*-
"""Pre-relatorio gerencial de setembro/2026 no mesmo modelo do de agosto.
   Reaproveita head, CSS, logos e scripts do relatorio de agosto e reescreve o corpo."""
import json,re,os,datetime
BASE=os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/")
MODELO=BASE+"Relatorio_Gerencial_Amana_Topazio_ago2026_v2.html"
SAIDA=BASE+"PRE_Relatorio_Gerencial_Amana_Topazio_set2026.html"
d=json.load(open("/Users/joaoandrade/painel-amanatopazio/dre/dados_rel.json")); orc=json.load(open("/Users/joaoandrade/painel-amanatopazio/dre/orc2.json"))
cx=json.load(open(os.path.expanduser("~/painel-amanatopazio/caixa/dados_caixa.json")))
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
pc=lambda v,b: ("%.1f%%"%(abs(v)/b*100)).replace(".",",") if b else "—"
S=d["casc"]; com=d["com"]
mod=open(MODELO,encoding="utf-8").read()
import collections as _c
_u=re.findall(r'<img class="logo" src="(data:image/[^"]+)"',mod)
_cnt=_c.Counter(_u); _ord=[k for k,_ in _cnt.most_common()]
logo_claro=_ord[0]      # o que aparece nos slides claros (14x)
logo_escuro=_ord[-1]    # o dos slides escuros (capa e fechamento)
logo_b=logo_claro
cabeca=mod[:mod.index("</head>")+7]
rodape=mod[mod.rindex("</section>")+10:]
TOT=11
def sec(n,titulo,corpo,cap=None,dark=False,capn=""):
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'%(logo_escuro if dark else logo_claro,cap or "Pré-relatório",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>Pré-relatório · Setembro/2026 · revisão em curso</span>'
        '<span class="page-num"><span class="cur">%02d</span> / %d</span></div>'%(' style="color: rgba(255,255,255,0.4);"' if dark else "",n,TOT))
    return '<section class="slide%s" data-slide="%d">%s<div class="s-body">%s</div>%s</section>\n'%(" dark" if dark else "",n,hd,corpo,ft)
def kc(l,v,dd,hl=False): return '<div class="kc"><div class="kl">%s</div><div class="kv%s">%s</div><div class="kd">%s</div></div>'%(l,' hl' if hl else '',v,dd)
def tab(cols,head,rows,cls="dtab xs",num=None):
    N=(lambda i: i>0) if num is None else (lambda i: i in num)
    h="".join('<th%s>%s</th>'%(' class="n"' if N(i) else '',c) for i,c in enumerate(head))
    b=""
    for r in rows:
        k=r.get("cls","")
        tds="".join('<td%s>%s</td>'%(' class="n%s"'%(" neg" if (isinstance(v,str) and v.startswith("-")) else "") if N(i) else '',v) for i,v in enumerate(r["c"]))
        b+='<tr class="%s">%s</tr>'%(k,tds)
    cg="".join('<col%s>'%(' style="width:%s"'%c if c else '') for c in cols)
    return '<table class="%s"><colgroup>%s</colgroup><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'%(cls,cg,h,b)
H=[]
# 1 capa
H.append(sec(1,"Setembro/2026",
 '<span class="eyebrow">Pré-relatório · fechamento em revisão</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1100px;">Setembro de 2026,<br><span style="color:var(--orange);">depois do pente-fino.</span></h2>'
 '<p class="lede" style="max-width:880px;font-size:19px;margin-top:18px;">Grupo Amana + Pousada Topázio. Os cinco apontamentos do fechamento foram conferidos um a um; três estão corrigidos e dois dependem de documento que ainda não chegou.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:900px;"><strong>Por que pré-relatório:</strong> falta a fatura de energia de setembro, que não está lançada nem paga, e o de-para dos fretes da Alem-Mar. Os dois entram no custo e vão reduzir o resultado. Tudo o mais já está conferido contra o Omie, os extratos e o relatório de faturamento da contabilidade.</p>',
 cap="Pré-relatório",dark=True))
# 2 em um olhar
H.append(sec(2,"Os números de setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 01 —</span>'
 '<h2 class="editorial" style="font-size:30px;">Setembro <span class="light">de 2026,</span> <span class="orange">em um olhar.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, por competência, pela data de emissão dos documentos.</p>'
 '<div class="kgrid">%s%s%s%s</div>'%(
   kc("Receita bruta",f(S["consol_9"]["rb"]),"faturamento do mês, pela emissão"),
   kc("EBITDA",f(S["consol_9"]["eb"]),"%s da receita bruta"%pc(S["consol_9"]["eb"],S["consol_9"]["rb"]),hl=True),
   kc("Resultado do mês",f(S["consol_9"]["res"]),"depois de investimento e não operacional"),
   kc("Ocupação",("%.2f%%"%com["9"]["oc"]).replace(".",","),"diária média de R$ %s"%f(com["9"]["tkt"])))+
 '<p class="body-text" style="font-size:14px;margin-top:22px;max-width:980px;">Contra agosto revisado, a receita cai <strong>R$ %s</strong> e o EBITDA, <strong>R$ %s</strong>. A ocupação saiu de 84,73%% para %s. Setembro é o primeiro mês em que a receita bate <strong>ao centavo</strong> com o relatório de faturamento da contabilidade: R$ 595.018,22 de hospedagem.</p>'%(
   f(S["consol_8"]["rb"]-S["consol_9"]["rb"]),f(S["consol_8"]["eb"]-S["consol_9"]["eb"]),("%.2f%%"%com["9"]["oc"]).replace(".",",")),
 cap="Capítulo 01"))
# 3 DRE consolidada
c=S["consol_9"]; rb=c["rb"]
linhas=[{"cls":"sub","c":["Receita bruta",f(c["rb"]),pc(c["rb"],rb)]},
 {"c":["(–) Deduções · impostos, devoluções e taxa de cartão",f(c["ded"]),pc(c["ded"],rb)]},
 {"cls":"sub","c":["= Receita líquida",f(c["rl"]),pc(c["rl"],rb)]},
 {"c":["(–) Custos dos serviços",f(c["cus"]),pc(c["cus"],rb)]},
 {"c":["(–) Pessoal direto",f(c["pdir"]),pc(c["pdir"],rb)]},
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
 {"cls":"tot","c":["= Resultado do mês",f(c["res"]),pc(c["res"],rb)]}]
H.append(sec(3,"DRE · setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 02 —</span>'
 '<h2 class="editorial" style="font-size:30px;">A DRE <span class="light">de</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. A compra de diárias entre as duas empresas é repasse e sai do consolidado.</p>'+
 tab(["44%","",""],["Linha","Valor R$","AV %"],linhas),cap="Capítulo 02"))
# 4 por empresa
a,t=S["amana_9"],S["topazio_9"]
rows=[{"c":[k,f(a[c]),f(t[c]),f(S["consol_9"][c])]} for k,c in
  [("Receita bruta","rb"),("(–) Deduções","ded"),("= Receita líquida","rl"),("(–) Custos","cus"),
   ("(–) Pessoal direto","pdir"),("(–) Despesas comerciais","com"),("(–) Despesas administrativas","adm"),
   ("(–) Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["= EBITDA",f(a["eb"]),f(t["eb"]),f(S["consol_9"]["eb"])]})
rows.append({"c":["(–) Investimentos","%s"%f(a["inv"]),f(t["inv"]),f(S["consol_9"]["inv"])]})
rows.append({"cls":"tot","c":["= Resultado",f(a["res"]),f(t["res"]),f(S["consol_9"]["res"])]})
H.append(sec(4,"Amana e Topázio · setembro/2026",
 '<span class="chapter-num" style="margin-bottom:10px;">— 03 —</span>'
 '<h2 class="editorial" style="font-size:30px;">As duas empresas, <span class="orange">lado a lado.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">A Amana fatura e a Topázio opera. Por isso a receita fica de um lado e o custo da operação do outro — e só o consolidado conta a história inteira.</p>'+
 tab(["34%","","",""],["Linha","Amana","Topázio","Consolidado"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">O consolidado elimina <strong>R$ 112.981,31</strong> de compra de diárias da Amana na Topázio. O prejuízo da Topázio isolada não é operacional: é o desenho societário, em que o faturamento sai pela Amana.</p>',
 cap="Capítulo 03"))
# 5 pente-fino
pf=[{"c":["Receita presa em adiantamento","12 NFS-e com nota emitida e título parado em conta de controle","+84.424,60","corrigido"]},
    {"c":["Duplicidade de receita","NFS-e 225: o título de adiantamento estava na categoria de receita","-9.849,97","corrigido"]},
    {"c":["Parcelas com data de vencimento","11 parcelas de 5 notas de agosto com a data do vencimento, não da nota","-20.291,35","corrigido"]},
    {"c":["Salário indevido na Topázio","competência de junho, empresa errada, baixado com desconto de 100%","+1.662,32","corrigido"]},
    {"c":["Material de consumo","18 títulos num balaio único, caindo como insumo de revenda","0,00","reclassificado"]},
    {"cls":"hi2","c":["Energia de setembro","fatura não lançada e, pelo extrato, não paga","a lançar","pendente"]},
    {"cls":"hi2","c":["Frete de insumo","R$ 9.431,70 da Alem-Mar num balde só, sem separar por insumo","a reclassificar","pendente"]}]
H.append(sec(5,"O pente-fino do fechamento",
 '<span class="chapter-num" style="margin-bottom:10px;">— 04 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O que mudou <span class="light">nesta</span> <span class="orange">revisão.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Cinco apontamentos do controller, conferidos um a um contra o Omie. Todos eram lançamento, nenhum era o painel.</p>'+
 tab(["24%","42%","18%","16%"],["Ponto","O que era","Efeito","Status"],pf,num={2})+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">Efeito líquido já aplicado: a receita de setembro da Amana subiu de R$ 540.734,94 para <strong>R$ 595.018,22</strong> e passou a bater ao centavo com a contabilidade. Agosto subiu para R$ 734.874,60.</p>',
 cap="Capítulo 04"))
# 6 faturamento x receita
fat={"1":529990.86,"2":270043.26,"3":88285.52,"4":57473.27,"5":272765.44,"6":297456.07,"7":551271.84,"8":750504.80,"9":595018.22}
pan={"1":529990.86,"2":270043.26,"3":88285.52,"4":57473.27,"5":272765.44,"6":297456.07,"7":551271.84,"8":734874.60,"9":595018.22}
nm={"1":"janeiro","2":"fevereiro","3":"março","4":"abril","5":"maio","6":"junho","7":"julho","8":"agosto","9":"setembro"}
rows=[{"cls":"hi" if m=="9" else "","c":[nm[m],f(fat[m]),f(pan[m]),f(pan[m]-fat[m])]} for m in nm]
H.append(sec(6,"Receita × faturamento da contabilidade",
 '<span class="chapter-num" style="margin-bottom:10px;">— 05 —</span>'
 '<h2 class="editorial" style="font-size:30px;">A receita, <span class="light">conferida contra</span> <span class="orange">a contabilidade.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Receita de hospedagem da Amana no painel contra o relatório de NFS-e emitido pela JC Buarque, mês a mês.</p>'+
 tab(["24%","","",""],["Mês","NFS-e · contabilidade","Painel","Diferença"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">Oito dos nove meses fecham. Agosto fica R$ 15.630,20 abaixo, e a diferença está identificada: R$ 17.155,91 da NFS-e 129, cujo título carrega a data da venda no cartão (10/07), menos R$ 1.525,67 de receita sem número de nota. Conferência nota a nota: <strong>as 74 notas de agosto e as 68 de setembro estão todas lançadas</strong>, nenhuma cancelada, com uma única divergência de três centavos.</p>',
 cap="Capítulo 05"))
# 7 setembro x agosto
ca,cs=S["consol_8"],S["consol_9"]
rows=[{"c":[k,f(ca[c]),f(cs[c]),f(cs[c]-ca[c])]} for k,c in
  [("Receita bruta","rb"),("Deduções","ded"),("Custos dos serviços","cus"),("Pessoal direto","pdir"),
   ("Despesas comerciais","com"),("Despesas administrativas","adm"),("Pessoal indireto","pind")]]
rows.append({"cls":"hi","c":["EBITDA",f(ca["eb"]),f(cs["eb"]),f(cs["eb"]-ca["eb"])]})
rows.append({"c":["Investimentos",f(ca["inv"]),f(cs["inv"]),f(cs["inv"]-ca["inv"])]})
rows.append({"cls":"tot","c":["Resultado",f(ca["res"]),f(cs["res"]),f(cs["res"]-ca["res"])]})
H.append(sec(7,"Setembro contra agosto",
 '<span class="chapter-num" style="margin-bottom:10px;">— 06 —</span>'
 '<h2 class="editorial" style="font-size:30px;">De agosto <span class="light">para</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado, com agosto já revisado pelas correções deste ciclo.</p>'+
 tab(["32%","","",""],["Linha","Agosto","Setembro","Variação"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">A receita cai 19,6%% com a baixa temporada, mas o custo não acompanha: pessoal direto <strong>sobe</strong> R$ %s e o investimento quase dobra. É o que explica o EBITDA cair de %s para %s da receita.</p>'%(
   f(abs(cs["pdir"]-ca["pdir"])),pc(ca["eb"],ca["rb"]),pc(cs["eb"],cs["rb"])),
 cap="Capítulo 06"))
# 8 orcado x realizado
rows=[{"c":[x["l"],f(x["o"]),f(x["r"]),f(x["d"])]} for x in orc["linhas"][:9]]
rows.append({"cls":"hi","c":["EBITDA do mês",f(orc["os"]),f(orc["rs"]),f(orc["rs"]-orc["os"])]})
rows.append({"cls":"tot","c":["EBITDA acumulado jan–set",f(orc["oa"]),f(orc["ra"]),f(orc["ra"]-orc["oa"])]})
H.append(sec(8,"Orçado × realizado",
 '<span class="chapter-num" style="margin-bottom:10px;">— 07 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O orçamento, <span class="orange">linha a linha.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Revisão 15.09 do orçamento 2026/27, cenário conservador, contra o realizado consolidado de setembro.</p>'+
 tab(["36%","","",""],["Linha","Orçado","Realizado","Variação"],rows)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">A receita respondeu por R$ 68 mil dos R$ 88,8 mil de desvio do mês. No ano, o EBITDA acumulado está R$ %s abaixo do orçado — e ainda sem a energia de setembro, que vai piorar a linha de custo.</p>'%f(abs(orc["ra"]-orc["oa"])),
 cap="Capítulo 07"))
# 9 caixa
cc=[]
for e,lab in (("amana","Amana"),("topazio","Topázio")):
    for x in cx["ents"][e]["contas"]:
        if abs(x["ini"])>0.004 or abs(x["hoje"])>0.004: cc.append({"c":["%s · %s"%(lab,x["n"]),f(x["ini"]),f(x["mov"]),f(x["hoje"])]})
tot_i=sum(x["ini"] for e in ("amana","topazio") for x in cx["ents"][e]["contas"])
tot_h=sum(x["hoje"] for e in ("amana","topazio") for x in cx["ents"][e]["contas"])
cc.append({"cls":"tot","c":["Total",f(tot_i),f(tot_h-tot_i),f(tot_h)]})
H.append(sec(9,"Caixa · posição por conta",
 '<span class="chapter-num" style="margin-bottom:10px;">— 08 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O caixa, <span class="light">conta a conta,</span> <span class="orange">contra o banco.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Âncora em 30/09, conferida com os extratos, mais o movimento já conciliado até %s.</p>'%cx["hoje"]+
 tab(["38%","","",""],["Conta","Em 30/09","Movimento","Hoje"],cc)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">A conta corrente do Santander aparece negativa porque o banco varre o saldo para a ContaMax automaticamente — leia as duas juntas. A GetNet fica negativa enquanto a taxa já conciliou e o crédito das parcelas ainda é previsto. Dos lançamentos do período, apenas <strong>três</strong> continuam sem conciliar, somando R$ 516,84.</p>',
 cap="Capítulo 08"))
# 10 pendencias
pen=[{"c":["Fatura de energia de setembro","Não está lançada e, pelo extrato, não foi paga. As duas pagas em setembro são de julho e agosto.","CSC / Topázio"]},
     {"c":["De-para dos manifestos da Alem-Mar","R$ 9.431,70 em um balde único. Em agosto o mesmo serviço era separado por tipo de insumo.","CSC"]},
     {"c":["Relação de faturamento de julho","Fecha os R$ 15.630,20 que faltam em agosto, ligados à NFS-e 129.","Contabilidade"]},
     {"c":["Data de emissão = data da NFS-e","Inclusive nas parcelas. Com essa regra, DRE e faturamento passam a bater sozinhos.","CSC · rotina"]},
     {"c":["De-para fixo de prestadores","A mesma pessoa cai em categorias diferentes conforme quem lança.","CSC · rotina"]}]
H.append(sec(10,"O que falta para fechar",
 '<span class="chapter-num" style="margin-bottom:10px;">— 09 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O que falta <span class="light">para</span> <span class="orange">fechar o mês.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Duas pendências mexem no resultado de setembro. As outras três são rotina, e evitam que isso se repita.</p>'+
 tab(["26%","54%","20%"],["Item","Por quê","Com quem"],pen,num=set())+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1000px;">Com a fatura de energia na mão, o relatório final sai no mesmo dia. Pela média dos dois últimos meses, a conta deve ficar entre R$ 6,9 mil e R$ 8,5 mil — e reduz o EBITDA de setembro nesse valor.</p>',
 cap="Capítulo 09"))
# 11 fechamento
H.append('<section class="slide dark" data-slide="11"><div class="closing-grid">'
 '<div class="cover-top"><img class="logo" src="%s" alt="Exact BR" style="height:26px;"><span style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--orange);">Próximo Passo</span></div>'
 '<div class="closing-main"><div class="closing-eye">Para os sócios</div>'
 '<h2 class="closing-title">Setembro já fecha <span class="ital">com a contabilidade.</span><br>Falta <span class="ital">uma conta de luz.</span></h2>'
 '<p class="closing-text">Pela primeira vez a receita do painel e o faturamento da contabilidade batem ao centavo — R$ 595.018,22. <strong>O que separa este pré-relatório do fechamento definitivo são dois documentos que estão com o CSC, não uma dúvida de número.</strong></p></div>'
 '<div class="closing-bottom"><div class="signature"><span class="sig-name">João Victor Andrade de Souza</span><span class="sig-role">Sócio-fundador · Exact BR</span></div>'
 '<div class="contact-block"><span class="c-lbl">Disciplina Gera Lucro</span><span class="c-val">Exact BR · Recife — PE</span></div></div></div></section>'%logo_escuro)
html=cabeca+'<body><div class="deck" id="deck">'+"".join(H)+rodape
html=html.replace("Relatório Gerencial · Agosto/2026 · Grupo Amana / Pousada Topázio · Exact BR",
                  "Pré-relatório Gerencial · Setembro/2026 · Grupo Amana / Pousada Topázio · Exact BR")
html=re.sub(r"(const TOTAL\s*=\s*)\d+",r"\g<1>%d"%TOT,html)
open(SAIDA,"w",encoding="utf-8").write(html)
print("gravado %s  (%d KB, %d secoes)"%(SAIDA.split("/")[-1],len(html)//1024,len(H)))
