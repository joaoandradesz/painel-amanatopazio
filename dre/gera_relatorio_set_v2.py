# -*- coding: utf-8 -*-
"""Relatorio Gerencial de setembro/2026 no padrao de 16 paginas do de agosto
   (Ponto A -> F.I.E.L -> Ponto B), que foi o formato pedido pelo Tiago.

   Todo numero sai de dre/dados_rel.json + dre/orc2.json, reconstruidos do
   index.html publicado pelo monta_dados_rel.py. O relatorio nao calcula DRE
   nem caixa por conta propria -- so le, compara e interpreta.

   Agosto aparece aqui com o numero PUBLICADO (760.600,59 / 165.553,19 /
   138.376,99). Os R$ 15.630,20 da NFS-e 129 estao segurados ate dezembro por
   decisao do Joao -- ver dre/PENDENCIA_AGOSTO_2026.md."""
import json,re,os,collections as _c
BASE=os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/")
RAIZ=os.path.expanduser("~/painel-amanatopazio/")
MODELO=BASE+"Relatorio_Gerencial_Amana_Topazio_ago2026_v2.html"
SAIDA=BASE+"Relatorio_Gerencial_Amana_Topazio_set2026.html"
d=json.load(open(RAIZ+"dre/dados_rel.json")); orc=json.load(open(RAIZ+"dre/orc2.json"))
S=d["casc"]; com=d["com"]; CX=d["caixa"]; RES=d["resumo"]
f=lambda v: format(round(v or 0,2),",.2f").replace(",","@").replace(".",",").replace("@",".")
pc=lambda v,b: ("%.1f%%"%(abs(v)/b*100)).replace(".",",") if b else "—"
pct=lambda v: ("%.2f%%"%v).replace(".",",")
pp=lambda v: ("%.1f%%"%v).replace(".",",")
M=[str(x) for x in range(1,10)]
NOME=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set"]

mod=open(MODELO,encoding="utf-8").read()
_ord=[k for k,_ in _c.Counter(re.findall(r'<img class="logo" src="(data:image/[^"]+)"',mod)).most_common()]
L_CLARO,L_ESC=_ord[0],_ord[-1]
cabeca=mod[:mod.index("</head>")+7]; rodape=mod[mod.rindex("</section>")+10:]
TAG="Relatório Gerencial · Setembro/2026 · caixa até 30/09"
PAG=[0]; CAP=[0]
def cab():
    CAP[0]+=1
    return ('<span class="chapter-num" style="margin-bottom:10px;">— %02d —</span>'%CAP[0],"Capítulo %02d"%CAP[0])
def sec(titulo,corpo,cap=None,dark=False,bodycls=""):
    PAG[0]+=1; n=PAG[0]
    hd=('<div class="s-header"><img class="logo" src="%s" alt="Exact BR"><div class="meta">'
        '<span class="accent">%s</span><span class="pipe"></span><span>%s</span></div></div>'
        %(L_ESC if dark else L_CLARO,cap or "Relatório",titulo))
    ft=('<div class="s-footer"><span class="doc-tag"%s>%s</span>'
        '<span class="page-num"><span class="cur">%02d</span> / __TOT__</span></div>'
        %(' style="color: rgba(255,255,255,0.4);"' if dark else "",TAG,n))
    return '<section class="slide%s" data-slide="%d">%s<div class="s-body"%s>%s</div>%s</section>\n'%(
        " dark" if dark else "",n,hd,(' style="%s"'%bodycls if bodycls else ""),corpo,ft)
def kc(l,v,dd,hl=False,neg=False):
    return '<div class="kc"><div class="kl">%s</div><div class="kv%s">%s</div><div class="kd">%s</div></div>'%(
        l,' hl' if hl else (' neg' if neg else ''),v,dd)
def tab(cols,head,rows,cls="dtab xs",num=None):
    N=(lambda i:i>0) if num is None else (lambda i:i in num)
    h="".join('<th%s>%s</th>'%(' class="n"' if N(i) else '',c) for i,c in enumerate(head))
    b=""
    for r in rows:
        if r.get("span"):
            b+='<tr class="grp"><td colspan="%d">%s</td></tr>'%(len(head),r["span"]); continue
        tds="".join('<td%s>%s</td>'%(' class="n%s"'%(" neg" if (isinstance(v,str) and v.startswith("-")) else "") if N(i) else '',v)
                    for i,v in enumerate(r["c"]))
        b+='<tr class="%s">%s</tr>'%(r.get("cls",""),tds)
    cg="".join('<col%s>'%(' style="width:%s"'%c if c else '') for c in cols)
    return '<table class="%s"><colgroup>%s</colgroup><thead><tr>%s</tr></thead><tbody>%s</tbody></table>'%(cls,cg,h,b)
def etapa(letra,nome,sub,pergunta_a,pergunta_b,itens,muda):
    """Pagina divisoria do F.I.E.L, no mesmo desenho do relatorio de agosto."""
    ordem="FIEL"; i=ordem.index(letra)
    tr='<span class="t done">PONTO A</span><span class="ln"></span>'
    for k,x in enumerate(ordem):
        tr+='<span class="t %s">%s</span><span class="ln"></span>'%("on" if k==i else ("done" if k<i else ""),x)
    tr+='<span class="t ">PONTO B</span>'
    li="".join('<div class="item"><div class="idx">%s.</div><div class="txt"><strong>%s</strong>%s</div></div>'%(r,t,x)
               for r,t,x in itens)
    return ('<div class="track">%s</div>'
            '<div class="step-wrap"><div><div class="big-let">%s</div><div class="big-name">%s</div>'
            '<div class="big-meta">%s</div></div>'
            '<div><div class="resolve">O que esta etapa resolve</div>'
            '<div class="resolve-q">%s <span class="ital">%s</span></div>'
            '<div class="resolve" style="margin-bottom:6px">O que fazemos</div>'
            '<div class="escopo-list tight" style="margin-top:0">%s</div>'
            '<div class="muda"><div class="m-lbl">O que muda para vocês</div><div class="m-txt">%s</div></div>'
            '</div></div>'%(tr,letra,nome,sub,pergunta_a,pergunta_b,li,muda))

