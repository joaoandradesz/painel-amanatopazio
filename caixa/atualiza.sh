#!/bin/sh
# Atualiza e publica o dashboard de caixa. Um comando so, para a rotina
# agendada precisar de uma aprovacao em vez de tres.
set -e
cd "$(dirname "$0")/.."
echo "== lendo o Omie"
python3 caixa/coleta_dash.py
echo "== montando o caixa.html"
python3 caixa/gera_dash.py
if git diff --quiet -- caixa.html; then
  echo "== nada mudou no caixa.html, nao ha o que publicar"
else
  git add caixa.html
  git commit -q -m "caixa $(date +%d/%m/%Y)"
  git push -q origin main
  echo "== publicado: $(git log --oneline -1)"
fi
echo "== conferindo a publicacao"
curl -s -o /dev/null -w "   caixa.html responde %{http_code}\n" https://joaoandradesz.github.io/painel-amanatopazio/caixa.html
