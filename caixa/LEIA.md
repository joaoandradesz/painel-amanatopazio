# Dashboard de caixa · Amana · Topázio · Consolidado

Publicado em **joaoandradesz.github.io/painel-amanatopazio/caixa.html**.
Posição de caixa e compromissos dos próximos 15 dias, com clique até o título.

## Atualizar (segunda e sexta)

```
cd ~/painel-amanatopazio
python3 caixa/coleta_dash.py     # lê o Omie das duas empresas (~3 min)
python3 caixa/gera_dash.py       # monta o caixa.html
git commit -am "caixa $(date +%d/%m)" && git push
```

O dashboard carimba no topo a data e a hora da geração, então dá para ver na
hora se está velho.

## O que dá para fazer na tela

- **Amana · Topázio · Consolidado** nas abas do topo
- **Clicar em qualquer dia** — no gráfico, no calendário ou na tabela — abre os
  recebimentos e pagamentos daquele dia, com cliente/fornecedor, categoria,
  empresa e valor
- **Filtrar** as listas de a receber e a pagar por nome, categoria ou data
- **Ocultar os títulos intercompany** Amana ↔ Topázio no consolidado
- **Exportar PDF** pelo botão, no layout de impressão

## A âncora — atualizar todo fechamento

`ANCORA_DATA` e `ANCORA`, no topo de `coleta_dash.py`: o saldo conciliado de
cada conta na última data fechada, conferido contra o extrato. **Depois de
fechar um mês, atualize os dois.** Sem isso o saldo de hoje acumula movimento
sobre base velha e se afasta do banco.

## Limites que o próprio painel declara

- Mostra **posição e compromissos**, não previsão: só enxerga o que já está
  lançado. Cobertura medida em outubro/2026: **41%**.
- Quando o saldo apurado de uma empresa fica negativo, o painel abre um alerta
  vermelho em vez de mostrar o número como se fosse verdade — foi o caso da
  Topázio em outubro, sem o recebimento intercompany lançado.

## Credenciais

`~/.omie_<empresa>.json`, permissão 600, fora do repositório.
