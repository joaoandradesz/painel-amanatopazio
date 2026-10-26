# -*- coding: utf-8 -*-
"""Planilha de conferencia: relacao de faturamento da contabilidade x receita no Omie/painel.
Amana, jan a set/2026, nota a nota em agosto e setembro."""
import os,json,collections
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
S=os.environ["S"]
OUT=os.environ["OUT"]
NAVY="FF0D0F1A"; ORANGE="FFF97316"; LIGHT="FFFFF7ED"; GREY="FFF3F4F6"
B=Font(bold=True); W=Font(bold=True,color="FFFFFFFF",size=11)
MON='#,##0.00'; THIN=Side(style='thin',color='FFD1D5DB')
def head(ws,cols,row=1):
    for i,(t,w) in enumerate(cols,1):
        c=ws.cell(row,i,t); c.font=W; c.fill=PatternFill('solid',fgColor=NAVY)
        c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width=w
    ws.row_dimensions[row].height=30
    ws.freeze_panes=ws.cell(row+1,1)
CONTAB={'01/2026':529990.86,'02/2026':270043.26,'03/2026':88285.52,'04/2026':57473.27,
 '05/2026':272765.44,'06/2026':297456.07,'07/2026':551271.84,'08/2026':750504.80,'09/2026':595018.22}
PAINEL={'01/2026':529990.86,'02/2026':270043.26,'03/2026':88285.52,'04/2026':57473.27,
 '05/2026':272765.44,'06/2026':297456.07,'07/2026':568427.75,'08/2026':734874.60,'09/2026':595018.22}
NOTA={'07/2026':'NFS-e 129 lancada com a data da venda no cartao (10/07) em vez da data da nota (agosto)',
      '08/2026':'(-) NFS-e 129 que ficou em julho  (+) R$ 1.525,67 de hospedagem faturada sem NFS-e'}
R=json.load(open(os.path.join(S,'cruzamento.json')))
wb=Workbook(); 
# ---------- RESUMO
ws=wb.active; ws.title="Resumo"
ws['A1']="Relação de faturamento da contabilidade  x  Receita de Hospedagem no Omie / painel"
ws['A1'].font=Font(bold=True,size=14,color=NAVY)
ws['A2']="AMANA EMPREENDIMENTOS TURISTICOS LTDA  ·  CNPJ 55.941.449/0001-46  ·  jan a set/2026"
ws['A2'].font=Font(size=10,color="FF6B7280")
ws['A3']="Fonte contabilidade: Relatório de Faturamento emitido em 14/10/2026 + relações detalhadas de agosto e setembro. Fonte painel: títulos a receber do Omie, categoria 1.01.02, por data de emissão."
ws['A3'].font=Font(size=9,italic=True,color="FF6B7280")
cols=[("Mês",12),("Contabilidade",16),("Painel / Omie",16),("Diferença",14),("Explicação da diferença",92)]
head(ws,cols,5)
r=6; tc=tp=0
for m in sorted(CONTAB,key=lambda k:k[:2]):
    dif=round(PAINEL[m]-CONTAB[m],2); tc+=CONTAB[m]; tp+=PAINEL[m]
    ws.cell(r,1,m); ws.cell(r,2,CONTAB[m]); ws.cell(r,3,PAINEL[m]); ws.cell(r,4,dif)
    ws.cell(r,5,NOTA.get(m,"bate ao centavo"))
    for c in range(1,6):
        cel=ws.cell(r,c); cel.border=Border(bottom=THIN)
        if c in (2,3,4): cel.number_format=MON
    if abs(dif)>=0.05:
        for c in range(1,6): ws.cell(r,c).fill=PatternFill('solid',fgColor=LIGHT)
        ws.cell(r,4).font=Font(bold=True,color="FFB91C1C")
    else:
        ws.cell(r,5).font=Font(color="FF059669")
    r+=1
ws.cell(r,1,"TOTAL").font=B
for c,v in ((2,tc),(3,tp),(4,round(tp-tc,2))):
    cel=ws.cell(r,c,v); cel.font=B; cel.number_format=MON; cel.fill=PatternFill('solid',fgColor=GREY)
