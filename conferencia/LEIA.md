# Conferência

`auditoria_estrita.py` testa **cada linha clicável, uma a uma**, contra o valor
que o clique abre — nas três entidades, em todos os meses, nas visões Ano e
Tudo, nos dois regimes (DRE e caixa).

Roda sozinha no `pre-commit`: **commit não passa com divergência**.

Para rodar à mão:

    python3 conferencia/auditoria_estrita.py index.html

## O ponto cego que isto fecha

A auditoria anterior somava a categoria na árvore inteira antes de comparar.
Por isso não via dois casos, que foram exatamente os que o Tiago achou:

1. **Categoria em mais de uma posição da árvore.** Cada linha mostrava um
   pedaço e o clique abria o todo (Prestadores Diversos: linha R$ 10.550,
   clique R$ 18.813,32). O clique abre a lista **da categoria**, não a lista
   daquela linha — então uma categoria tem que ter uma linha só.
2. **Ano / Tudo com a lista desatualizada.** A linha somava os meses, a lista
   não tinha agosto.

A regra que o painel precisa manter: **uma categoria, uma linha**, e lista
acumulada = concatenação dos meses em que a categoria tem linha.