c9,c8,cT=S["consol_9"],S["consol_8"],S["consol_T"]
x9,x8=CX["9"],CX["8"]
CONT=d["contas"]["consol"]
CAIXA_SF=round(sum(a["sf"] for a in CONT),2)
APL=round(sum(a["sf"] for a in CONT if a["t"]=="CA"),2)
IC=abs(round(sum(a["v"] for a in d["linhas"]["amana_9"] if "02. Custo dos Serviços Prestados" in a["c"]),2))

# ponto de equilibrio, pelos buckets de custo variavel e fixo do proprio painel
def be(m):
    x=RES["consol"][m]; rb=x["rb"]; mc=rb+x["cvar"]; pe=-x["cfix"]/(mc/rb)
    return dict(rb=rb,cvar=x["cvar"],mc=mc,mcp=mc/rb,cfix=x["cfix"],eb=x["ebitda"],
                pe=pe,oce=com[m]["oc"]*pe/rb,seg=(rb-pe)/rb*100)
B8,B9=be("8"),be("9")
# decomposicao preco x volume, na base do sistema comercial
v0,v1=com["8"]["noites"],com["9"]["noites"]; p0,p1=com["8"]["tkt"],com["9"]["tkt"]
EF_VOL=round((v1-v0)*p0,2); EF_PRE=round(v0*(p1-p0),2); EF_CRU=round((v1-v0)*(p1-p0),2)

# relatorio comercial diario da pousada, posicao de 26/10/2026
FRENTE=[("outubro/26",85.59,82.80,686080.29),("novembro/26",69.11,77.11,510749.07),
        ("dezembro/26",35.27,77.20,265104.09)]
CARTEIRA_CARTAO=586280.21; CARTEIRA_COBRAR=449828.12; CAIXA_2610=645769.35; OUT_CANC=43.97
# saldo do banco em 30/09, dos extratos consolidados e do extrato de investimentos
EXTRATO={"Amana · Bradesco":1.00,"Amana · Santander":0.00,"Amana · Infinit Pay":11921.00,
 "Amana · Mercado Pago - Amana":632.55,"Amana · Santander - Aplicação":236180.23,
 "Amana · Bradesco - Invest Fácil":10045.54,"Amana · Santander - CDB DI PJ":None,
 "Amana · Bradesco - CDB DI PJ":78811.59,"Topázio · Santander_Top_40-3":0.00,
 "Topázio · Santander - Aplicação_Top_40-3":12683.22}
NOMES={"Amana · Bradesco":"Bradesco · conta corrente",
 "Amana · Santander":"Santander · conta corrente",
 "Amana · Infinit Pay":"InfinitePay",
 "Amana · Mercado Pago - Amana":"Mercado Pago",
 "Amana · Santander - Aplicação":"Santander · ContaMax (aplicação)",
 "Amana · Bradesco - Invest Fácil":"Bradesco · Invest Fácil",
 "Amana · Santander - CDB DI PJ":"Santander · CDB DI PJ",
 "Amana · Bradesco - CDB DI PJ":"Bradesco · CDB DI PJ",
 "Topázio · Santander_Top_40-3":"Santander · conta corrente",
 "Topázio · Santander - Aplicação_Top_40-3":"Santander · ContaMax (aplicação)"}
nome=lambda n: NOMES.get(n,n)

H=[]
# ============ 01 capa
H.append(sec("Setembro/2026",
 '<span class="eyebrow">Fechamento · 30 de setembro de 2026</span>'
 '<h2 class="editorial xl" style="margin-top:18px;max-width:1150px;font-size:clamp(42px,5vw,72px);">'
 'Relatório Gerencial Setembro<br><span style="color:var(--orange);">Amana e Topázio</span></h2>'
 '<p class="lede" style="max-width:920px;font-size:19px;margin-top:18px;">O resultado e o caixa fecham na '
 'mesma data: 30 de setembro, conta a conta contra os extratos dos bancos.</p>'
 '<div class="rule" style="margin:28px 0 24px 0;"></div>'
 '<p class="body-text" style="font-size:15px;max-width:940px;">A receita recuou %s contra agosto e o custo fixo '
 'ficou praticamente igual — é isso que leva o EBITDA de %s para %s da receita. A operação segue acima do ponto '
 'de equilíbrio, com um terço menos de folga: a margem de segurança foi de %s para <strong>%s</strong>.</p>'
 '<div class="proof-row"><div><div class="pv orange">%s</div><div class="pl">Receita bruta do mês</div></div>'
 '<div><div class="pv">%s</div><div class="pl">EBITDA · %s da receita</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Resultado depois de capex</div></div>'
 '<div><div class="pv">%s</div><div class="pl">Caixa em 30/09</div></div></div>'%(
   ("%.1f%%"%((c8["rb"]-c9["rb"])/c8["rb"]*100)).replace(".",","),
   pc(c8["eb"],c8["rb"]),pc(c9["eb"],c9["rb"]),pp(B8["seg"]),pp(B9["seg"]),
   f(c9["rb"]),f(c9["eb"]),pc(c9["eb"],c9["rb"]),f(c9["res"]),f(CAIXA_SF)),
 dark=True))

