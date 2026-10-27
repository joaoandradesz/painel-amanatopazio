# -*- coding: utf-8 -*-
"""Retificacao do relatorio gerencial de agosto/2026 (rev. 3).
   Documento curto que acompanha o relatorio entregue em 07/10: o que mudou,
   quanto, por que, e qual era o numero anterior."""
import re,os,json,collections as _c
BASE=os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/")
MODELO=BASE+"Relatorio_Gerencial_Amana_Topazio_ago2026_v2.html"
SAIDA=BASE+"Retificacao_Relatorio_Agosto2026_rev3.html"
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
sg=lambda v: ("+" if v>0 else "")+f(v)
mod=open(MODELO,encoding="utf-8").read()
_ord=[k for k,_ in _c.Counter(re.findall(r'<img class="logo" src="(data:image/[^"]+)"',mod)).most_common()]
L_CLARO,L_ESC=_ord[0],_ord[-1]
cabeca=mod[:mod.index("</head>")+7]; rodape=mod[mod.rindex("</section>")+10:]
TOT=4
def sec(n,titulo,corpo,cap=None,dark=False):
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'%(L_ESC if dark else L_CLARO,cap or "Retificação",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>Retificação · Agosto/2026 · rev. 3 · substitui a rev. 2 de 07/10/2026</span>'
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
H=[]
H.append(sec(1,"Retificação de agosto",
 '<span class="eyebrow">Retificação · rev. 3 · substitui a rev. 2 de 07/10/2026</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1100px;">Agosto de 2026,<br><span style="color:var(--orange);">retificado.</span></h2>'
 '<p class="lede" style="max-width:900px;font-size:19px;margin-top:18px;">Grupo Amana + Pousada Topázio. O relatório de agosto entregue em 07/10 foi retificado em um único ponto, e o resultado do mês subiu R$ 29.508,23.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:16px;max-width:950px;"><strong>Por que esta retificação existe:</strong> na conferência da receita de setembro contra o relatório de faturamento da contabilidade apareceram 11 parcelas de notas emitidas em <strong>agosto</strong> que estavam lançadas com a data do vencimento em vez da data da nota. Corrigir a competência dessas parcelas aumentou a receita de agosto. Este documento diz exatamente o que mudou, quanto, e qual era o número anterior.</p>',
 dark=True))
rows=[{"cls":"sub","c":["Receita bruta",f(731092.36),f(760600.59),sg(29508.23)]},
 {"c":["&nbsp;&nbsp;Amana",f(725151.37),f(754659.60),sg(29508.23)]},
 {"c":["&nbsp;&nbsp;Topázio",f(5940.99),f(5940.99),"—"]},
 {"cls":"sub","c":["EBITDA",f(136044.96),f(165553.19),sg(29508.23)]},
 {"c":["&nbsp;&nbsp;margem sobre a receita bruta","18,61%","21,77%","+3,16 p.p."]},
 {"cls":"tot","c":["Resultado do mês",f(108868.76),f(138376.99),sg(29508.23)]},
 {"c":["&nbsp;&nbsp;margem sobre a receita bruta","14,89%","18,19%","+3,30 p.p."]}]
H.append(sec(2,"O que mudou",
 '<span class="chapter-num" style="margin-bottom:8px;">— 01 —</span>'
 '<h2 class="editorial" style="font-size:30px;">Um ponto só, <span class="light">e ele move</span> <span class="orange">os três indicadores igual.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">Consolidado Amana + Topázio, agosto/2026, por competência.</p>'
 +tab(["36%","21%","21%","22%"],["Linha","Relatório rev. 2 · 07/10","Retificado · rev. 3","Diferença"],rows,num={1,2,3})
 +'<div class="rule" style="margin:24px 0 16px 0;"></div>'
 '<p class="body-text" style="font-size:14.5px;max-width:1020px;">Os três indicadores andam exatamente o mesmo valor porque o que entrou é <strong>receita de hospedagem já faturada, sem nenhum custo associado</strong> — entra no topo e chega inteira embaixo. A Topázio não teve nenhuma alteração.</p>'
 '<p class="body-text" style="font-size:14.5px;max-width:1020px;margin-top:12px;"><strong>Nenhum vencimento, nenhum valor e nenhuma categoria foram alterados — só a data de competência.</strong> O caixa de agosto e de todos os meses seguintes permanece exatamente como estava no relatório anterior.</p>'
 '<p class="body-text" style="font-size:14.5px;max-width:1020px;margin-top:12px;">A Receita de Hospedagem da Amana foi de <strong>R$ 705.366,37</strong> para <strong>R$ 734.874,60</strong>.</p>',
 cap="Capítulo 01"))
