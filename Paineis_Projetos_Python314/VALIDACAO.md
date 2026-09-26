# Validação do complemento visual

Data: 25/09/2026.

## Ambiente efetivamente utilizado

- CPython 3.14.7, Linux x86_64.
- O complemento usa somente biblioteca padrão do Python.
- JavaScript executado com Node.js 24 em uma simulação de DOM para testar montagem
  de telas, filtros e busca; sem dependências externas na página entregue.

## Resultado

16 testes Python aprovados. Evidência: `evidencias/testes_python314.txt`.

Cobertura relevante:

- Conversão de centavos para reais e totais dos projetos 1, 3 e 4.
- Matriz de confusão e métricas do projeto 2.
- Exportações repetidas não somam faturamento duplicado.
- Visão Olist agrega itens antes de contar pedidos.
- Remoção de duplicatas idênticas; rejeição de pedidos duplicados conflitantes.
- Ausência de preços não é apresentada como receita conhecida de zero.
- Arquivos ausentes/malformados exibem aviso, sem inventar indicadores.
- Leitura não modifica arquivos de origem.
- Conteúdo semelhante a HTML em categorias não cria scripts na página.
- Caminhos com espaços e acentos.
- Modelos serializados não são carregados; tokens não aparecem no resultado.

Na simulação de DOM, todas as cinco telas foram montadas sem exceção; o filtro
Olist fevereiro/2026 + SP resultou em 2 pedidos, 100% atrasados e R$ 210,00,
conforme a amostra artificial incluída. Busca e estado de dados ausentes também
foram exercitados. Evidência: `evidencias/testes_interface.json`.

## Fontes utilizadas nos testes

Projetos 1–4: exportações de referência do pacote de projetos Python 3.14.
Olist: esquema e nomes de saídas do notebook
`Analise_Olist_Atrasos_CORRIGIDO_JupyterLab.ipynb`; testes com CSVs artificiais.
Os CSVs completos que estão no computador do usuário não foram acessados.

## Limites da validação

- Não foi executado no Windows do usuário. O comando `py -3.14` depende do launcher
  Windows que ele já utilizou com sucesso nesta conversa.
- Não foi concluída uma inspeção visual em navegador real: o ambiente não tinha
  navegador instalado e a tentativa de download não retornou o executável.
  A verificação de JavaScript em DOM simulado não substitui testes de layout em Chrome/Edge.
- A abertura automática do navegador depende da associação de arquivos do sistema;
  há instrução para abrir o HTML manualmente se necessário.
- Os testes não são uma auditoria de segurança completa, nem validam as métricas
  de negócio de uma base que não foi disponibilizada.

Este pacote acrescenta visualização; não modifica os projetos originais.
