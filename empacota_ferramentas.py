"""Gera a versão do painel para o Ferramentas (ferramentas.fiel.one), abaixo de 5 MB.

O único <script> da página (const D + código) vai compactado em gzip/base64 e o
navegador descompacta ao abrir (DecompressionStream, nativo). Tela e dados não mudam.

Uso: python3 empacota_ferramentas.py  ->  ferramentas/<pagina>.html
"""
import base64, gzip, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PAGINAS = ['index.html', 'socios.html', 'caixa.html']
LIMITE = 5 * 1024 * 1024

CARREGADOR = """<script id="dados-gz" type="application/octet-stream">%s</script>
<script>
(async function () {
  var b = atob(document.getElementById('dados-gz').textContent), u = new Uint8Array(b.length);
  for (var i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
  var txt = await new Response(new Blob([u]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
  var s = document.createElement('script'); s.textContent = txt; document.body.appendChild(s);
})();
</script>"""


def empacota(html):
    m = list(re.finditer(r'<script>(.*?)</script>', html, re.S))
    assert len(m) == 1 and 'const D=' in m[0].group(1)[:20], 'esperava um único <script> começando por const D='
    gz = base64.b64encode(gzip.compress(m[0].group(1).encode('utf-8'), 9)).decode()
    # ponytail: substituição por fatia, não por regex, para não interpretar o conteúdo
    return html[:m[0].start()] + CARREGADOR % gz + html[m[0].end():]


if __name__ == '__main__':
    os.makedirs(os.path.join(AQUI, 'ferramentas'), exist_ok=True)
    for p in PAGINAS:
        original = open(os.path.join(AQUI, p), encoding='utf-8').read()
        if not original.lstrip().lower().startswith('<!doctype html'):
            original = '<!doctype html>\n' + original
        saida = empacota(original)
        destino = os.path.join(AQUI, 'ferramentas', p)
        open(destino, 'w', encoding='utf-8').write(saida)
        tam = len(saida.encode())
        print(f'{p}: {len(original.encode())//1024} KB -> {tam//1024} KB')
        if tam > LIMITE:
            sys.exit(f'{p} passou de 5 MB')
