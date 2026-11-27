# -*- coding: utf-8 -*-
"""Camada de ESTIMATIVA da projecao de caixa (caixa.html).

O painel firme enxerga so o que esta lancado no Omie, e nestas bases o Omie e
alimentado depois do fato. Esta camada soma, a parte e marcada, o que ainda nao
foi lancado mas acontece todo mes. Nada aqui grava no Omie.

1. DESPESA RECORRENTE. Categoria de despesa fixa (folha e encargos, pro-labore,
   arrendamento/aluguel, sistemas, energia, agua, telefonia/internet,
   alojamento, contabilidade/consultoria) que saiu do banco em TODOS os meses
   fechados da base. Estimativa do mes = media da base pela data do pagamento
   menos o que ja esta lancado (titulo ou agenda) na mesma categoria naquele
   mes, nunca abaixo de zero. Cai no dia tipico: mediana dos dias de pagamento,
   ponderada pelo valor.
2. RECEITA. Amana: vendas previstas por competencia do relatorio comercial
   (jan/fev 2027: receita bruta do mesmo mes de 2026, Amana + Topazio),
   proporcional aos dias da janela, menos o que ja e titulo ou agenda da GetNet
   nesses dias, menos a taxa de cartao. Boldro: venda media por dia da semana
   nas ultimas 8 semanas do 3LM, liquida da MDR, com o prazo de credito que o
   extrato mostra (cartao no dia util seguinte, PIX no dia, dinheiro fica no
   fundo fixo e fora do saldo). YO e Topazio: zero.

Uso:  python3 caixa/estimativa.py   (depois de coleta_dash.py)  -> estimativa.json
O mesmo arquivo serve painel-yoboldro e painel-amanatopazio: o grupo sai do EMP
do coleta_dash.py ao lado.
"""
import collections
import datetime
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from omie_api import call  # noqa: E402
import coleta_dash as C  # noqa: E402

R2 = (lambda v: round((v or 0) + 0.0, 2))
dt = (lambda s: datetime.datetime.strptime(s, '%d/%m/%Y').date())
br = (lambda d: d.strftime('%d/%m/%Y'))
fm = (lambda v: format(R2(v), ',.2f').replace(',', '@').replace('.', ',').replace('@', '.'))
MES = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
SEM = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']
VS = os.path.join(os.path.dirname(os.path.dirname(AQUI)),
                  'Library/Mobile Documents/com~apple~CloudDocs/Claude VS')

# meses fechados da base. A Boldro abriu o salao no fim de agosto (agosto tem
# R$ 7 mil de folha zero e quase nenhuma compra): base dela e set-out, senao a
# regra "todos os meses" deixaria a folha de fora.
BASE = {'boldro': ['2026-09', '2026-10']}
BASE_PADRAO = ['2026-08', '2026-09', '2026-10']
FIXA = re.compile(r'sal[áa]rio|encargo|fgts|inss|pr[óo]-?labore|arrendamento|aluguel(?! de ve)|'
                  r'sistemas|energia|[áa]gua e esgoto|telefon|internet|alojamento|'
                  r'contabilidade|consultoria|advocacia|vale transporte|benef[íi]cios', re.I)
# Boldro: a receita entra pelo ritmo de vendas do horizonte inteiro, entao o
# custo que anda com a venda (insumos, bebidas, caches, diaristas, ISS) precisa
# entrar junto, pela mesma base set-out. Sem isso a camada somava R$ 3,25 mi de
# venda contra R$ 248 mil de custo fixo em 90 dias. Nas outras a receita
# estimada e curta (Amana: so nov-dez, reserva ja vendida) e fica so o fixo.
VARIAVEL = {'boldro'}
FORA_VAR = re.compile(r'^2\.(07|08|09|10)\.')     # investimento, intercompany e afins
FORA_VAR_DESC = re.compile(r'taxa.*cart', re.I)     # MDR ja sai liquida da receita
INTER = ('BOLDRO PRAIA', 'YO NORONHA', 'POUSADA TOPAZIO', 'AMANA EMPREENDIMENTOS')
# bancos fechados no horizonte (cartao credita no dia util seguinte)
FERIADOS = {datetime.date(2026, 12, 25), datetime.date(2027, 1, 1),
            datetime.date(2027, 2, 8), datetime.date(2027, 2, 9)}
