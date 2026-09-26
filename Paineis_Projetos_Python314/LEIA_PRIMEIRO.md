# Painéis dos projetos — Python 3.14

Complemento visual para os projetos de Benevaldo. Um comando gera um relatório HTML
com cinco telas, abre o navegador e encerra. Não precisa de pip, Docker, servidor
web ou conexão com a internet para visualizar. Use Python 3.14 de 64 bits já instalado.

## 1. Extrair o pacote

No Windows, extraia o ZIP em `C:/Users/Benevaldo/Documents`.
O resultado deve ser:

`C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py`

A pasta deve conter também `interface.html`. Não mova somente o arquivo Python.
Este complemento fica separado dos projetos que você já executou.

## 2. Abrir seus resultados

Cole a linha inteira no terminal Bash ou PowerShell do VS Code:

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py"
```

Esse comando procura os resultados nas pastas que você já usou e abre um único
painel com menu lateral. Você pode executá-lo de qualquer pasta do terminal.
Os dados são lidos do computador; não são enviados para serviços externos.

Os quatro projetos devem ter gerado suas exportações previamente. As execuções
que você já concluiu com `tudo` são suficientes, desde que os arquivos em `outputs`
ainda existam. Clones do GitHub podem não trazer arquivos de saída ignorados pelo Git.

Se o navegador não abrir automaticamente, abra:
`C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/resultados/painel.html`.

## 3. O que aparece em cada tela

| Tela | Dados usados | Visualizações |
|---|---|---|
| Videoaula 13 | `outputs/python` | Faturamento, custo, lucro bruto, ticket, margem, categorias e meses |
| Videoaula 14 | `outputs/metricas_teste.json` e `qualidade.json` | Matriz de confusão, métricas, baseline, limpeza e divisão temporal |
| Videoaula 15 | `outputs/execucoes/*` | Indicadores da última exportação, checkpoint, faturamento diário, status e histórico de exportações |
| Videoaula 16 | `outputs/consulta_*` | Indicadores, categorias e versões que possuem consultas exportadas |
| Olist | CSVs na pasta do notebook e exportações em `outputs` | Filtros por mês e UF, pedidos, atrasos, valores dos produtos, métricas e figuras do notebook |

Todos os gráficos possuem valores ou tabelas de apoio. As tabelas têm busca.
O botão **Imprimir / PDF** imprime a tela selecionada, com os filtros atuais.
A galeria Olist exibe até 20 PNGs de até 8 MB cada em `outputs/figuras`.

## 4. Abrir somente uma tela

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto 1
```

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto 2
```

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto 3
```

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto 4
```

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto olist
```

Esses comandos usam o mesmo arquivo de saída padrão. Gerar um painel novo substitui
somente o HTML anterior. Use `--saida "C:/caminho/relatorio.html"` para guardar uma cópia separada.

## 5. Se uma tela disser “Resultados não encontrados”

Veja as pastas detectadas:

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --diagnostico
```

Uma tela vazia não será preenchida com resultados de demonstração. As outras
continuam disponíveis. A saída de erro do comando indica que pelo menos uma tela
não conseguiu carregar seus dados; leia a mensagem do próprio painel.

Para escolher uma pasta explicitamente, por exemplo:

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto 1 --pasta "C:/Users/Benevaldo/Documents/meus-projetos/Bancos de Dados para Ciencia de Dados/Projeto_Videoaula13"
```

Para o Olist, o caminho visto nas suas capturas é:

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --projeto olist --pasta "C:/Users/Benevaldo/Documents/meus-projetos/Análise de Desempenho de Vendas e Previsão de Atrasos em Entregas no E-commerce Brasileiro"
```

Para salvar os caminhos de todos os projetos, copie `caminhos.exemplo.json` para
`caminhos.json`, na pasta deste complemento, e edite os caminhos. Use barras `/`.
Os caminhos explícitos dessa configuração têm prioridade sobre a descoberta automática.
Se houver duas cópias com resultados, confira a pasta selecionada no terminal e em
**Fontes e rastreabilidade**; configure a cópia desejada para evitar ambiguidade.

### Gerar saídas ausentes

Na pasta original do projeto, execute o comando já usado nas aulas:

- Projetos 1, 2 e 3: `py -3.14 executar.py tudo`.
- Projeto 4 já inicializado e com versão publicada: `py -3.14 executar.py consultar`.
- Projeto 4 ainda não executado: `py -3.14 executar.py instalar`, depois `py -3.14 executar.py tudo`.
- Olist: execute o notebook para gerar métricas e figuras. A visão exploratória pode
  ser gerada diretamente dos CSVs, sem executar o modelo.

Os comandos relativos desta seção exigem que você esteja na pasta original correta.
O painel nunca chama essas operações automaticamente. No Projeto 4, `tudo` cria uma
nova versão; para apenas atualizar a consulta, use `consultar`.

## 6. Demonstração independente

Para experimentar sem depender das pastas originais:

```bash
py -3.14 "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/painel.py" --demonstracao
```

Uma faixa amarela identifica todas as telas como **DEMONSTRAÇÃO**. Os projetos 1 a 4
usam exportações de referência dos exercícios; o Olist usa 18 pedidos artificiais
e uma matriz didática independente de 8 exemplos. Não são resultados atuais do seu computador.
Para voltar aos seus resultados, execute o comando da seção 2 sem `--demonstracao`.

## 7. Atualização e interpretação

1. Execute seu projeto ou notebook para atualizar os arquivos de origem.
2. Execute novamente `painel.py`.
3. Confira a data da fotografia e os detalhes de cada fonte no rodapé da tela.

Apertar F5 no navegador só recarrega o HTML salvo. Não refaz cálculos a partir dos CSVs.

- Financeiro: valores em centavos das videoaulas são convertidos para reais uma única vez.
- Pipeline: não somamos fotografias de execuções diferentes; escolhemos a última
  exportação pela data de modificação do arquivo. Copiar arquivos pode alterar essa data.
- Governança: mostra a versão da consulta mais recente, que pode ser diferente da
  versão ativa atual. Não afirma que a assinatura ou auditoria foi novamente validada.
  Para isso, execute `py -3.14 executar.py verificar` no projeto original.
- Olist: a visão exploratória inclui somente entregues, com datas de compra, entrega
  e previsão válidas e cronologicamente coerentes. Atraso compara timestamps completos,
  como no notebook de referência; entrega posterior à meia-noite da data prevista
  também conta como atraso. Métricas exportadas do modelo usam sua população original.
- Olist: itens são agregados por pedido para evitar multiplicar a contagem ao juntar tabelas.
  O valor dos produtos exclui frete; não é total pago, receita contábil reconhecida ou lucro.
- Olist: filtros por mês/UF afetam a visão exploratória, não as métricas do modelo já treinado.
- CSVs não encontrados deixam os indicadores correspondentes indisponíveis. Preços inválidos
  são excluídos com aviso; preços parciais não devem ser interpretados como um total completo.

## 8. Arquivos e privacidade

`painel.py` lê os formatos conhecidos e monta os dados. `interface.html` contém a tela,
gráficos e filtros. `resultados/painel.html` é autossuficiente: contém os valores e imagens
usados e abre offline. Não depende de bibliotecas carregadas de serviços externos.

O relatório pode conter indicadores e caminhos locais nas fontes. Revise-o antes de
compartilhar. Não inclui IDs Olist, pseudônimos de clientes, chaves ou tokens do Projeto 4.
O complemento não lê modelos `.joblib`, não executa notebooks e não abre servidores.

`caminhos.json`, `resultados/` e arquivos temporários estão no `.gitignore` deste complemento.
Os gráficos e valores do HTML são informativos; não substituem testes dos projetos.

## 9. Verificar o complemento

```bash
py -3.14 -m unittest discover -s "C:/Users/Benevaldo/Documents/Paineis_Projetos_Python314/tests" -v
```

A validação executada na entrega está em `VALIDACAO.md`.

## Referências técnicas

- Python 3.14, abertura do navegador: https://docs.python.org/3.14/library/webbrowser.html
- Python 3.14, leitura CSV: https://docs.python.org/3.14/library/csv.html
- Formatos das videoaulas: pacote `Quatro_Projetos_Python314_Terminal.zip`.
- Formatos Olist: notebook `Analise_Olist_Atrasos_CORRIGIDO_JupyterLab.ipynb` consultado.