ws.cell(r,5,"A divergência de todo o período é R$ 1.525,71 — hospedagem faturada sem NFS-e em agosto (1.525,67) e 4 centavos de arredondamento da contabilidade.").font=B
r+=3
for t in ("O que o cruzamento mostra, nota a nota:",
  "·  SETEMBRO: 68 notas na relação da contabilidade, R$ 595.018,22. As 68 estão no Omie, com a receita dentro de setembro. Diferença: ZERO.",
  "·  AGOSTO: 74 notas, R$ 750.504,80. As 74 estão no Omie. 73 com a receita dentro de agosto; só a NFS-e 129 está em julho.",
  "·  Nenhuma nota da contabilidade está faltando no Omie, e nenhuma nota do Omie está fora da relação da contabilidade, em nenhum dos dois meses.",
  "·  Nenhuma nota cancelada foi contada como receita.",
  "",
  "Pendência única, e ela se resolve sozinha nos dois meses:",
  "·  NFS-e 129 — MATHEUS ROCCA DOS SANTOS — R$ 17.155,91. O título está com data de emissão 10/07/2026, que é a data da venda no cartão; a nota é de agosto.",
  "·  Corrigindo a data para a data da nota: julho passa de 568.427,75 para 551.271,84 (= contabilidade, exato) e agosto vai para 752.030,51.",
  "·  Sobra então apenas R$ 1.525,67 em agosto, que é hospedagem faturada sem NFS-e — não é erro, é receita sem nota.",
  "",
  "Observação sobre 2025: out a dez/2025 não entram nesta comparação. Nesses meses o Omie só tem a perna de Adiantamento de Hospedagem (venda antecipada da temporada) e o painel usa regime de caixa conciliado com os extratos, não competência."):
    ws.cell(r,1,t).font=Font(bold=t.endswith(':'),size=10)
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=5); r+=1
# ---------- NOTA A NOTA
for rot,aba in (("08/2026","Agosto nota a nota"),("09/2026","Setembro nota a nota")):
    ln=R[rot]; w=wb.create_sheet(aba)
    w['A1']=f"{aba} — Amana, {rot}.  Contabilidade x receita no Omie (categoria 1.01.02 Receita de Hospedagem)"
    w['A1'].font=Font(bold=True,size=12,color=NAVY)
    cols=[("NFS-e",9),("Cliente",44),("Valor na contabilidade",17),("Receita no Omie",15),
          ("Dentro de "+rot,15),("Em outro mês",14),("Diferença",12),("Onde a receita foi reconhecida",34),
          ("Parcelas",9),("Adiantamento (conta de controle)",20)]
    head(w,cols,3); r=4
    for x in ln:
        pend=abs(x['dif'])>0.05 or abs(x['fora'])>0.05
        for i,v in enumerate([int(x['nf']),x['cli'],x['contab'],x['omie'],x['no_mes'],x['fora'],
                              x['dif'],x['meses'],x['npar'],x['adiant']],1):
            c=w.cell(r,i,v); c.border=Border(bottom=THIN)
            if i in (3,4,5,6,7,10): c.number_format=MON
            if pend: c.fill=PatternFill('solid',fgColor=LIGHT)
        if pend: w.cell(r,7).font=Font(bold=True,color="FFB91C1C")
        r+=1
    w.cell(r,2,"TOTAL").font=B
    for i,k in ((3,'contab'),(4,'omie'),(5,'no_mes'),(6,'fora'),(10,'adiant')):
        c=w.cell(r,i,round(sum(y[k] for y in ln),2)); c.font=B; c.number_format=MON
        c.fill=PatternFill('solid',fgColor=GREY)
    w.cell(r,1,len(ln)).font=B
    w.auto_filter.ref=f"A3:J{r-1}"
# ---------- PARCELAS REALOCADAS
w=wb.create_sheet("Parcelas realocadas")
w['A1']="11 parcelas de 6 notas de agosto que estavam com a data do vencimento em vez da data da nota — já corrigidas"
w['A1'].font=Font(bold=True,size=12,color=NAVY)
cols=[("NFS-e",9),("Cliente",40),("Total da NF",14),("Parcela",9),("Valor",13),
      ("Estava em",13),("Foi para",13),("Realocada",11),("Situação",12),("Cód. Omie",13)]
head(w,cols,3)
import csv
p="/Users/joaoandrade/Library/Mobile Documents/com~apple~CloudDocs/Claude VS/Parcelas realocadas para agosto-2026 - Amana.csv"
rows=list(csv.reader(open(p,encoding='utf-8-sig'),delimiter=';'))[1:]
r=4; num=lambda v: float(v.replace('.','').replace(',','.'))
for x in rows:
    vals=[int(x[0]),x[1],num(x[2]),int(x[3]),num(x[4]),x[5],x[6],x[7],x[9],int(x[10])]
    for i,v in enumerate(vals,1):
        c=w.cell(r,i,v); c.border=Border(bottom=THIN)
        if i in (3,5): c.number_format=MON
        if x[7]=='SIM': c.fill=PatternFill('solid',fgColor=LIGHT)
    r+=1
w.cell(r,2,"Total realocado para agosto").font=B
c=w.cell(r,5,round(sum(num(x[4]) for x in rows if x[7]=='SIM'),2)); c.font=B; c.number_format=MON
r+=2
w.cell(r,2,"De onde saiu cada parcela:").font=B; r+=1
for m,v in (("Setembro",20291.35),("Outubro",5453.77),("Novembro",3763.11),("TOTAL",29508.23)):
    w.cell(r,2,m).font=(B if m=="TOTAL" else Font())
    c=w.cell(r,5,v); c.number_format=MON; c.font=(B if m=="TOTAL" else Font()); r+=1
# ---------- NOTAS DE ADIANTAMENTO
w=wb.create_sheet("Notas presas no adiantamento")
w['A1']="Notas de setembro que estavam lançadas somente como Adiantamento de Hospedagem (conta de controle, fora da DRE) — já corrigidas"
w['A1'].font=Font(bold=True,size=12,color=NAVY)
w['A2']="A venda no cartão gera o título de Adiantamento. Quando a NFS-e é emitida, falta a baixa do adiantamento contra a receita — e a receita não entra na DRE."
w['A2'].font=Font(size=9,italic=True,color="FF6B7280")
cols=[("NFS-e",9),("Cliente",44),("Valor da nota",15),("Situação antes",46)]
head(w,cols,4)
st=json.load(open(os.path.join(S,'set_contab.json')))
adi=json.load(open('nfse_adiant.json'))
r=5; t=0
for n in adi:
    c=st[n]
    ja = n=="214"
    for i,v in enumerate([int(n),c['cli'],c['val'],
        "receita já existia; só a data da parcela estava errada" if ja else "só a perna de adiantamento; sem receita na DRE"],1):
        cel=w.cell(r,i,v); cel.border=Border(bottom=THIN)
        if i==3: cel.number_format=MON
        if not ja: cel.fill=PatternFill('solid',fgColor=LIGHT)
    if not ja: t+=c['val']
    r+=1
w.cell(r,2,"Receita de setembro que estava fora da DRE (12 notas)").font=B
c=w.cell(r,3,round(t,2)); c.font=B; c.number_format=MON
wb.save(OUT); print("gravado:",OUT)
