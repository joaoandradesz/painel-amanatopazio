# -*- coding: utf-8 -*-
"""Nota tecnica: o que mudou no resultado de setembro/2026, mudanca por mudanca,
com a origem de cada uma. Reaproveita head, CSS e logos do relatorio de agosto."""
import re,os,collections as _c
BASE=os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/")
MODELO=BASE+"Relatorio_Gerencial_Amana_Topazio_ago2026_v2.html"
SAIDA=BASE+"Nota_Tecnica_Setembro2026_O_que_mudou.html"
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
sg=lambda v: ("+" if v>0 else "")+f(v)
mod=open(MODELO,encoding="utf-8").read()
_u=re.findall(r'<img class="logo" src="(data:image/[^"]+)"',mod)
_ord=[k for k,_ in _c.Counter(_u).most_common()]
L_CLARO,L_ESC=_ord[0],_ord[-1]
cabeca=mod[:mod.index("</head>")+7]
rodape=mod[mod.rindex("</section>")+10:]
TOT=7
def sec(n,titulo,corpo,cap=None,dark=False):
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'%(L_ESC if dark else L_CLARO,cap or "Nota técnica",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>Nota técnica · Setembro/2026 · Amana + Topázio</span>'
        '<span class="page-num"><span class="cur">%02d</span> / %d</span></div>'%(' style="color: rgba(255,255,255,0.4);"' if dark else "",n,TOT))
    return '<section class="slide%s" data-slide="%d">%s<div class="s-body">%s</div>%s</section>\n'%(" dark" if dark else "",n,hd,corpo,ft)
def kc(l,v,dd,hl=False): return '<div class="kc"><div class="kl">%s</div><div class="kv%s">%s</div><div class="kd">%s</div></div>'%(l,' hl' if hl else '',v,dd)
def tab(cols,head,rows,cls="dtab xs",num=None):
    N=(lambda i: i>0) if num is None else (lambda i: i in num)
    h="".join('<th%s>%s</th>'%(' class="n"' if N(i) else '',c) for i,c in enumerate(head))
    b=""
    for r in rows:
        tds="".join('<td%s>%s</td>'%(' class="n%s"'%(" neg" if (isinstance(v,str) and v.startswith("-")) else "") if N(i) else '',v) for i,v in enumerate(r["c"]))
        b+='<tr class="%s">%s</tr>'%(r.get("cls",""),tds)
    cg="".join('<col%s>'%(' style="width:%s"'%c if c else '') for c in cols)
    return '<table class="%s"><colgroup>%s</colgroup><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'%(cls,cg,h,b)
# ---------------- a trilha (consolidado Amana+Topazio)
T=[("DRE de setembro como publicada em 20/10",553717.94,107637.13,73151.69,"","base"),
   ("Três apontamentos da conferência extrato × Omie",557037.94,111085.03,76567.08,"Lançamentos que existiam no banco e não no Omie: quatro PIX da InfinitePay, o rendimento do CDB e o IR, e um título duplicado da GetNet.","CSC"),
   ("Moto da Amana reconhecida inteira em setembro",557037.94,111085.03,53233.74,"As três parcelas estavam com emissão em set, out e nov. Passaram para 04/09, a data da compra do ativo. Investimento fica abaixo do EBITDA.","CSC"),
   ("Comissão do Booking de setembro volta para setembro",557037.94,56162.06,-1689.23,"Parcela 009/012, R$ 54.922,97, estava com emissão em 05/10 e caía em outubro. Todas as outras parcelas da série saíram no fim do mês de competência.","CSC"),
   ("Título de R$ 633,00 excluído pelo CSC no Omie",557037.94,56162.06,-1056.23,"Investimento Bangalô, Marcus Vinicius, vencimento 11/10. O CSC excluiu o título no Omie entre duas puxadas do mesmo dia. Não foi mudança nossa.","CSC"),
   ("Pente-fino do Tiago",631640.57,132801.10,75208.15,"Receita presa em conta de controle, nota duplicada, salário indevido e a categoria coringa “Material de consumo”. Detalhado na página seguinte.","CSC"),
   ("11 parcelas de notas de agosto voltam para agosto",611349.22,112509.75,54916.80,"O CSC emitia cada parcela com a data do vencimento em vez da data da NFS-e. R$ 29.508,23 em 6 notas, dos quais R$ 20.291,35 estavam em setembro.","CSC")]