# Amana: "Vendas Prev Competencia (Checkout)", relatorio comercial de outubro, pag. 3
AMANA_COMP = {'2026-11': 474249.81, '2026-12': 299253.65,
              # jan/fev 2027: o relatorio comercial so traz 2027 somado. Base = receita bruta
              # do mesmo mes de 2026 no painel, Amana + Topazio (a Topazio faturava direto ate abril).
              # ponytail: sazonalidade pura, sem crescimento; trocar pela previsao mensal quando vier.
              '2027-01': 904819.76, '2027-02': 444242.51}
AMANA_BASE_2026 = {'2027-01', '2027-02'}


def mes_rot(m):
    return MES[int(m[5:]) - 1]


CACHE = os.path.join(AQUI, 'estimativa_base.json')


def _cache():
    try:
        return json.load(open(CACHE, encoding='utf-8'))
    except Exception:
        return {}


def historico(emp, meses):
    """Saida realizada por categoria, mes a mes (o extrato trunca em periodo longo).
    Mes fechado nao muda (so por retificacao declarada): a base fica guardada em
    estimativa_base.json e o Omie so e lido quando a lista de meses muda. Para
    reler, apague o arquivo. Guarda codigo, data e valor; nome nenhum."""
    ch = _cache()
    if ch.get(emp, {}).get('meses') == meses:
        return [(c, dt(d), v) for c, d, v in ch[emp]['mov']]
    L = []
    for cc, _ in C.EMP[emp]['contas']:
        for m in meses:
            a = datetime.date(int(m[:4]), int(m[5:]), 1)
            b = (a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
            r = call(emp, 'financas/extrato', 'ListarExtrato',
                     {'nCodCC': cc, 'dPeriodoInicial': br(a), 'dPeriodoFinal': br(b)})
            for x in r.get('listaMovimentos') or []:
                v = x.get('nValorDocumento') or 0
                if (v >= 0 or x.get('cSituacao') == 'Previsto'
                        or (x.get('cDesCliente') or '').startswith('SALDO')
                        or 'Transf' in (x.get('cOrigem') or '')
                        or (x.get('cCodCategoria') or '').startswith('0.')
                        or any(t in (x.get('cDesCliente') or '').upper() for t in INTER)):
                    continue
                L.append((x['cCodCategoria'], dt(x['dDataLancamento']), -v))
    ch = _cache()
    ch[emp] = {'meses': meses, 'mov': [(c, br(d), R2(v)) for c, d, v in L]}
    json.dump(ch, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    return L


def categorias(emp):
    ch = _cache()
    if ch.get('_cats', {}).get(emp):
        return ch['_cats'][emp]
    CT = C.cats(emp)
    ch.setdefault('_cats', {})[emp] = CT
    json.dump(ch, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    return CT


def mediana_pond(pares):
    pares = sorted(pares)
    tot, acc = sum(p for _, p in pares), 0
    for d, p in pares:
        acc += p
        if acc >= tot / 2:
            return d
    return pares[-1][0]


def meses_horizonte(H, F):
    out, a = [], H.replace(day=1)
    while a <= F:
        out.append(a.strftime('%Y-%m'))
        a = (a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return out


def despesa(emp, x, H, F, CT):
    meses = BASE.get(emp, BASE_PADRAO)
    por = collections.defaultdict(lambda: {'m': collections.defaultdict(float), 'dias': []})
    var = collections.defaultdict(lambda: collections.defaultdict(float))
    for cod, d, v in historico(emp, meses):
        desc = CT.get(cod) or cod
        if not FIXA.search(desc):
            if emp in VARIAVEL and not FORA_VAR.match(cod) and not FORA_VAR_DESC.search(desc):
                var[desc][d.strftime('%Y-%m')] += v
            continue
        # ponytail: movimento rateado entra inteiro na 1a categoria do rateio; a
        # base fica certa no total e torta na divisao. Ler o rateio pelo titulo
        # (ConsultarContaPagar) se a divisao importar.
        por[desc]['m'][d.strftime('%Y-%m')] += v
        por[desc]['dias'].append((d.day, v))
    firme = collections.defaultdict(float)
    for i in x['itens'] + (x.get('agenda') or []):
        if i['lado'] == 'pagar':
            firme[(i['cat'], i['d'][6:] + '-' + i['d'][3:5])] += i['v']
    itens, prem = [], []
    for desc, p in sorted(por.items(), key=lambda kv: -sum(kv[1]['m'].values())):
        if not all(p['m'].get(m) for m in meses):
            continue
        med = sum(p['m'][m] for m in meses) / len(meses)
        dia = mediana_pond(p['dias'])
        base_txt = ' · '.join('%s %s' % (mes_rot(m), fm(p['m'][m])) for m in meses)
        linha = {'cat': desc, 'media': R2(med), 'dia': dia,
                 'base': {mes_rot(m): R2(p['m'][m]) for m in meses}, 'mes': {}}
        for mh in meses_horizonte(H, F):
            a = datetime.date(int(mh[:4]), int(mh[5:]), 1)
            ult = ((a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                   - datetime.timedelta(days=1)).day
            d = a.replace(day=min(dia, ult))
            if not (H <= d <= F):
                continue
            lan = firme.get((desc, mh), 0.0)
            est = R2(max(0.0, med - lan))
            linha['mes'][mes_rot(mh)] = {'lancado': R2(lan), 'est': est}
            if est <= 0:
                continue
            itens.append({'lado': 'pagar', 'd': br(d), 'nome': 'Estimativa · ' + desc, 'cat': desc,
                          'v': est, 'fonte': 'estimado',
                          'calc': ('Média de %s pela data do pagamento: R$ %s (%s). Já lançado no '
                                   'Omie em %s nesta categoria: R$ %s. Estimado: R$ %s, no dia %02d, '
                                   'dia típico de pagamento.'
                                   % ('–'.join(mes_rot(m) for m in (meses[0], meses[-1])), fm(med),
                                      base_txt, mes_rot(mh), fm(lan), fm(est), dia))})
        prem.append(linha)
    # custo variavel: media da base espalhada por igual nos dias da janela
    var = {k: v for k, v in var.items() if all(v.get(m) for m in meses)}
    if var:
        medv = {k: sum(v[m] for m in meses) / len(meses) for k, v in var.items()}
        totv = sum(medv.values())
        top = ', '.join('%s %s' % (k, fm(v)) for k, v in sorted(medv.items(), key=lambda kv: -kv[1])[:6])
        linha = {'cat': 'Custos variáveis da operação (%d categorias)' % len(var), 'media': R2(totv),
                 'dia': None, 'tipo': 'variavel',
                 'base': {mes_rot(m): R2(sum(v[m] for v in var.values())) for m in meses}, 'mes': {},
                 'categorias': {k: R2(v) for k, v in sorted(medv.items(), key=lambda kv: -kv[1])}}
        for mh in meses_horizonte(H, F):
            a = datetime.date(int(mh[:4]), int(mh[5:]), 1)
            ult = ((a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
                   - datetime.timedelta(days=1)).day
            ds = [a + datetime.timedelta(days=i) for i in range(ult) if H <= a + datetime.timedelta(days=i) <= F]
            if not ds:
                continue
            prop = sum(medv[k] * len(ds) / ult for k in medv)
            lan = sum(firme.get((k, mh), 0.0) for k in medv)
            est = max(0.0, prop - lan)
            linha['mes'][mes_rot(mh)] = {'lancado': R2(lan), 'est': R2(est)}
            calc = ('Custos que andam com a venda, %d categorias pagas em todos os meses de %s: média de '
                    'R$ %s por mês pela data do pagamento (maiores: %s). Em %s, %d de %d dias na janela: '
                    'R$ %s, menos R$ %s já lançados no Omie nessas categorias = R$ %s, espalhado por igual: '
                    'R$ %s por dia.'
                    % (len(var), '–'.join(mes_rot(m) for m in (meses[0], meses[-1])), fm(totv), top,
                       mes_rot(mh), len(ds), ult, fm(prop), fm(lan), fm(est), fm(est / len(ds))))
            for d in ds:
                if est > 0:
                    itens.append({'lado': 'pagar', 'd': br(d), 'nome': 'Estimativa · custos variáveis',
                                  'cat': 'Insumos, bebidas, cachês e outros variáveis', 'v': R2(est / len(ds)),
                                  'fonte': 'estimado', 'calc': calc})
        prem.append(linha)
    return itens, prem, meses


def dia_util(d):
    while d.weekday() >= 5 or d in FERIADOS:
        d += datetime.timedelta(days=1)
    return d


def receita_boldro(x, H, F):
    V = json.load(open(os.path.join(VS, 'omie-boldro', 'vendas.json')))
    P = json.load(open(os.path.join(VS, 'omie-boldro', 'dados_painel.json')))
    dias = sorted(((dt(d['data'] + '/' + m[:4]), d['valor']) for m in V for d in V[m]['dias']))
    ult = dias[-1][0]
    janela = [(d, v) for d, v in dias if (ult - d).days < 56]
    dow = collections.defaultdict(list)
    for d, v in janela:
        dow[d.weekday()].append(v)
    media = {k: sum(v) / len(v) for k, v in dow.items()}
    mref = ult.strftime('%Y-%m')
    formas = dict(P['receita'][mref]['formas'])
    tot = sum(formas.values())
    cartao = sum(v for k, v in formas.items() if k.lower().startswith(('cartão', 'crédito')))
    pix = sum(v for k, v in formas.items() if 'pix' in k.lower())
    dinheiro = tot - cartao - pix
    mdr = P['taxas'][mref]['cartao']['pc'] / 100
    fat = cartao / tot * (1 - mdr) + pix / tot
    # ja lancado: a Boldro nao tem titulo a receber nem agenda da GetNet no
    # horizonte (receita nasce da conciliacao); se aparecer, desconta no mes
    firme = collections.defaultdict(float)
    for i in x['itens'] + (x.get('agenda') or []):
        if i['lado'] == 'receber':
            firme[i['d'][3:]] += i['v']
    credito = collections.defaultdict(list)
    d = H - datetime.timedelta(days=7)
    while d <= F:
        bruto = media[d.weekday()]
        liq_c = bruto * cartao / tot * (1 - mdr)
        liq_p = bruto * pix / tot
        for quando, v, como in ((dia_util(d + datetime.timedelta(days=1)), liq_c, 'cartão'),
                                (d, liq_p, 'PIX')):
            if H <= quando <= F:
                credito[quando].append((d, v, como, bruto))
        d += datetime.timedelta(days=1)
    porm = collections.defaultdict(float)
    for q, L in credito.items():
        porm[q.strftime('%m/%Y')] += sum(v for _, v, _, _ in L)
    itens = []
    for q in sorted(credito):
        L = credito[q]
        k = q.strftime('%m/%Y')
        esc = max(0.0, 1 - firme.get(k, 0) / porm[k]) if porm[k] else 0
        v = R2(sum(v for _, v, _, _ in L) * esc)
        if v <= 0:
            continue
        partes = '; '.join('%s de %s (%s, venda média de %s R$ %s)' % (fm(vv), como, br(s)[:5], SEM[s.weekday()], fm(b))
                           for s, vv, como, b in L)
        itens.append({'lado': 'receber', 'd': br(q), 'nome': 'Estimativa · vendas do salão',
                      'cat': 'Receita operacional (salão)', 'v': v, 'fonte': 'estimado',
                      'calc': ('Crédito estimado neste dia: %s. Venda média por dia da semana nas 8 semanas '
                               'de %s a %s no 3LM; cartão %.1f%% da venda, líquido da MDR de %.2f%%, entra no '
                               'dia útil seguinte; PIX %.1f%% entra no dia; dinheiro %.1f%% vai para o fundo '
                               'fixo e fica fora do saldo.'
                               % (partes, br(janela[0][0])[:5], br(ult)[:5], cartao / tot * 100, mdr * 100,
                                  pix / tot * 100, dinheiro / tot * 100))})
    prem = {'texto': ('Venda média por dia da semana nas 8 semanas de %s a %s (3LM), sem sazonalidade. '
                      'Sobre a venda: cartão %.1f%% (líquido da MDR de %.2f%%, crédito no dia útil seguinte, '
                      'como o extrato da GetNet mostra), PIX %.1f%% (no dia), dinheiro %.1f%% (fundo fixo, '
                      'fora do saldo). Fator líquido que entra no banco: %.1f%% da venda. Já lançado no Omie '
                      'no horizonte: nada, a receita nasce da conciliação.'
                      % (br(janela[0][0]), br(ult), cartao / tot * 100, mdr * 100, pix / tot * 100,
                         dinheiro / tot * 100, fat * 100)),
            'dia_semana': {SEM[k]: R2(v) for k, v in sorted(media.items())}}
    return itens, prem


def receita_amana(x, H, F):
    gn = x.get('getnet') or {}
    taxa = abs(gn.get('taxa') or 0) / gn['bruto'] if gn.get('bruto') else 0
    firme = collections.defaultdict(float)
    for i in x['itens'] + (x.get('agenda') or []):
        if i['lado'] == 'receber':
            firme[dt(i['d'])] += i['v']
    itens, linhas = [], []
    for m, comp in sorted(AMANA_COMP.items()):
        a = datetime.date(int(m[:4]), int(m[5:]), 1)
        ult = (a.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
        ds = [a + datetime.timedelta(days=i) for i in range(ult.day) if H <= a + datetime.timedelta(days=i) <= F]
        if not ds:
            continue
        prop = comp * len(ds) / ult.day
        lan = sum(firme.get(d, 0) for d in ds)
        bruto = max(0.0, prop - lan)
        liq = bruto * (1 - taxa)
        linhas.append({'mes': mes_rot(m), 'comp': comp, 'dias': len(ds), 'de': ult.day,
                       'proporcional': R2(prop), 'lancado': R2(lan), 'estimado': R2(liq)})
        fonte = ('Receita bruta de %s/2026 no painel (Amana + Topázio, mesmo mês do ano passado; o relatório '
                 'comercial só traz 2027 somado)' % mes_rot(m) if m in AMANA_BASE_2026 else
                 'Vendas previstas por competência em %s no relatório comercial de outubro' % mes_rot(m))
        calc = ('%s: R$ %s. '
                'Proporcional aos %d de %d dias do mês dentro da janela: R$ %s. Já lançado no Omie nesses '
                'dias (título a receber ou agenda da GetNet): R$ %s. Sobra R$ %s, menos a taxa de cartão '
                'de %.2f%% = R$ %s, espalhado por igual: R$ %s por dia.'
                % (fonte, fm(comp), len(ds), ult.day, fm(prop), fm(lan), fm(bruto), taxa * 100,
                   fm(liq), fm(liq / len(ds))))
        for d in ds:
            if liq > 0:
                itens.append({'lado': 'receber', 'd': br(d), 'nome': ('Estimativa · mesmo mês de 2026' if m in AMANA_BASE_2026 else 'Estimativa · reservas vendidas'),
                              'cat': 'Receita de Hospedagem', 'v': R2(liq / len(ds)),
                              'fonte': 'estimado', 'calc': calc})
    prem = {'texto': ('Vendas previstas por competência (checkout) do relatório comercial de outubro: '
                      'nov R$ 474.249,81 e dez R$ 299.253,65. Cada mês proporcional aos dias dentro da janela, '
                      'menos o que já é título a receber ou agenda da GetNet nesses dias, menos a taxa de '
                      'cartão de %.2f%% (a da agenda da GetNet), espalhado por igual. Janeiro e fevereiro: o relatório '
                      'só traz 2027 somado (R$ 334.034,63), então a base é a receita bruta do mesmo mês de 2026 '
                      'no painel, Amana + Topázio (jan R$ 904.819,76, fev R$ 444.242,51), sem crescimento. Competência '
                      'não é caixa: reserva paga antes já entrou e não volta a entrar.' % (taxa * 100)),
            'meses': linhas}
    return itens, prem


def roda():
    D = json.load(open(os.path.join(AQUI, 'dados_caixa.json'), encoding='utf-8'))
    H, F = dt(D['hoje']), dt(D['fim'])
    out = {'gerado': datetime.datetime.now().strftime('%d/%m/%Y às %H:%M'), 'ents': {}}
    for emp in C.EMP:
        x = D['ents'][emp]
        CT = categorias(emp)
        itens, prem, meses = despesa(emp, x, H, F, CT)
        rec, prem_r = [], None
        if emp == 'boldro':
            rec, prem_r = receita_boldro(x, H, F)
        elif emp == 'amana':
            rec, prem_r = receita_amana(x, H, F)
        out['ents'][emp] = {'itens': itens + rec, 'despesa': prem, 'receita': prem_r,
                            'base': '–'.join(mes_rot(m) for m in (meses[0], meses[-1]))}
        print('  %-8s despesa estimada %12s em %2d lançamentos | receita estimada %12s'
              % (emp, fm(sum(i['v'] for i in itens)), len(itens), fm(sum(i['v'] for i in rec))))
    json.dump(out, open(os.path.join(AQUI, 'estimativa.json'), 'w'), ensure_ascii=False)


if __name__ == '__main__':
    roda()