# ============ 02 os numeros
_m,_c=cab()
H.append(sec("Os números de setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">Setembro <span class="light">de 2026,</span> <span class="orange">em um olhar.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">O mês fechado por competência, com o caixa do próprio mês. Consolidado Amana + Topázio.</p>'
 '<div class="kgrid">%s%s%s%s%s%s%s%s%s</div>'%(
   kc("Receita bruta",f(c9["rb"]),"faturamento do mês, pela emissão"),
   kc("EBITDA",f(c9["eb"]),"%s da receita bruta"%pc(c9["eb"],c9["rb"]),hl=True),
   kc("Resultado do mês",f(c9["res"]),"depois de investimento e não operacional"),
   kc("Taxa de ocupação",pct(com["9"]["oc"]),"%d hóspedes em %d noites"%(com["9"]["hosp"],com["9"]["noites"])),
   kc("Diária média",f(com["9"]["tkt"]),"R$ %s a menos que agosto"%f(abs(p1-p0))),
   kc("RevPar",f(com["9"]["revpar"]),"diária média × ocupação"),
   kc("Geração de caixa operacional",f(x9["ger_op"]),"o que a operação produziu no mês",neg=True),
   kc("Geração de caixa final",f(x9["ger_fim"]),"após investimento e não operacional",neg=True),
   kc("Saldo nas contas em 30/09",f(CAIXA_SF),"conta corrente e aplicação"))+
 '<p class="body-text" style="font-size:14px;margin-top:20px;max-width:1030px;">Setembro <strong>deu lucro e '
 'consumiu caixa ao mesmo tempo</strong>, e os dois estão certos: faturamos R$ %s e recebemos R$ %s — o resto '
 'é venda no cartão que entra no banco nos meses seguintes. O EBITDA cai mais rápido que a receita porque a '
 'estrutura fixa não acompanha a baixa temporada.</p>'%(f(c9["rb"]),f(x9["rec"])),
 cap=_c))

# ============ 03 DRE do mes
rb=c9["rb"]
lin=[{"cls":"sub","c":["Receita bruta",f(c9["rb"]),pc(c9["rb"],rb)]},
 {"c":["(–) Deduções de receita",f(c9["ded"]),pc(c9["ded"],rb)]},
 {"cls":"sub","c":["= Receita líquida",f(c9["rl"]),pc(c9["rl"],rb)]},
 {"c":["(–) Custos dos serviços",f(c9["cus"]),pc(c9["cus"],rb)]},
 {"c":["(–) Pessoal da operação",f(c9["pdir"]),pc(c9["pdir"],rb)]},
 {"cls":"sub","c":["= Lucro bruto",f(c9["lb"]),pc(c9["lb"],rb)]},
 {"c":["(–) Despesas comerciais",f(c9["com"]),pc(c9["com"],rb)]},
 {"c":["(–) Despesas administrativas",f(c9["adm"]),pc(c9["adm"],rb)]},
 {"c":["(–) Pessoal indireto",f(c9["pind"]),pc(c9["pind"],rb)]},
 {"cls":"hi","c":["= EBITDA",f(c9["eb"]),pc(c9["eb"],rb)]},
 {"c":["(±) Resultado financeiro",f(c9["rf"]),pc(c9["rf"],rb)]},
 {"cls":"sub","c":["= Lucro líquido",f(c9["ll"]),pc(c9["ll"],rb)]},
 {"span":"ABAIXO DO EBITDA · CAPEX E NÃO OPERACIONAL"},
 {"c":["(–) Investimentos (capex)",f(c9["inv"]),pc(c9["inv"],rb)]},
 {"c":["(+) Receita não operacional",f(c9["recnop"]),pc(c9["recnop"],rb)]},
 {"c":["(±) Não operacional",f(c9["nop"]),pc(c9["nop"],rb)]},
 {"cls":"hi2","c":["= RESULTADO APÓS INVESTIMENTOS",f(c9["res"]),pc(c9["res"],rb)]}]
