# Versão de demonstração

Cópias do dashboard de caixa e do painel mensal com **os mesmos números** e
**nomes fictícios**, para apresentar em reunião sem expor o cliente.

- `demo/caixa.html` — dashboard de caixa e compromissos
- `demo/painel.html` — painel mensal (DRE e fluxo de caixa)

O que é trocado: razão social das empresas, nomes de hóspedes, prestadores e
fornecedores, CNPJ e CPF. Mantém-se o que não identifica ninguém — bancos,
adquirentes, OTAs, tributos — porque é o que dá verossimilhança à demonstração.

A substituição é **determinística**: o mesmo nome real vira sempre o mesmo
nome fictício, então as séries continuam coerentes de um mês para o outro.

Nas duas páginas há uma faixa fixa no rodapé dizendo que é demonstração.

## Como regerar, depois de atualizar os originais

```
python3 caixa/anonimiza.py
git commit -am "demo" && git push
```