H=[]
# 1 capa
H.append(sec(1,"O que mudou em setembro",
 '<span class="eyebrow">Nota técnica · rastreabilidade do fechamento</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1100px;">O que mexeu no resultado<br>de setembro — <span style="color:var(--orange);">e o que não mexeu.</span></h2>'
 '<p class="lede" style="max-width:900px;font-size:19px;margin-top:18px;">Grupo Amana + Pousada Topázio. Sete alterações entre a DRE publicada em 20/10 e a versão atual, cada uma com o efeito medido em receita, EBITDA e resultado, e com a origem identificada.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:16px;max-width:950px;"><strong>A conclusão, antes do detalhe:</strong> nenhuma das sete alterações foi mudança de critério contábil ou gerencial. Todas as sete são lançamento que faltava, lançamento errado ou data de competência errada no Omie. O critério do painel não mudou em nenhum ponto — e a prova externa é que setembro passou a bater <strong>ao centavo</strong> com o relatório de faturamento da contabilidade.</p>',
 dark=True))
# 2 resumo
H.append(sec(2,"Antes e depois",
 '<span class="chapter-num" style="margin-bottom:10px;">— 01 —</span>'
 '<h2 class="editorial" style="font-size:30px;">O saldo <span class="light">das sete</span> <span class="orange">alterações.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, setembro/2026, por competência.</p>'
 '<div class="kgrid">%s%s%s</div>'%(
   kc("Receita bruta","%s &rarr; %s"%(f(553717.94),f(611349.22)),"+ R$ 57.631,28 · receita que faltava"),
   kc("EBITDA","%s &rarr; %s"%(f(107637.13),f(112509.75)),"+ R$ 4.872,62 · praticamente neutro",hl=True),
   kc("Resultado do mês","%s &rarr; %s"%(f(73151.69),f(54916.80)),"− R$ 18.234,89 · o resultado CAIU"))+
 '<div class="rule" style="margin:26px 0 18px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;">Os três indicadores andaram em direções diferentes, e é isso que explica a confusão. A <strong>receita</strong> subiu R$ 57,6 mil porque havia receita de setembro fora da DRE. O <strong>EBITDA</strong> ficou praticamente no mesmo lugar, porque esse ganho de receita foi quase todo consumido por uma comissão de canal que estava no mês errado. E o <strong>resultado</strong> caiu R$ 18,2 mil, porque abaixo do EBITDA entraram a moto inteira e o restante.</p>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;margin-top:14px;">Quem olha só a Amana isolada vê o resultado subir de R$ 262.653,81 para R$ 297.652,14. Quem olha o consolidado do grupo vê cair de R$ 73.151,69 para R$ 54.916,80. <strong>As duas leituras estão certas</strong> — e a do grupo é a que vale para a decisão.</p>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;margin-top:14px;"><strong>E a queda de agosto para setembro ficou maior, não menor.</strong> Era R$ 35.717,07; passou a R$ 83.460,19 — porque agosto subiu com as parcelas que voltaram para o mês da nota e setembro absorveu a comissão do Booking. A tendência que o Tiago apontou está confirmada pelos ajustes, não desmentida.</p>',
 cap="Capítulo 01"))