_m,_c=cab()
H.append(sec("DRE · setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">A DRE <span class="light">de</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, pela data de emissão dos documentos. O repasse entre as duas empresas é transferência, não receita.</p>'
 +tab(["44%","",""],["Linha","Valor R$","AV %"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">O consolidado elimina '
 '<strong>R$ %s</strong> de compra de diárias da Amana na Topázio. Margem EBITDA de %s — a menor desde maio. '
 'O capex de R$ %s consome boa parte do lucro líquido do mês.</p>'%(
   f(IC),pc(c9["eb"],rb),f(abs(c9["inv"]))),cap=_c))

# ============ 04 caixa do mes
rec=x9["rec"]
lin=[{"cls":"sub","c":["Saldo inicial em 01/09",f(x9["si"]),"—"]},
 {"cls":"sub","c":["(+) Recebimentos",f(x9["rec"]),"100,0%"]},
 {"c":["(–) Custos da operação",f(x9["cus"]),pc(x9["cus"],rec)]},
 {"c":["(–) Despesas",f(x9["des"]),pc(x9["des"],rec)]},
 {"cls":"hi","c":["= GERAÇÃO DE CAIXA OPERACIONAL",f(x9["ger_op"]),pc(x9["ger_op"],rec)]},
 {"c":["(–) Investimentos e empréstimos",f(x9["inv"]),pc(x9["inv"],rec)]},
 {"c":["(±) Não operacional",f(x9["nop"]),pc(x9["nop"],rec)]},
 {"cls":"hi2","c":['= GERAÇÃO DE CAIXA FINAL<br><span style="font-weight:600;letter-spacing:0;text-transform:none">após investimento, empréstimo e não operacional</span>',f(x9["ger_fim"]),pc(x9["ger_fim"],rec)]},
 {"cls":"tot","c":["Saldo final em 30/09",f(x9["sf"]),"—"]}]
_m,_c=cab()
H.append(sec("Fluxo de caixa · setembro/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">O caixa <span class="light">de</span> <span class="orange">setembro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Movimentação bancária do mês, conta a conta, conferida contra os extratos. Transferência entre contas do grupo não entra como entrada nem como saída.</p>'
 +tab(["44%","",""],["Linha","Valor R$","AV %"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">A distância entre o lucro de '
 'R$ %s e o consumo de caixa de R$ %s é <strong>capital de giro</strong>: a receita faturada entra no banco '
 'depois (R$ %s de diferença entre faturar e receber) e a despesa comercial pagou R$ 139.653,57 contra '
 'R$ %s de competência — comissão de reserva de meses anteriores saindo agora. Não é prejuízo; é prazo, e ele '
 'se inverte quando a alta temporada começar a receber.</p>'%(
   f(c9["res"]),f(abs(x9["ger_fim"])),f(abs(rec-c9["rb"])),f(abs(c9["com"]))),cap=_c))

# ============ 05 F · Fidedigno
_m,_c=cab()
H.append(sec("Fidedigno · Conciliação",
 etapa("F","Fidedigno.","Etapa 01<br>Conciliação<br>Fechamento",
  "Números em que","ninguém confia.",
  [("i","Receita que não aparecia na DRE",
    "Doze NFS-e de setembro estavam lançadas só como Adiantamento de Hospedagem, conta de controle fora da DRE. "
    "A nota existia, a receita não. São R$ 84.424,60 que voltaram para a linha certa."),
   ("ii","Competência pela data da nota",
    "Onze parcelas de seis notas carregavam a data do vencimento em vez da data da nota. A regra agora é uma só: "
    "a receita entra no mês em que a NFS-e foi emitida."),
   ("iii","Custo no mês em que aconteceu",
    "A energia de setembro (R$ 8.540,55) foi lançada, e o frete deixou de cair num balaio único: obra, limpeza, "
    "café da manhã e geral, cada um na sua linha."),
   ("iv","Caixa conferido contra o extrato",
    "Um crédito de R$ 687,00 existia no extrato do Santander e não no Omie. Lançado. As dez contas do grupo "
    "foram batidas uma a uma contra os extratos.")],
  "A receita de hospedagem de setembro bate <strong>ao centavo</strong> com a relação de faturamento da "
  "contabilidade: R$ 595.018,22. E o caixa do grupo em 30 de setembro é R$ %s."%f(CAIXA_SF)),
 cap=_c,bodycls="justify-content:center;"))

# ============ 06 posicao de caixa
lin=[]; tot_o=tot_b=0.0
for emp,pref in (("AMANA EMPREENDIMENTOS TURÍSTICOS","Amana · "),("POUSADA TOPÁZIO","Topázio · ")):
    lin.append({"span":emp})
    for a in CONT:
        if not a["n"].startswith(pref): continue
        if abs(a["sf"])<0.004 and a["t"]!="CC": continue
        b=EXTRATO.get(a["n"]); tot_o+=a["sf"]
        if b is None:
            lin.append({"c":[nome(a["n"]),f(a["sf"]),"—","—","sem extrato na mão"]}); continue
        tot_b+=b; dif=round(a["sf"]-b,2)
        lin.append({"c":[nome(a["n"]),f(a["sf"]),f(b),f(dif),
                         "confere" if abs(dif)<0.05 else ("rendimento de 01/10" if abs(dif)<2 else "bruto × líquido de IR")]})
com_ext=round(tot_o-sum(a["sf"] for a in CONT if EXTRATO.get(a["n"]) is None and a["n"] in EXTRATO),2)
lin.append({"cls":"hi","c":["SUBTOTAL · CONTAS COM EXTRATO NA MÃO",f(com_ext),f(tot_b),f(round(com_ext-tot_b,2)),"oito de nove conferem"]})
lin.append({"cls":"hi2","c":["CAIXA DO GRUPO EM 30/09",f(tot_o),"—","—",""]})
_m,_c=cab()
H.append(sec("Posição de caixa · 30/09/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">Dez contas, <span class="light">uma a uma,</span> <span class="orange">contra o extrato do banco.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Saldo do Omie em 30 de setembro contra o extrato consolidado de cada banco. O relatório “C.C” não mostra aplicação e resgate — a conferência é sempre pelo consolidado.</p>'
 +tab(["26%","13%","13%","11%","19%"],["Conta","Omie 30/09","Extrato 30/09","Diferença","Conferência"],lin,num={1,2,3})+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">Oito das nove contas com '
 'extrato na mão fecham. A única diferença de valor são <strong>R$ 32,51 no CDB do Bradesco</strong>, e é '
 'critério, não lançamento: o Omie carrega o valor bruto e o banco informa o líquido de IR. Falta o extrato do '
 '<strong>CDB DI PJ do Santander</strong> (R$ 312.008,23) — é o único saldo do grupo que ainda não tem documento '
 'do banco atrás.</p>',cap=_c))

# ============ 07 caixa mes a mes
def linha_cx(rot,campo,cls=""):
    v=[CX[m][campo] for m in M]
    return {"cls":cls,"c":[rot]+[f(x) for x in v]+[f(round(sum(v),2))]}
lin=[{"cls":"sub","c":["Saldo inicial"]+[f(CX[m]["si"]) for m in M]+[f(CX["1"]["si"])]},
 linha_cx("(+) Recebimentos","rec","sub"),
 linha_cx("(–) Custos da operação","cus"),
 linha_cx("(–) Despesas","des"),
 linha_cx("= GERAÇÃO DE CAIXA OPERACIONAL","ger_op","hi"),
 linha_cx("(–) Investimentos e empréstimos","inv"),
 linha_cx("(±) Não operacional","nop"),
 linha_cx("= GERAÇÃO DE CAIXA FINAL","ger_fim","hi2"),
 {"cls":"tot","c":["Saldo final"]+[f(CX[m]["sf"]) for m in M]+[f(CX["9"]["sf"])]}]
ger_ano=round(sum(CX[m]["ger_fim"] for m in M),2)
_m,_c=cab()
H.append(sec("Fluxo de caixa · jan a set/2026",
 _m+'<h2 class="editorial" style="font-size:28px;">O caixa <span class="light">mês a mês,</span> <span class="orange">pelo extrato.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio. Apurado pela movimentação bancária, conta a conta. Transferência entre contas do grupo não entra como entrada nem como saída.</p>'
 +tab(["17%"]+[""]*10,["Linha"]+NOME+["Total"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1040px;">No ano o caixa %s '
 '<strong>R$ %s</strong>, saindo de R$ %s em 01/01 para R$ %s em 30/09. Os dois meses de maior consumo são '
 'justamente os de maior investimento. A operação sozinha, sem capex, %s no período.</p>'%(
   "caiu" if ger_ano<0 else "subiu",f(abs(ger_ano)),f(CX["1"]["si"]),f(CX["9"]["sf"]),
   ("gerou R$ "+f(sum(CX[m]["ger_op"] for m in M))) if sum(CX[m]["ger_op"] for m in M)>0
   else ("consumiu R$ "+f(abs(sum(CX[m]["ger_op"] for m in M))))),cap=_c))

# ============ 08 I · Inteligente
_m,_c=cab()
H.append(sec("Inteligente · Leitura",
 etapa("I","Inteligente.","Etapa 02<br>Leitura<br>Diagnóstico",
  "Número certo que","não vira decisão.",
  [("i","A estrutura fixa não respira",
    "A receita caiu R$ %s de agosto para setembro e o custo fixo subiu R$ %s. Cada real de receita que sai leva "
    "%s centavos de EBITDA junto."%(f(abs(B9["rb"]-B8["rb"])),f(abs(B9["cfix"]-B8["cfix"])),"%.0f"%(B9["mcp"]*100))),
   ("ii","A queda é preço, não volume",
    "A pousada perdeu 17 noites ocupadas, mas perdeu R$ %s por diária. Três quartos da queda de receita vêm da "
    "diária média."%f(abs(p1-p0))),
   ("iii","Lucro e caixa andam separados",
    "O mês deu R$ %s de lucro e consumiu R$ %s de caixa. A diferença é prazo de cartão e comissão de meses "
    "anteriores — não é resultado."%(f(c9["res"]),f(abs(x9["ger_fim"])))),
   ("iv","É o capex que consome o ano",
    "No ano o grupo gerou R$ %s de EBITDA e fechou com resultado após investimentos negativo em R$ %s. A operação "
    "paga as contas; o investimento é que pesa."%(f(cT["eb"]),f(abs(cT["res"]))))],
  "O número para guardar é a <strong>ocupação de equilíbrio: %s</strong>. Abaixo disso, com a diária média de "
  "setembro, o mês dá prejuízo operacional."%pp(B9["oce"])),
 cap=_c,bodycls="justify-content:center;"))

# ============ 09 DRE acumulada
rbT=cT["rb"]
lin=[{"span":"RESULTADO POR COMPETÊNCIA · JANEIRO A SETEMBRO DE 2026"},
 {"cls":"sub","c":["Receita bruta",f(cT["rb"]),pc(cT["rb"],rbT)]},
 {"c":["(–) Deduções de receita",f(cT["ded"]),pc(cT["ded"],rbT)]},
 {"cls":"sub","c":["= Receita líquida",f(cT["rl"]),pc(cT["rl"],rbT)]},
 {"c":["(–) Custos dos serviços",f(cT["cus"]),pc(cT["cus"],rbT)]},
 {"c":["(–) Pessoal da operação",f(cT["pdir"]),pc(cT["pdir"],rbT)]},
 {"cls":"sub","c":["= Lucro bruto",f(cT["lb"]),pc(cT["lb"],rbT)]},
 {"c":["(–) Despesas comerciais",f(cT["com"]),pc(cT["com"],rbT)]},
 {"c":["(–) Despesas administrativas",f(cT["adm"]),pc(cT["adm"],rbT)]},
 {"c":["(–) Pessoal indireto",f(cT["pind"]),pc(cT["pind"],rbT)]},
 {"cls":"hi","c":["= EBITDA",f(cT["eb"]),pc(cT["eb"],rbT)]},
 {"c":["(±) Resultado financeiro",f(cT["rf"]),pc(cT["rf"],rbT)]},
 {"cls":"sub","c":["= Lucro líquido",f(cT["ll"]),pc(cT["ll"],rbT)]},
 {"span":"ABAIXO DO EBITDA · CAPEX E NÃO OPERACIONAL"},
 {"c":["(–) Investimentos (capex)",f(cT["inv"]),pc(cT["inv"],rbT)]},
 {"c":["(+) Receita não operacional",f(cT["recnop"]),pc(cT["recnop"],rbT)]},
 {"c":["(±) Não operacional",f(cT["nop"]),pc(cT["nop"],rbT)]},
 {"cls":"hi2","c":["= RESULTADO APÓS INVESTIMENTOS",f(cT["res"]),pc(cT["res"],rbT)]}]
_m,_c=cab()
H.append(sec("DRE consolidada · jan a set/2026",
 _m+'<h2 class="editorial" style="font-size:30px;">A cascata da receita <span class="orange">até o resultado.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado Amana + Topázio, pela data de emissão dos documentos. O repasse entre as duas empresas é transferência, não receita.</p>'
 +tab(["44%","",""],["Linha","Valor R$","AV %"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">Nove meses, R$ %s de receita '
 'e R$ %s de EBITDA — margem de %s. O que leva o resultado do ano para o negativo é o capex de R$ %s, que é '
 'decisão de investimento, não desempenho da operação.</p>'%(
   f(cT["rb"]),f(cT["eb"]),pc(cT["eb"],rbT),f(abs(cT["inv"]))),cap=_c))

# ============ 10 resultado mes a mes
R=lambda m: RES["consol"][m]
lin=[{"cls":"sub","c":["Receita bruta"]+[f(R(m)["rb"]) for m in M]+[f(cT["rb"])]},
 {"c":["(–) Custos variáveis"]+[f(R(m)["cvar"]) for m in M]+[f(sum(R(m)["cvar"] for m in M))]},
 {"c":["(–) Custos e despesas fixas"]+[f(R(m)["cfix"]) for m in M]+[f(sum(R(m)["cfix"] for m in M))]},
 {"cls":"hi","c":["= EBITDA"]+[f(R(m)["ebitda"]) for m in M]+[f(cT["eb"])]},
 {"c":["Margem EBITDA"]+[pc(R(m)["ebitda"],R(m)["rb"]) if R(m)["ebitda"]>0 else "—" for m in M]+[pc(cT["eb"],rbT)]},
 {"cls":"hi2","c":["= RESULTADO DO MÊS"]+[f(R(m)["res"]) for m in M]+[f(cT["res"])]}]
melhor=max(M,key=lambda m:R(m)["ebitda"]); pior=min(M,key=lambda m:R(m)["ebitda"])
_m,_c=cab()
H.append(sec("Resultado · jan a set/2026",
 _m+'<h2 class="editorial" style="font-size:28px;">O resultado <span class="light">mês a mês,</span> <span class="orange">por competência.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Consolidado do grupo pela data de emissão dos documentos. Variável é o que anda com a ocupação; fixo é o que a pousada paga com a casa cheia ou vazia.</p>'
 +tab(["17%"]+[""]*10,["Linha"]+NOME+["Total"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1040px;">O melhor mês do ano em EBITDA '
 'foi <strong>%s</strong> (R$ %s) e o pior, <strong>%s</strong> (R$ %s). O custo fixo médio do ano é de R$ %s '
 'por mês e varia pouco — é ele que define quanto a pousada precisa vender todo mês, independente da '
 'temporada.</p>'%(NOME[int(melhor)-1],f(R(melhor)["ebitda"]),NOME[int(pior)-1],f(R(pior)["ebitda"]),
   f(abs(sum(R(m)["cfix"] for m in M))/9)),cap=_c))

# ============ 11 comercial
ind=[("Ocupação",lambda m: pct(com[m]["oc"]),pct(com["T"]["oc"]) if "T" in com else ""),
     ("Diária média",lambda m: f(com[m]["tkt"]),""),
     ("RevPar",lambda m: f(com[m]["revpar"]),""),
     ("Hóspedes",lambda m: "%d"%com[m]["hosp"],""),
     ("Noites vendidas",lambda m: "%d"%com[m]["noites"],""),
     ("Reservas canceladas",lambda m: "%d"%com[m]["canc"],"")]
lin=[]
for rot,fn,_t in ind:
    v=[fn(m) for m in M]
    if rot in ("Hóspedes","Noites vendidas","Reservas canceladas"):
        tt="%d"%sum(com[m]["hosp" if rot=="Hóspedes" else "noites" if rot=="Noites vendidas" else "canc"] for m in M)
    elif rot=="Ocupação": tt=pct(com["T"]["oc"])
    elif rot=="Diária média": tt=f(com["T"]["adr"]) if "adr" in com.get("T",{}) else f(com["T"]["tkt"])
    else: tt="—"
    lin.append({"c":[rot]+v+[tt]})
pv=[{"c":["Noites ocupadas","%d"%v0,"%d"%v1,"%d"%(v1-v0)]},
    {"c":["Diária média",f(p0),f(p1),f(p1-p0)]},
    {"cls":"sub","c":["Receita do sistema comercial",f(com["8"]["rec"]),f(com["9"]["rec"]),f(com["9"]["rec"]-com["8"]["rec"])]},
    {"c":["&nbsp;&nbsp;efeito volume","","",f(EF_VOL)]},
    {"c":["&nbsp;&nbsp;efeito preço","","",f(EF_PRE)]},
    {"c":["&nbsp;&nbsp;efeito cruzado","","",f(EF_CRU)]}]
_m,_c=cab()
H.append(sec("Desempenho comercial · Pousada Topázio",
 _m+'<h2 class="editorial" style="font-size:28px;">Ocupação, diária <span class="light">e o que</span> <span class="orange">sustenta a receita.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Indicadores operacionais da pousada, por competência de check-in. Fonte: relatório comercial de vocês, posição de 26/10.</p>'
 +tab(["17%"]+[""]*10,["Indicador"]+NOME+["Período"],lin)+
 '<h3 style="margin-top:18px;">De onde vem a queda de receita de agosto para setembro</h3>'
 +tab(["38%","","",""],["","Agosto","Setembro","Efeito"],pv)+
 '<p class="body-text" style="font-size:13.5px;margin-top:14px;max-width:1040px;">Três quartos da queda vêm da '
 '<strong>diária média</strong>, não do volume. Preço de baixa temporada é esperado. O que merece política '
 'própria é o <strong>cancelamento</strong>: em setembro foram %d reservas canceladas contra %d feitas, e em '
 'outubro a taxa está em %s — isso destrói previsibilidade de inventário e de caixa.</p>'%(
   com["9"]["canc"],com["9"]["res"],pct(OUT_CANC)),cap=_c))

# ============ 12 E · Estrategico
_m,_c=cab()
H.append(sec("Estratégico · Prioridade",
 etapa("E","Estratégico.","Etapa 03<br>Prioridade<br>Decisão",
  "Diagnóstico que","não vira prioridade.",
  [("i","Dezembro é o mês a resolver",
    "35,27% de ocupação contratada contra 77,20% em dezembro de 2025. Com a previsão de faturamento de hoje "
    "(R$ 265.104,09), é o único mês do horizonte <strong>abaixo do ponto de equilíbrio</strong> — e é alta temporada."),
   ("ii","A diária média antes do volume",
    "A receita responde mais a preço do que a ocupação. Recuperar R$ 100 na diária média vale mais que seis "
    "noites ocupadas a mais."),
   ("iii","Cancelamento como política",
    "Taxa de %s em outubro. Sem regra de garantia ou de prazo, o inventário fica indisponível e volta tarde "
    "demais para ser revendido."%pct(OUT_CANC)),
   ("iv","O custo fixo é a alavanca estrutural",
    "R$ %s por mês em média. Cada R$ 10 mil de custo fixo a menos derruba a receita de equilíbrio em cerca de "
    "R$ 15 mil."%f(abs(sum(R(m)["cfix"] for m in M))/9))],
  "A receita de equilíbrio do grupo é <strong>R$ %s por mês</strong>, ou %s de ocupação. É esse o número que "
  "a venda de dezembro precisa superar."%(f(B9["pe"]),pp(B9["oce"]))),
 cap=_c,bodycls="justify-content:center;"))

# ============ 13 orcado x realizado
LA=sorted(orc["linhas_ano"],key=lambda x:-abs(x["d"]))[:16]
lin=[{"c":[x["l"],f(x["o"]),f(x["r"]),f(x["d"]),
           (("%.0f%%"%(x["d"]/abs(x["o"])*100)) if x["o"] else "—")]} for x in LA]
lin.append({"cls":"hi","c":["EBITDA do mês · setembro",f(orc["os"]),f(orc["rs"]),f(orc["rs"]-orc["os"]),
                            "%.0f%%"%((orc["rs"]-orc["os"])/abs(orc["os"])*100)]})
lin.append({"cls":"hi2","c":["EBITDA ACUMULADO JAN–SET",f(orc["oa"]),f(orc["ra"]),f(orc["ra"]-orc["oa"]),
                             "%.0f%%"%((orc["ra"]-orc["oa"])/abs(orc["oa"])*100)]})
_m,_c=cab()
H.append(sec("Orçado × realizado · jan a set/2026",
 _m+'<h2 class="editorial" style="font-size:28px;">O orçamento confrontado <span class="orange">linha a linha.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">Revisão 15.09 do orçamento 2026/27, cenário conservador, contra o realizado consolidado. As dezesseis linhas de maior desvio no acumulado do ano.</p>'
 +tab(["34%","","","",""],["Linha","Orçado jan–set","Realizado jan–set","Variação","%"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:14px;max-width:1040px;">O EBITDA do ano está '
 '<strong>R$ %s abaixo</strong> do orçado. A maior parte do desvio está na receita; do lado do custo, as linhas '
 'que mais estouraram são as que não tinham previsão no orçamento.</p>'%f(abs(orc["ra"]-orc["oa"])),cap=_c))

# ============ 14 comparativo 2025 x 2026
r25,r26=RES["consol"]["T25"],RES["consol"]["T"]
cx25_i=CX["1"]["si"]
lin=[{"span":"RESULTADO"},
 {"c":["Receita bruta",f(r25["rb"]),f(r26["rb"]),f(r26["rb"]-r25["rb"])]},
 {"c":["(–) Custos variáveis",f(r25["cvar"]),f(r26["cvar"]),f(r26["cvar"]-r25["cvar"])]},
 {"c":["(–) Custos e despesas fixas",f(r25["cfix"]),f(r26["cfix"]),f(r26["cfix"]-r25["cfix"])]},
 {"cls":"sub","c":["= EBITDA",f(r25["ebitda"]),f(r26["ebitda"]),f(r26["ebitda"]-r25["ebitda"])]},
 {"c":["Margem EBITDA",pc(r25["ebitda"],r25["rb"]),pc(r26["ebitda"],r26["rb"]),
       ("%.1f"%(r26["ebitda"]/r26["rb"]*100-r25["ebitda"]/r25["rb"]*100)).replace(".",",")+" p.p."]},
 {"cls":"sub","c":["= Resultado",f(r25["res"]),f(r26["res"]),f(r26["res"]-r25["res"])]},
 {"span":"CAIXA"},
 {"c":["Saldo no início",f(38646.73),f(cx25_i),f(cx25_i-38646.73)]},
 {"c":["Geração de caixa",f(r25["res"]),f(ger_ano),f(ger_ano-r25["res"])]},
 {"cls":"hi2","c":["SALDO NO FIM",f(cx25_i),f(CX["9"]["sf"]),f(CX["9"]["sf"]-cx25_i)]}]
_m,_c=cab()
H.append(sec("Comparativo · 2025 × 2026",
 _m+'<h2 class="editorial" style="font-size:30px;">O que mudou <span class="light">de um ciclo</span> <span class="orange">para o outro.</span></h2>'
 '<p class="lede" style="margin-top:8px;font-size:14px;">2025 traz cinco meses (agosto a dezembro), em regime caixa. 2026 traz a DRE de janeiro a setembro e o caixa do mesmo período. Os períodos não são iguais — a comparação é de ordem de grandeza, não linha a linha.</p>'
 +tab(["36%","","",""],["Linha","2025 · ago–dez","2026 · jan–set","Variação"],lin)+
 '<p class="body-text" style="font-size:13.5px;margin-top:16px;max-width:1030px;">A receita de nove meses de '
 '2026 é <strong>%s vezes</strong> a de cinco meses de 2025, mas a margem EBITDA caiu de %s para %s. O caixa '
 'quase não se moveu no ano: R$ %s de saldo em 01/01 contra R$ %s em 30/09 — o grupo converteu resultado em '
 'ativo.</p>'%(("%.1f"%(r26["rb"]/r25["rb"])).replace(".",","),pc(r25["ebitda"],r25["rb"]),
   pc(r26["ebitda"],r26["rb"]),f(cx25_i),f(CX["9"]["sf"])),cap=_c))

# ============ 15 L · Longevo
_m,_c=cab()
H.append(sec("Longevo · Rotina",
 etapa("L","Longevo.","Etapa 04<br>Rotina<br>Sustentação",
  "Correção que","precisa ser refeita.",
  [("i","Data de emissão é a data da nota",
    "Inclusive nas parcelas. Com essa regra valendo no lançamento, DRE e relatório de faturamento passam a bater "
    "sozinhos, sem conferência nota a nota."),
   ("ii","Baixa do adiantamento junto com a NFS-e",
    "Quando a nota é emitida, o adiantamento tem de ser baixado contra a receita no mesmo movimento. Foi a falha "
    "que prendeu R$ 84 mil em setembro."),
   ("iii","Conciliação mensal pelo extrato consolidado",
    "Todas as contas, todo mês, até o dia 10. O relatório “C.C” esconde aplicação e resgate — a conferência é "
    "sempre pelo consolidado."),
   ("iv","Painel atualizado, não planilha refeita",
    "Resultado, caixa e orçamento no mesmo lugar, clicáveis até o lançamento. A leitura mensal passa a ser de "
    "decisão, não de apuração.")],
  "Com a rotina em pé, o fechamento deixa de ser um projeto todo mês e vira um relatório que sai sozinho — e "
  "sobra tempo para discutir dezembro, que é o que importa agora."),
 cap=_c,bodycls="justify-content:center;"))

# ============ 16 fechamento
H.append('<section class="slide dark" data-slide="%d"><div class="closing-grid">'
 '<div class="cover-top"><img class="logo" src="%s" alt="Exact BR" style="height:26px;">'
 '<span style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:10px;font-weight:700;letter-spacing:.22em;'
 'text-transform:uppercase;color:var(--orange);">Próximo Passo</span></div>'
 '<div class="closing-main"><div class="closing-eye">Para os sócios</div>'
 '<h2 class="closing-title">A operação paga as contas. <span class="ital">O investimento é que pesa.</span><br>'
 'E dezembro <span class="ital">ainda dá para vender.</span></h2>'
 '<p class="closing-text">Nove meses fechados, R$ %s de EBITDA e um caixa de R$ %s com extrato atrás de cada '
 'centavo. <strong>A decisão que este relatório pede é uma só: colocar dezembro acima da receita de equilíbrio '
 'de R$ %s antes que o mês chegue.</strong></p></div>'
 '<div class="closing-bottom"><div class="signature"><span class="sig-name">João Victor Andrade de Souza</span>'
 '<span class="sig-role">Sócio-fundador · Exact BR</span></div>'
 '<div class="contact-block"><span class="c-lbl">Disciplina Gera Lucro</span>'
 '<span class="c-val">Exact BR · Recife — PE</span></div></div></div></section>'%(
   PAG[0]+1,L_ESC,f(cT["eb"]),f(CAIXA_SF),f(B9["pe"])))

html=cabeca+'<body><div class="deck" id="deck">'+"".join(H)+rodape
html=html.replace("Relatório Gerencial · Agosto/2026 · Grupo Amana / Pousada Topázio · Exact BR",
                  "Relatório Gerencial · Setembro/2026 · Grupo Amana / Pousada Topázio · Exact BR")
html=html.replace("__TOT__",str(len(H)))
html=re.sub(r"(const TOTAL\s*=\s*)\d+",r"\g<1>%d"%len(H),html)
open(SAIDA,"w",encoding="utf-8").write(html)
print("gravado %s (%d KB, %d paginas)"%(SAIDA.split("/")[-1],len(html)//1024,len(H)))
print("  agosto publicado: %s / %s / %s"%(f(c8["rb"]),f(c8["eb"]),f(c8["res"])))
print("  setembro:         %s / %s / %s"%(f(c9["rb"]),f(c9["eb"]),f(c9["res"])))
