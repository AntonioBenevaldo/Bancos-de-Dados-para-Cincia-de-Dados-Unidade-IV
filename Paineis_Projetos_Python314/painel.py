"""Painéis locais dos projetos de Benevaldo. Apenas biblioteca padrão, Python 3.14.

Lê exportações e gera um HTML independente; não executa notebooks/pipelines,
não carrega modelos serializados e não lê credenciais nem bancos de segurança.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent
NAMES = {'1': 'Projeto_Videoaula13', '2': 'Projeto02_Videoaula14',
         '3': 'Projeto03_Videoaula15', '4': 'Projeto04_Videoaula16'}
TITLES = {'1': 'Extração e análise', '2': 'Machine learning',
          '3': 'Automação de consultas', '4': 'Governança e versões',
          'olist': 'Vendas e entregas • Olist'}
SUBTITLES = {'1': 'Videoaula 13 · pandas e SQLAlchemy',
             '2': 'Videoaula 14 · Ingestão e pré-processamento',
             '3': 'Videoaula 15 · Pipelines de dados',
             '4': 'Videoaula 16 · Segurança e versionamento',
             'olist': 'Análise de desempenho e previsão de atrasos'}


def read_json(p):
    def bad(x):
        raise ValueError(f'Valor JSON não finito: {x}')
    return json.loads(p.read_text(encoding='utf-8-sig'), parse_constant=bad)


def read_csv(p, required=()):
    with p.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{p.name}: faltam colunas {", ".join(sorted(missing))}')
        yield from reader


def number(x):
    v = float(x)
    if not math.isfinite(v):
        raise ValueError('Número inválido nos resultados.')
    return v


def page(key, folder):
    return dict(id=key, title=TITLES[key], subtitle=SUBTITLES[key], folder=str(folder),
                status='ok', cards=[], charts=[], tables=[], notes=[], sources=[], images=[])


def source(p, file):
    """Data e hash permitem reconhecer a fotografia efetivamente lida."""
    if file.is_file():
        p['sources'].append(dict(arquivo=str(file),
            modificado=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(),
            sha256=hashlib.sha256(file.read_bytes()).hexdigest()))


def card(p, label, value, fmt='integer', detail=''):
    p['cards'].append(dict(label=label, value=value, format=fmt, detail=detail))


def chart(p, title, labels, values, fmt='number', note='', kind='bar'):
    p['charts'].append(dict(title=title, labels=labels, values=[number(v) for v in values],
                            format=fmt, note=note, kind=kind))


def table(p, title, rows, columns=None):
    if columns is None:
        columns = list(rows[0]) if rows else []
    p['tables'].append(dict(title=title, columns=columns,
                           rows=[[r.get(c, '') for c in columns] for r in rows]))


def finance(p, d, count='pedidos_concluidos'):
    card(p, 'Pedidos concluídos', int(d[count]))
    card(p, 'Faturamento', number(d['faturamento_centavos']) / 100, 'currency')
    card(p, 'Custo dos produtos', number(d['custo_total_centavos']) / 100, 'currency')
    card(p, 'Lucro bruto', number(d['lucro_bruto_centavos']) / 100, 'currency')
    p['notes'].append('Dados simulados. Lucro bruto = faturamento − custo dos produtos; não desconta tributos e outras despesas.')


def aggregate(rows, group, field):
    result = defaultdict(float)
    for row in rows:
        result[row[group]] += number(row[field])
    return sorted(result.items())


def p1(folder):
    p = page('1', folder); out = folder / 'outputs/python'
    path = out / 'indicadores.json'; d = read_json(path); source(p, path)
    finance(p, d, 'vendas'); card(p, 'Unidades vendidas', int(d['unidades']))
    card(p, 'Ticket médio', number(d['ticket_medio_reais']), 'currency')
    card(p, 'Margem bruta', number(d['margem_bruta_percentual']), 'percent')
    for file, col, title in [('resumo_categoria.csv','categoria','Faturamento por categoria'),
                              ('resumo_mensal.csv','mes','Faturamento por mês')]:
        path = out / file; rows = list(read_csv(path, [col, 'faturamento_centavos']))
        source(p, path)
        chart(p, title, [r[col] for r in rows], [number(r['faturamento_centavos'])/100 for r in rows], 'currency')
        display = [{col:r[col], 'Faturamento (R$)':number(r['faturamento_centavos'])/100,
                    'Custo (R$)':number(r['custo_total_centavos'])/100,
                    'Lucro bruto (R$)':number(r['lucro_bruto_centavos'])/100} for r in rows]
        table(p, title + ' • valores', display)
    p['notes'].append('O painel apresenta a exportação Python. Não executa nem valida a parte em R ou PostgreSQL.')
    return p


def p2(folder):
    p = page('2', folder); out = folder / 'outputs'
    fp = out/'metricas_teste.json'; d = read_json(fp); source(p, fp)
    model = d['regressao_logistica']; base = d['baseline_prior']
    for label, key in [('Acurácia','acuracia'),('Precisão','precisao'),('Recall','recall'),('F1','f1')]:
        card(p, label, number(model[key])*100, 'percent')
    card(p, 'ROC-AUC', model.get('roc_auc'), 'decimal')
    card(p, 'Pedidos no teste', int(model['linhas']))
    card(p, 'Limiar registrado', number(d['limiar_fixo']), 'decimal')
    p['matrix'] = model['matriz_confusao']
    keys = ['acuracia','acuracia_balanceada','precisao','recall','f1','roc_auc']
    table(p, 'Modelo e baseline • escala de 0 a 1',
          [{'Métrica':k, 'Regressão logística':model.get(k), 'Baseline':base.get(k)} for k in keys])
    chart(p, 'Qualidade da classificação', ['Acurácia','Precisão','Recall','F1'],
          [number(model[k])*100 for k in ['acuracia','precisao','recall','f1']], 'percent')
    fp = out/'qualidade.json'
    if fp.exists():
        q = read_json(fp); source(p, fp)
        chart(p, 'Qualidade dos registros de entrada', ['Válidos','Duplicatas removidas','Rejeitados'],
              [q['linhas_validas'],q['duplicatas_exatas_removidas'],q['registros_rejeitados']], 'integer')
        div = q.get('divisao', {})
        parts = div.get('particoes', {})
        if parts:
            chart(p, 'Divisão temporal', list(parts)+['Embargo'],
                  [v['linhas'] for v in parts.values()]+[div.get('linhas_embargo',0)], 'integer',
                  'Embargo: registros separados para evitar usar rótulos futuros no treinamento.')
    p['notes'] += ['Classe positiva: atraso. A matriz usa classe real nas linhas e classe prevista nas colunas.',
                  'Resultados de dados simulados. Os filtros visuais não treinam o modelo nem alteram o limiar.']
    return p


def latest(files):
    files = list(files)
    if not files:
        raise FileNotFoundError('Nenhuma exportação encontrada em outputs. Execute o projeto primeiro.')
    return max(files, key=lambda f: (f.stat().st_mtime_ns, str(f)))


def p3(folder):
    p = page('3', folder)
    files = list((folder/'outputs/execucoes').glob('*/indicadores.json'))
    fp = latest(files); d = read_json(fp); source(p, fp); finance(p, d)
    card(p, 'Pedidos no destino', int(d['pedidos_no_destino']))
    card(p, 'Checkpoint da exportação', int(d['ultimo_evento']))
    rows = list(read_csv(fp.parent/'resumo_diario.csv', ['data_venda','faturamento_centavos']))
    source(p, fp.parent/'resumo_diario.csv')
    groups = aggregate(rows, 'data_venda', 'faturamento_centavos')
    chart(p, 'Faturamento diário', [k for k,v in groups], [v/100 for k,v in groups], 'currency')
    facts = list(read_csv(fp.parent/'pedidos_analiticos.csv', ['status']))
    source(p, fp.parent/'pedidos_analiticos.csv')
    statuses = Counter(r['status'] for r in facts)
    chart(p, 'Situação dos pedidos no destino', list(statuses), list(statuses.values()), 'integer')
    history = []
    for file in sorted(files, key=lambda f:f.stat().st_mtime_ns, reverse=True)[:30]:
        v = read_json(file)
        history.append({'Exportação':file.parent.name, 'Checkpoint':v['ultimo_evento'],
                        'Concluídos':v['pedidos_concluidos'], 'Faturamento (R$)':number(v['faturamento_centavos'])/100})
    table(p, 'Até 30 exportações mais recentes', history)
    p['notes'].append('Fotografia da exportação mais recente por data de modificação. Não é monitoramento ao vivo; uma exportação pode incluir mais de uma execução confirmada. Os valores não são somados entre exportações.')
    return p


def p4(folder):
    p = page('4', folder)
    files = list((folder/'outputs').glob('consulta_*/indicadores.json'))
    fp = latest(files); d = read_json(fp); source(p, fp); finance(p, d)
    version = fp.parent.name.split('_')[1]
    card(p, 'Versão da consulta', version, 'text')
    rows = list(read_csv(fp.parent/'dados_publicados.csv', ['categoria','faturamento_centavos']))
    source(p, fp.parent/'dados_publicados.csv')
    groups = aggregate(rows, 'categoria', 'faturamento_centavos')
    chart(p, 'Faturamento publicado por categoria', [k for k,v in groups], [v/100 for k,v in groups], 'currency')
    versions = {}
    for file in sorted(files, key=lambda f:f.stat().st_mtime_ns):
        v = read_json(file); name = file.parent.name.split('_')[1]
        versions[name] = {'Versão consultada':name,'Pedidos':v['pedidos_concluidos'],
                          'Faturamento (R$)':number(v['faturamento_centavos'])/100,
                          'Lucro bruto (R$)':number(v['lucro_bruto_centavos'])/100}
    table(p, 'Versões com consultas exportadas', list(versions.values()))
    p['notes'] += ['Este painel lê somente consultas já exportadas. Não identifica a versão ativa atual nem repete a verificação criptográfica.',
                  'Para verificar a integridade atual, use executar.py verificar no projeto original. Para atualizar a exportação, use executar.py consultar e gere este painel novamente.',
                  'Identificadores de clientes, pseudônimos, chaves e tokens não são incluídos nesta página.']
    return p


def money_cents(raw):
    d = Decimal(raw)
    if not d.is_finite() or d < 0:
        raise ValueError('Preço inválido.')
    return int((d * 100).quantize(Decimal('1')))


def date(raw):
    if not raw or not raw.strip():
        return None
    if len(raw.strip()) < 10:
        return None
    try:
        return datetime.fromisoformat(raw.strip())
    except ValueError:
        return None


def olist_raw(folder, p):
    """Agrega antes de exibir: nenhum ID de cliente/pedido vai para o HTML."""
    orders_file = folder/'olist_orders_dataset.csv'
    if not orders_file.exists():
        return
    orders = {}; dup = 0; missing_id = 0
    required = ['order_id','customer_id','order_status','order_purchase_timestamp',
                'order_delivered_customer_date','order_estimated_delivery_date']
    for r in read_csv(orders_file, required):
        oid = r['order_id']
        if not oid:
            missing_id += 1; continue
        if oid in orders:
            if orders[oid] != r:
                raise ValueError('Pedidos Olist com mesmo ID e conteúdo diferente. Corrija a origem antes de visualizar.')
            dup += 1; continue
        orders[oid] = r
    source(p, orders_file)
    customers = {}; customer_file = folder/'olist_customers_dataset.csv'
    if customer_file.exists():
        for r in read_csv(customer_file, ['customer_id','customer_state']):
            if r['customer_id'] in customers and customers[r['customer_id']] != r['customer_state']:
                raise ValueError('Cliente Olist com estados conflitantes.')
            customers[r['customer_id']] = r['customer_state']
        source(p, customer_file)
    prices = defaultdict(int); priced_orders = set(); items_seen = {}; invalid_prices = 0
    items_file = folder/'olist_order_items_dataset.csv'
    if items_file.exists():
        for r in read_csv(items_file, ['order_id','order_item_id','price']):
            key = (r['order_id'],r['order_item_id'])
            if key in items_seen:
                if items_seen[key] != r['price']:
                    raise ValueError('Item Olist duplicado com preços conflitantes.')
                continue
            items_seen[key] = r['price']
            try:
                cents = money_cents(r['price'])
            except (InvalidOperation, ValueError):
                invalid_prices += 1; continue
            prices[r['order_id']] += cents; priced_orders.add(r['order_id'])
        source(p, items_file)
    agg = {}; excluded = Counter(); included = set()
    for oid, r in orders.items():
        if r['order_status'] != 'delivered':
            excluded['Não entregues'] += 1; continue
        buy = date(r['order_purchase_timestamp']); actual = date(r['order_delivered_customer_date']); estimated = date(r['order_estimated_delivery_date'])
        if not all([buy, actual, estimated]):
            excluded['Datas ausentes ou inválidas'] += 1; continue
        if any(d.tzinfo is not None for d in [buy, actual, estimated]):
            excluded['Datas com fuso não esperado'] += 1; continue
        if actual < buy or estimated < buy:
            excluded['Datas anteriores à compra'] += 1; continue
        key = (buy.strftime('%Y-%m'), customers.get(r['customer_id']) or 'Não informado')
        a = agg.setdefault(key, dict(month=key[0],state=key[1],orders=0,late=0,revenue=0,days=0,priced=0))
        a['orders'] += 1; a['late'] += int(actual > estimated)
        a['revenue'] += prices[oid]; a['days'] += (actual-buy).total_seconds()/86400
        a['priced'] += int(oid in priced_orders); included.add(oid)
    p['olist_groups'] = list(agg.values())
    p['olist_has_prices'] = items_file.exists()
    p['notes'].append('Visão exploratória: pedidos com status delivered e datas válidas. Atraso = instante de entrega posterior ao instante estimado, seguindo a comparação do notebook. Filtros usam mês da compra e UF do cliente.')
    p['notes'].append('Valor dos produtos = soma dos preços dos itens dos pedidos incluídos, sem frete. Não representa lucro nem valor total pago. As tabelas de itens são agregadas por pedido antes dos indicadores.')
    if not items_file.exists():
        p['notes'].append('CSV de itens ausente: os valores monetários ficam indisponíveis.')
    if invalid_prices:
        p['notes'].append(f'{invalid_prices} preços inválidos foram excluídos da soma; valor dos produtos é parcial.')
    table(p, 'Conferência da leitura dos CSVs', [{'Verificação':k,'Quantidade':v} for k,v in {
        'Pedidos distintos na origem':len(orders), 'Pedidos entregues incluídos':len(included),
        'Linhas duplicadas idênticas removidas':dup, 'Linhas sem ID excluídas':missing_id,
        'Pedidos incluídos sem itens com preço válido':len(included-priced_orders), **excluded}.items()])


def olist(folder):
    p = page('olist', folder); out = folder/'outputs'
    olist_raw(folder, p)
    for name, title in [('metricas_modelo_final.csv','Métricas exportadas pelo notebook'),
                         ('comparacao_modelos.csv','Comparação de modelos exportada'),
                         ('indicadores_relatorio.csv','Indicadores exportados pelo notebook')]:
        fp = out/name
        if fp.exists():
            rows = list(read_csv(fp)); source(p, fp); table(p, title, rows)
            if name == 'metricas_modelo_final.csv':
                vals = []
                for r in rows:
                    if r.get('Métrica') in ['Precision','Recall','F1','F2','ROC-AUC','PR-AUC']:
                        try: vals.append((r['Métrica'],number(r['Valor'])))
                        except (ValueError, KeyError): continue
                if vals:
                    chart(p, 'Avaliação do modelo • escala de 0 a 1', [k for k,v in vals], [v for k,v in vals], 'decimal',
                          'Valores lidos da exportação. Os filtros da visão exploratória não recalculam estas métricas.')
    # Galeria só de PNGs gerados: não interpretar HTML ou executar notebooks.
    for fp in sorted((out/'figuras').glob('*.png'))[:20]:
        if fp.stat().st_size > 8_000_000:
            p['notes'].append(f'Imagem {fp.name} acima de 8 MB: não incorporada.'); continue
        raw = fp.read_bytes()
        if not raw.startswith(b'\x89PNG\r\n\x1a\n'): continue
        p['images'].append(dict(title=fp.stem.replace('_',' '), data='data:image/png;base64,'+base64.b64encode(raw).decode()))
        source(p, fp)
    if 'olist_groups' in p and not p['olist_groups']:
        p['notes'].append('Nenhum pedido elegível para a visão exploratória.')
    if not p['sources']:
        raise FileNotFoundError('Não encontrei CSVs Olist na pasta nem exportações reconhecidas em outputs. Informe a pasta que contém o notebook e os CSVs.')
    p['notes'].append('O painel não executa o notebook nem refaz o treinamento. Métricas e imagens exportadas podem corresponder a uma execução anterior; confira as datas das fontes. A população da visão exploratória pode diferir da população usada no teste do modelo.')
    return p


ADAPTERS = {'1':p1,'2':p2,'3':p3,'4':p4,'olist':olist}


def has_output(key, folder):
    if key=='1':return (folder/'outputs/python/indicadores.json').is_file()
    if key=='2':return (folder/'outputs/metricas_teste.json').is_file()
    if key=='3':return any((folder/'outputs/execucoes').glob('*/indicadores.json'))
    if key=='4':return any((folder/'outputs').glob('consulta_*/indicadores.json'))
    return (folder/'olist_orders_dataset.csv').is_file() or (folder/'outputs/metricas_modelo_final.csv').is_file()


def discover():
    home = Path.home(); docs = home/'Documents'
    bases = [Path.cwd(),ROOT.parent,docs/'meus-projetos/Bancos de Dados para Ciencia de Dados',
             docs/'Bancos-Dados-Publicacao',docs/'meus-projetos/bancos-de-dados-para-ciencia-de-dados']
    result = {}
    for key, name in NAMES.items():
        candidates = [b/name for b in bases]+[b for b in bases if b.name==name]
        result[key] = next((p for p in candidates if has_output(key,p)),
                            next((p for p in candidates if p.is_dir()),bases[2]/name))
    title='Análise de Desempenho de Vendas e Previsão de Atrasos em Entregas no E-commerce Brasileiro'
    candidates=[Path.cwd(), ROOT.parent, docs/'meus-projetos'/title,
                docs/'meus-projetos/Trabalho-Programming-for-Data-Science-Python-R',
                docs/'Trabalho-Programming-for-Data-Science-Python-R']
    result['olist']=next((p for p in candidates if has_output('olist',p)), docs/'meus-projetos'/title)
    return result


def build(paths, keys):
    pages=[]
    for key in keys:
        folder=paths[key].expanduser().resolve()
        try:
            p=ADAPTERS[key](folder)
        except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
            p=page(key,folder); p['status']='missing' if isinstance(exc,FileNotFoundError) else 'error'
            p['notes'].append(str(exc))
            p['notes'].append('Confira a pasta indicada. Para as videoaulas, gere os resultados no projeto original; no Projeto 4, use consultar se já houver versão publicada.')
        pages.append(p)
    return dict(generated=datetime.now(timezone.utc).isoformat(), pages=pages)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Gera painéis HTML locais dos quatro projetos e do Olist. Python 3.14, sem pip.')
    parser.add_argument('--projeto',choices=['todos','1','2','3','4','olist'],default='todos')
    parser.add_argument('--pasta',type=Path,help='Pasta de um projeto; use com --projeto 1, 2, 3, 4 ou olist.')
    parser.add_argument('--config',type=Path,help='JSON com caminhos nas chaves 1, 2, 3, 4 e olist.')
    parser.add_argument('--sem-abrir',action='store_true',help='Gera o HTML sem abrir o navegador.')
    parser.add_argument('--demonstracao',action='store_true',help='Abre amostras incluídas, identificadas como demonstração.')
    parser.add_argument('--diagnostico',action='store_true',help='Mostra caminhos encontrados, sem gerar relatório.')
    parser.add_argument('--saida',type=Path,default=ROOT/'resultados/painel.html')
    args=parser.parse_args(argv)
    if args.pasta and args.projeto=='todos':parser.error('--pasta exige um único --projeto.')
    paths=discover()
    config=args.config or ROOT/'caminhos.json'
    if config.is_file():
        try:
            data=read_json(config)
            for k,v in data.items():
                if k in paths and v:
                    p=Path(v).expanduser(); paths[k]=p if p.is_absolute() else config.resolve().parent/p
        except (ValueError,OSError,AttributeError,TypeError) as exc:
            parser.error(f'Configuração inválida: {exc}')
    if args.demonstracao:
        if args.pasta or args.config:parser.error('--demonstracao não pode ser combinado com --pasta ou --config.')
        paths={k:ROOT/'demonstracao'/k for k in ADAPTERS}
    if args.pasta:paths[args.projeto]=args.pasta
    keys=list(ADAPTERS) if args.projeto=='todos' else [args.projeto]
    if args.diagnostico:
        for k in keys:print(f'{k} | {"Resultados encontrados" if has_output(k,paths[k]) else "Verificar pasta/resultados"} | {paths[k]}')
        return 0
    payload=build(paths,keys)
    payload['demo']=args.demonstracao
    # Evita que um nome de categoria feche o elemento script no HTML.
    embedded=json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    template=(ROOT/'interface.html').read_text(encoding='utf-8')
    output=args.saida.expanduser().resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(template.replace('__PAYLOAD__',embedded),encoding='utf-8')
    for p in payload['pages']:print(f'{p["id"]} | {p["status"]} | {p["folder"]}')
    print(f'\nPainel gerado: {output}\nExecute o comando novamente após atualizar os resultados.')
    if not args.sem_abrir:
        try:
            if not webbrowser.open(output.as_uri()):print('Abra o arquivo painel.html manualmente no navegador.')
        except webbrowser.Error:print('Abra o arquivo painel.html manualmente no navegador.')
    return 0 if all(p['status']=='ok' for p in payload['pages']) else 1


if __name__=='__main__':
    raise SystemExit(main())