P=[("90","Bruno da Silva Almeida","10.245,66",[("002/004","2.561,43","30/09","31/08"),("003/004","2.561,40","31/10","31/08"),("004/004","2.561,40","30/11","31/08")]),
   ("96","Ana Carollyne Miranda Mesquita","8.831,39",[("002/002","4.415,69","18/09","18/08")]),
   ("99","Rodrigo Improta da Silva","4.493,85",[("002/002","2.246,92","19/09","19/08")]),
   ("109","Anna Paula Albuquerque Santos","4.806,85",[("002/004","1.201,71","05/09","05/08"),("003/004","1.201,71","05/10","05/08"),("004/004","1.201,71","05/11","05/08")]),
   ("111","Sthefany Ventura Muller","5.071,98",[("002/003","1.690,66","20/09","20/08"),("003/003","1.690,66","20/10","20/08")]),
   ("126","Anderson Silva Alves","16.349,89",[("002/002","8.174,94","19/09","19/08")])]
rows=[]
for nf,cl,tot,ps in P:
    for k,(parc,v,a,d) in enumerate(ps):
        rows.append({"c":[nf if k==0 else "",cl if k==0 else "",tot if k==0 else "",parc,v,a+"/2026",d+"/2026"]})
rows.append({"cls":"tot","c":["6 notas","","","11 parcelas","29.508,23","",""]})
H.append(sec(3,"O detalhe",
 '<span class="chapter-num" style="margin-bottom:8px;">— 02 —</span>'
 '<h2 class="editorial" style="font-size:28px;">As 11 parcelas, <span class="light">de</span> <span class="orange">6 notas de agosto.</span></h2>'
 '<p class="lede" style="margin-top:6px;font-size:13px;">Em todas as 6 notas a primeira parcela já estava em agosto, correta. Só as parcelas seguintes vinham com a data do vencimento.</p>'
 +tab(["8%","26%","13%","11%","12%","15%","15%"],["NFS-e","Cliente","Total da NF","Parcela","Valor","Competência antes","Competência agora"],rows,num={2,4})
 +'<p class="body-text" style="font-size:13.5px;margin-top:14px;max-width:1020px;">Das 11 parcelas, <strong>6 estavam em setembro</strong> (R$ 20.291,35), 3 em outubro (R$ 5.453,77) e 2 em novembro (R$ 3.763,11). Por isso agosto recebeu os R$ 29.508,23 inteiros, enquanto setembro devolveu R$ 20.291,35.</p>'
 '<p class="body-text" style="font-size:13.5px;margin-top:10px;max-width:1020px;"><strong>Regra daqui em diante:</strong> em venda parcelada, a data de emissão do título é a data da NFS-e em todas as parcelas, nunca a data do vencimento.</p>',
 cap="Capítulo 02"))
H.append(sec(4,"O efeito na leitura",
 '<span class="eyebrow" style="color:var(--orange);">O que isso muda na análise</span>'
 '<h2 class="editorial" style="font-size:30px;max-width:1050px;margin-top:14px;">Agosto melhora, <span class="light">e a queda para setembro</span><br><span style="color:var(--orange);">fica maior, não menor.</span></h2>'
 '<div class="kgrid" style="margin-top:26px;">%s%s%s</div>'%(
   kc("Resultado de agosto","%s &rarr; %s"%(f(108868.76),f(138376.99)),"retificado, +R$ 29.508,23"),
   kc("Resultado de setembro",f(54916.80),"pré-fechamento, sem a energia"),
   kc("Queda agosto &rarr; setembro","%s &rarr; %s"%(f(35717.07),f(83460.19)),"a queda mais que dobrou",hl=True))+
 '<div class="rule" style="margin:26px 0 18px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;">Quem leu o relatório anterior viu uma queda de R$ 35,7 mil de agosto para setembro. Com agosto retificado e setembro fechado, a queda real é de <strong>R$ 83,5 mil</strong>. A retificação não suaviza o mês: ela mostra que a queda era maior do que parecia.</p>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;margin-top:16px;"><strong>A contrapartida é que os números agora conferem por fora.</strong> Setembro passou a bater ao centavo com o relatório de faturamento da contabilidade — R$ 595.018,22 — e sete dos nove meses de 2026 também batem ao centavo. Agosto fica R$ 15.630,20 abaixo do faturamento apurado (R$ 750.504,80), e a diferença está identificada: R$ 17.155,91 da NFS-e 129, cujo título está com a data da venda no cartão, em julho, menos R$ 1.525,67 de hospedagem faturada sem NFS-e.</p>'
 '<p class="body-text" style="font-size:15px;max-width:1000px;margin-top:16px;">Corrigir a data dessa última nota fecha julho e agosto de uma vez. É o único item aberto, e depende da decisão de reabrir julho.</p>'
 '<div class="rule" style="margin:28px 0 18px 0;"></div>'
 '<p class="lede" style="font-size:15px;max-width:900px;">Exact BR · controladoria Grupo Amana + Pousada Topázio</p>',
 dark=True))
open(SAIDA,"w",encoding="utf-8").write(cabeca+"<body>\n"+"".join(H)+rodape)
print("gravado:",SAIDA)
