"""Publica as três páginas de ferramentas/ no Ferramentas (ferramentas.fiel.one).

Rodar depois de empacota_ferramentas.py. Fala direto com o conector MCP ferramentas-exact,
porque um HTML de 2 MB não cabe numa chamada do Claude. O endereço (com o token) é lido
de ~/.claude.json, nunca fica neste repositório.

Uso: python3 publica_ferramentas.py "nota da versão"
     python3 publica_ferramentas.py --listar     (só confere o acesso)
"""
import json, os, ssl, sys, urllib.request
import certifi

AQUI = os.path.dirname(os.path.abspath(__file__))
EMPRESA = 'amana'  # identificador no Ferramentas; conferir com --listar

FERRAMENTAS = [
    # (arquivo, identificador, nome, descrição, ícone)
    ('index.html', 'painel-gerencial-amana', 'Painel gerencial', 'DRE, caixa, orçado e comercial do grupo, com cada número abrindo até o lançamento.', '📊'),
    ('socios.html', 'painel-socios-amana', 'Painel dos sócios', 'Visão dos sócios: resultado e caixa do grupo, mês a mês.', '🤝'),
    ('caixa.html', 'caixa-diario-amana', 'Caixa diário', 'Saldo dos bancos e o que entra e sai nos próximos dias.', '💵'),
]


def url_conector():
    cfg = json.load(open(os.path.expanduser('~/.claude.json')))
    achados = []
    def busca(o):
        if isinstance(o, dict):
            if 'ferramentas-exact' in o and isinstance(o['ferramentas-exact'], dict):
                achados.append(o['ferramentas-exact'].get('url'))
            for v in o.values(): busca(v)
    busca(cfg)
    assert achados and achados[0], 'conector ferramentas-exact não encontrado em ~/.claude.json'
    return achados[0]


def chama(ferramenta, args):
    corpo = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                        'params': {'name': ferramenta, 'arguments': args}}).encode()
    req = urllib.request.Request(url_conector(), corpo, {
        'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'})
    txt = urllib.request.urlopen(req, timeout=300, context=ssl.create_default_context(cafile=certifi.where())).read().decode()
    if txt.lstrip().startswith('event:') or 'data:' in txt[:20]:
        txt = next(l[5:] for l in txt.splitlines() if l.startswith('data:'))
    r = json.loads(txt)
    if 'error' in r or r.get('result', {}).get('isError'):
        sys.exit(f'{ferramenta} falhou: {json.dumps(r, ensure_ascii=False)[:800]}')
    return '\n'.join(c.get('text', '') for c in r['result']['content'])


if __name__ == '__main__':
    if '--listar' in sys.argv:
        print(chama('listar_empresas', {}))
        sys.exit()
    nota = sys.argv[1] if len(sys.argv) > 1 else None
    for arq, ident, nome, desc, icone in FERRAMENTAS:
        html = open(os.path.join(AQUI, 'ferramentas', arq), encoding='utf-8').read()
        args = {'empresa': EMPRESA, 'ferramenta': ident, 'nome': nome, 'descricao': desc,
                'icone': icone, 'categoria': 'Financeiro', 'html': html}
        if nota: args['nota'] = nota
        print(f'== {arq}\n' + chama('publicar_ferramenta', args))