# 3 a trilha
rows=[]
for i,(d,rb,eb,re_,_,og) in enumerate(T):
    if i==0: rows.append({"cls":"sub","c":[d,f(rb),f(eb),f(re_),"—","—"]})
    else:
        p=T[i-1]
        rows.append({"c":[d,sg(rb-p[1]) if abs(rb-p[1])>.005 else "—",
                            sg(eb-p[2]) if abs(eb-p[2])>.005 else "—",
                            sg(re_-p[3]) if abs(re_-p[3])>.005 else "—",
                            "competência" if i in (2,3,6) else ("lançamento" if i in (1,4) else "misto"),og]})
rows.append({"cls":"sub","c":["Setembro/2026 — versão atual",f(611349.22),f(112509.75),f(54916.80),"","" ]})
rows.append({"cls":"tot","c":["Efeito total das sete alterações",sg(57631.28),sg(4872.62),sg(-18234.89),"",""]})
H.append(sec(3,"A trilha completa",
 '<span class="chapter-num" style="margin-bottom:8px;">— 02 —</span>'
 '<h2 class="editorial" style="font-size:28px;">Mudança <span class="light">por mudança,</span> <span class="orange">na ordem em que aconteceram.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">Consolidado. Cada linha é um commit datado no repositório do painel, com as travas de consistência registradas.</p>'
 +tab(["38%","13%","13%","13%","11%","12%"],["Alteração","Receita","EBITDA","Resultado","Natureza","Origem"],rows,num={1,2,3})
 +'<p class="body-text" style="font-size:13px;margin-top:16px;max-width:1020px;">As três colunas de valores fecham exatamente: as variações somadas dão a diferença entre a primeira e a última linha, sem resíduo, nos três indicadores. <strong>Não há nenhuma alteração fora desta lista.</strong></p>',
 cap="Capítulo 02"))
# 4 pente-fino aberto
pf=[{"c":["12 NFS-e lançadas só como Adiantamento de Hospedagem","+84.424,60","+84.424,60","+84.424,60"]},
    {"c":["NFS-e 225 (Bruna Bianco) com o adiantamento na conta de receita","-9.849,97","-9.849,97","-9.849,97"]},
    {"c":["Salário indevido na Topázio (título 3130101856, baixado com 100% de desconto)","—","+1.662,32","+1.662,32"]},
    {"c":["Frigobar e taxa de cartão da Topázio","+28,00","+27,43","+27,43"]},
    {"c":["“Material de consumo” redistribuído em 7 categorias (balança vai para Ativos)","—","+374,66","—"]},
    {"cls":"tot","c":["Efeito do pente-fino","+74.602,63","+76.639,04","+76.264,38"]}]
H.append(sec(4,"O pente-fino aberto",
 '<span class="chapter-num" style="margin-bottom:8px;">— 03 —</span>'
 '<h2 class="editorial" style="font-size:28px;">A maior alteração <span class="light">foi receita que</span> <span class="orange">já era de setembro.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">Abertura da linha “Pente-fino do Tiago” da página anterior.</p>'
 +tab(["52%","16%","16%","16%"],["Item","Receita","EBITDA","Resultado"],pf,num={1,2,3})
 +'<div class="rule" style="margin:22px 0 14px 0;"></div>'
 '<p class="body-text" style="font-size:14px;max-width:1020px;"><strong>O mecanismo, que é o ponto central da defesa.</strong> A venda no cartão gera um título em “Adiantamento de Hospedagem”, que é conta de controle e fica <strong>fora da DRE</strong> — correto, porque ainda não há serviço prestado. Quando a NFS-e é emitida, o adiantamento deve ser baixado contra a receita. Em 12 notas de setembro essa baixa não foi feita: ficou só a perna de controle, e R$ 84.424,60 de receita faturada não entraram na DRE.</p>'
 '<p class="body-text" style="font-size:14px;max-width:1020px;margin-top:12px;">Não é lucro novo. É lucro que <strong>já era de setembro</strong>. A DRE publicada em 20/10 estava <strong>subestimando</strong> a receita e o resultado da Amana. O ajuste não inflou setembro: corrigiu uma omissão.</p>'
 '<p class="body-text" style="font-size:14px;max-width:1020px;margin-top:12px;">Na mesma varredura apareceu o oposto: a NFS-e 225 tinha o título de adiantamento <em>dentro</em> da categoria de receita, duplicando R$ 9.849,97 de faturamento. Voltou para a conta de controle. E o salário de R$ 1.662,32 na Topázio era de competência 06/2026, lançado na empresa errada — a própria observação do título diz “SÓCIO DA AMANA — RECEBE PELA AMANA COMO PRÓ-LABORE” — e foi baixado com 100% de desconto, ou seja, nunca saiu caixa nenhum.</p>',
 cap="Capítulo 03"))
