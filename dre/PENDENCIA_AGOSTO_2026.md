# Agosto/2026 — R$ 15.630,20 segurados até o fechamento de dezembro

**Decisão do João em 27/10/2026.** Agosto já foi entregue duas vezes (rev. 2 em
07/10 e rev. 3 em 26/10). Uma terceira retificação no mesmo mês custa mais
credibilidade do que corrige. O valor fica **registrado e não publicado** até o
relatório de dezembro fechado, quando o acumulado do ano absorve a diferença e a
pendência morre.

## O que está diferente, e onde

| | Painel (publicado) | Omie e contabilidade |
|---|---|---|
| Receita de Hospedagem · Amana · ago/26 | 734.874,60 | 750.504,84 |
| Receita bruta consolidada · ago/26 | 760.600,59 | 777.756,50 |
| EBITDA consolidado · ago/26 | 165.553,19 | 182.709,10 |
| Resultado · ago/26 | 138.376,99 | 155.532,90 |
| EBITDA acumulado jan–set | 505.153,38 | 522.309,29 |

**O painel está R$ 15.630,20 abaixo do Omie em agosto, de propósito.**

## Por que são 15.630,20

| | |
|---|---|
| NFS-e 129 · Matheus Rocca · título 5290043958 | +17.155,91 |
| Hospedagem sem NFS-e · Aline Affonso, reserva 2082 · título 5299412371 | −1.525,67 |
| Arredondamento da contabilidade nas mesmas 74 notas | +0,04 |
| **Total** | **+15.630,20** |

## O que JÁ está feito no Omie (e fica como está)

O Omie guarda o fato, não a versão publicada. Os dois lançamentos foram
corrigidos em 27/10 e **não devem ser desfeitos**:

- título **5290043958** (NFS-e 129): `data_emissao` passou de 10/07/2026 para
  **31/08/2026**, a data da nota — igual às vizinhas 127, 130, 131 e 132. A data
  antiga era a da venda no cartão.
- categoria **1.01.94 Hospedagem sem NFS-e** criada (superior 1.01, DRE 1.01.01),
  e o título **5299412371** movido de 1.01.02 para ela.

## O que fazer no fechamento de dezembro

1. `python3 dre/retifica_ago_nfse129.py` — o script existe, tem as travas de
   pré-condição e aplica exatamente estes R$ 15.630,20 no painel (mês 8 e os
   acumulados T e TT). Rodar com `GRAVA=1`.
2. Rodar os três gates nos dois arquivos.
3. No relatório de dezembro, declarar o ajuste no acumulado do ano: agosto sai de
   760.600,59 / 165.553,19 / 138.376,99 para 777.756,50 / 182.709,10 / 155.532,90.
4. Apagar este arquivo.

## Risco a vigiar

Qualquer `MES=8 publica_set.py` repuxa agosto do Omie e traz os R$ 15.630,20 de
volta **sem avisar**. Antes de republicar agosto por qualquer motivo, ler isto.
