# Relatório de caixa · Grupo Amana

Posição de caixa e compromissos dos próximos 15 dias. **Atualizar segunda e sexta.**

## Como atualizar

```
cd ~/painel-amanatopazio
python3 caixa/gera_caixa.py
git commit -am "caixa DD/MM" && git push
```

Leva uns 3 minutos — quase tudo é leitura do Omie. O arquivo publicado é
`caixa.html`, na raiz do repositório. O relatório carimba na capa a data e a
hora em que foi gerado, então dá para ver na hora se está velho.

Para simular outra data de corte: `python3 caixa/gera_caixa.py 23/10/2026`.

## O que o script faz

1. Lê o extrato de cada conta desde a última conciliação fechada e soma o que
   já está **conciliado** — esse é o saldo de hoje.
2. Levanta os títulos **em aberto** com vencimento nos próximos 15 dias, dos
   dois lados.
3. Monta a curva diária, o calendário, a tabela e o relatório inteiro.

## A âncora — atualizar todo fechamento

No topo de `gera_caixa.py` está `ANCORA_DATA` e `ANCORA`: o saldo conciliado
de cada conta na última data fechada, conferido contra o extrato do banco.
**Depois de fechar um mês, atualize os dois.** Sem isso, o saldo de hoje vai
acumulando movimento sobre uma base velha e se afasta do banco.

## Limite conhecido

O relatório mostra **posição e compromissos**, não previsão: só enxerga o que
já está lançado. Medido em outubro/2026: dos R$ 200.386,32 pagos na primeira
quinzena, só R$ 81.943,07 estavam no Omie no dia 30 de setembro — cobertura de
**41%**. A página de alertas publica esse número a cada edição.

Para virar previsão de verdade, os fornecedores recorrentes precisam ser
lançados como previsto antes do dia 25. A lista está em
`Fornecedores_Recorrentes_Amana_Topazio.xlsx`.

## Credenciais

Ficam em `~/.omie_<empresa>.json`, com permissão 600, **fora do repositório**.
Nada de chave neste diretório.