# 5 o que nao mudou
nm=[{"c":["“Aluguel de veículos” da Topázio para 21. Custos / 01. Arrendamento","Arrendamento de autorização de veículo, não pessoal","Nenhum"]},
    {"c":["“Agencia de MKT” da Amana renomeada para “Marketing”","Nome que a Topázio já usava no mesmo nó; no consolidado viram uma linha","Nenhum"]},
    {"c":["“Taxa de Permanência” da Amana renomeada para “ISS | Permanência”","Mesmas observações da categoria da Topázio, mesmo nó da árvore","Nenhum"]},
    {"c":["Título de ISS de R$ 300,00 sai de dedução de receita e vai para custo","É ISS de prorrogação de estada, não dedução do faturamento","Nenhum"]}]
H.append(sec(5,"O que não mudou",
 '<span class="chapter-num" style="margin-bottom:8px;">— 04 —</span>'
 '<h2 class="editorial" style="font-size:28px;">Nenhum critério <span class="light">foi alterado</span> <span class="orange">para mexer no EBITDA.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">As quatro arrumações de árvore e nomenclatura do período, todas com trava de “nenhum total pode mudar”.</p>'
 +tab(["38%","42%","20%"],["Arrumação","Por quê","Efeito no EBITDA e no resultado"],nm,num={})
 +'<div class="rule" style="margin:22px 0 14px 0;"></div>'
 '<p class="body-text" style="font-size:14px;max-width:1020px;"><strong>Essas quatro não movem número nenhum.</strong> O script que as executa (<code>dre/arruma_arvore.py</code>) roda com uma asserção explícita: nenhum total de nenhum mês pode mudar. Nenhum mudou. Elas existem só para que a mesma despesa não apareça com dois nomes diferentes no consolidado.</p>'
 '<p class="body-text" style="font-size:14px;max-width:1020px;margin-top:12px;"><strong>As travas de consistência rodam a cada republicação</strong> e estão registradas em cada commit: 5.803 linhas clicáveis conferidas contra o detalhe dos lançamentos com 0 divergências, a varredura de invariantes sem nenhuma falha, e 102 comparações entre os KPIs do painel e a soma da árvore com 0 divergências. Nenhuma versão foi publicada com trava falhando.</p>',
 cap="Capítulo 04"))
# 6 prova externa
pv=[("Janeiro",529990.86,529990.86),("Fevereiro",270043.26,270043.26),("Março",88285.52,88285.52),
    ("Abril",57473.27,57473.27),("Maio",272765.44,272765.44),("Junho",297456.07,297456.07),
    ("Julho",551271.84,568427.75),("Agosto",750504.80,734874.60),("Setembro",595018.22,595018.22)]
rows=[]
for m,c,p in pv:
    d=round(p-c,2)
    rows.append({"cls":"" if abs(d)<.05 else "alert","c":[m,f(c),f(p),("—" if abs(d)<.05 else sg(d)),
      "bate ao centavo" if abs(d)<.05 else ("NFS-e 129 com o título em 10/07, data da venda no cartão" if m=="Julho" else "(–) a NFS-e 129 que ficou em julho   (+) R$ 1.525,67 sem nota")]})
