# Conferência

Três travas, todas no `pre-commit`: **commit não passa se alguma falhar.**

| arquivo | o que testa |
|---|---|
| `auditoria_estrita.py` | cada linha clicável, uma a uma, contra o valor que o clique abre |
| `varredura.py` | invariantes de estrutura: acumulado = soma dos meses, grupo = soma das categorias, saldo inicial + resultado = acumulado, contas = saldo, número clicável que abre lista vazia |
| `kpi_x_arvore.js` | KPIs e gráficos (`D.resumo`) contra a árvore da DRE, usando o `dbucket` **da própria página** |

Rodar à mão:

    python3 conferencia/auditoria_estrita.py index.html
    python3 conferencia/varredura.py index.html
    node    conferencia/kpi_x_arvore.js index.html

## As regras que o painel tem que manter

1. **Uma categoria, uma linha.** O clique abre a lista *da categoria*, não a da
   linha. Categoria em duas posições da árvore = linha mostrando um pedaço e
   clique abrindo o todo. Foi o bug que o Tiago achou em 14/10/2026
   (Prestadores Diversos: linha R$ 10.550, clique R$ 18.813,32).
2. **Receita e despesa com o mesmo nome nunca se juntam.** "Hospedagem" vendida
   e hospedagem paga são coisas diferentes; a de despesa leva sufixo e vira
   categoria própria. Juntar as duas mexeria na receita.
3. **Acumulado = soma dos meses**, árvore e lista. As listas de Ano/Tudo são a
   concatenação dos meses em que a categoria tem linha — há itens em `tx` de
   categorias que a DRE oficial não mostra (intercompany, contas de controle) e
   eles não entram no ano.
4. **Todo total é a soma do que está embaixo dele.**

## Diferença conhecida e declarada

Nos meses de **2025** (base de comparação), `saldo inicial + resultado` não
fecha com o `acumulado`: o acumulado veio do extrato e o resultado, dos
lançamentos classificados. Está medido em `varredura.py` (lista `GAP25`) —
entre R$ 0,10 e R$ 3.157,98 por mês. Em 2026 fecha ao centavo.
