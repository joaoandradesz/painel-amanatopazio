# Dashboard de caixa · Amana · Topázio · Consolidado

Publicado em **joaoandradesz.github.io/painel-amanatopazio/caixa.html**.
Posição de caixa e compromissos, com **seletor de período** e clique até o título.

## Atualizar (segunda e sexta)

```
cd ~/painel-amanatopazio
python3 caixa/coleta_dash.py     # lê o Omie das duas empresas, 90 dias de títulos (~3 min)
python3 caixa/gera_dash.py       # monta o caixa.html
git commit -am "caixa $(date +%d/%m)" && git push
```

O dashboard carimba no topo a data e a hora da geração, então dá para ver na
hora se está velho.

## O que dá para fazer na tela

- **Escolher o período**: atalhos de 15, 30 e 60 dias, até o fim do mês e mês que vem, ou as datas de e até na mão. O horizonte carregado é de **90 dias** — o seletor trabalha dentro dele
- **Amana · Topázio · Consolidado** nas abas do topo
- **Clicar em qualquer dia** — no gráfico, no calendário ou na tabela — abre os
  recebimentos e pagamentos daquele dia, com cliente/fornecedor, categoria,
  empresa e valor
- **Filtrar** as listas de a receber e a pagar por nome, categoria ou data
- **Ocultar os títulos intercompany** Amana ↔ Topázio no consolidado
- **Exportar PDF** pelo botão, no layout de impressão

## Previsto × realizado

A cada rodada o `coleta_dash.py` guarda um retrato em `caixa/historico/AAAA-MM-DD.json`
— saldo e a lista de títulos em aberto dos 15 dias seguintes, com código. Na
rodada seguinte ele compara e classifica cada título daquele retrato:

| balde | o que é |
|---|---|
| **confirmou** | foi pago ou recebido |
| **escorregou** | venceu e continua em aberto |
| **surpresa** | foi liquidado sem estar no retrato — entrou depois |

Dois indicadores saem disso, e eles **não** medem a mesma coisa:

- **Acerto da previsão** — do que estava previsto e já venceu, quanto aconteceu.
  Mede se o que está lançado é confiável.
- **Cobertura** — de tudo que aconteceu, quanto já estava lançado no retrato
  anterior. Mede se o sistema enxerga o mês antes de ele acontecer.

Para semear o histórico com uma data passada:

    python3 caixa/semeia_historico.py 30/09/2026 '{"amana":649598.21,"topazio":12683.18}'

Os retratos ficam no repositório — não apague, é a série histórica.

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