rows.append({"cls":"tot","c":["Total jan a set",f(3412809.28),f(3414334.99),sg(1525.71),"hospedagem faturada sem NFS-e, mais 4 centavos de arredondamento"]})
H.append(sec(6,"A prova externa",
 '<span class="chapter-num" style="margin-bottom:8px;">— 05 —</span>'
 '<h2 class="editorial" style="font-size:28px;">Sete dos nove meses <span class="light">batem</span> <span class="orange">ao centavo.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">Receita de Hospedagem da Amana no painel × Relatório de Faturamento da contabilidade, emitido em 14/10/2026.</p>'
 +tab(["12%","15%","15%","12%","46%"],["Mês","Contabilidade","Painel","Diferença","Explicação"],rows,num={1,2,3})
 +'<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1020px;">O cruzamento foi feito <strong>nota a nota</strong>, não por total. Em agosto, as 74 NFS-e da relação da contabilidade estão todas lançadas no Omie, somando R$ 750.504,84; 73 com a receita dentro de agosto. Em setembro, as 68 NFS-e estão todas lançadas e todas dentro de setembro: <strong>zero pendência</strong>. Nenhuma nota faltando, nenhuma nota a mais, nenhuma cancelada contada como receita.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1020px;">A divergência de nove meses inteiros é <strong>R$ 1.525,71</strong>, e é hospedagem faturada sem NFS-e em agosto. Corrigir a data da NFS-e 129 fecha julho e agosto de uma vez: julho vai para R$ 551.271,84, exato, e agosto para R$ 752.030,51.</p>',
 cap="Capítulo 05"))
# 7 fechamento
H.append(sec(7,"A posição",
 '<span class="eyebrow" style="color:var(--orange);">Conclusão</span>'
 '<h2 class="editorial" style="font-size:34px;max-width:1050px;margin-top:14px;">A instabilidade não foi no dado.<br><span style="color:var(--orange);">Foi na entrada do dado.</span></h2>'
 '<div class="rule" style="margin:26px 0 20px 0;"></div>'
 '<p class="body-text" style="font-size:16px;max-width:980px;">Sete alterações, todas rastreadas, todas com a mesma origem: informação que não estava no Omie, estava duplicada, ou estava com a data de competência errada. Nenhuma mudança de critério. Nenhuma reclassificação que mexesse em EBITDA. Nenhuma versão publicada sem as travas de consistência fecharem.</p>'
 '<p class="body-text" style="font-size:16px;max-width:980px;margin-top:16px;">O resultado desse trabalho é verificável por fora: setembro bate <strong>ao centavo</strong> com o faturamento apurado pela contabilidade, e sete dos nove meses de 2026 também.</p>'
 '<p class="body-text" style="font-size:16px;max-width:980px;margin-top:16px;"><strong>Três coisas precisam acontecer para isso não se repetir:</strong></p>'
 '<p class="body-text" style="font-size:15px;max-width:980px;margin-top:10px;">1. &nbsp;Em venda parcelada, a data de emissão do título é a data da NFS-e, em <strong>todas</strong> as parcelas — nunca a data do vencimento.<br>'
 '2. &nbsp;Quando a NFS-e é emitida, o adiantamento é baixado contra a receita no mesmo lançamento.<br>'
 '3. &nbsp;“Material de consumo” sai de uso como categoria coringa.</p>'
 '<p class="body-text" style="font-size:15px;max-width:980px;margin-top:18px;"><strong>E dois itens seguem pendentes do CSC:</strong> a fatura de energia de competência setembro, que não está lançada nem paga, e o de-para dos manifestos da Alem-Mar. Os dois entram no custo e vão reduzir o resultado de setembro — por isso o relatório do mês segue como pré-relatório.</p>'
 '<div class="rule" style="margin:28px 0 18px 0;"></div>'
 '<p class="lede" style="font-size:15px;max-width:900px;">Exact BR · controladoria Grupo Amana + Pousada Topázio</p>',
 dark=True))
open(SAIDA,"w",encoding="utf-8").write(cabeca+"<body>\n"+"".join(H)+rodape)
print("gravado:",SAIDA)
