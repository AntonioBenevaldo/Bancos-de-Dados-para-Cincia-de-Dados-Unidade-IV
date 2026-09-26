"""Verificações de valores, agregação e leitura dos arquivos, sem internet."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import painel as m

class PainelTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        shutil.copytree(m.ROOT/'demonstracao',self.root/'dados')
        self.data=self.root/'dados'
    def tearDown(self):self.temp.cleanup()
    def test_financas_centavos_convertidos_em_reais(self):
        p=m.p1(self.data/'1')
        self.assertEqual([c['value'] for c in p['cards'][:4]],[10,1053,630,423])
    def test_modelo_preserva_matriz_e_metricas(self):
        p=m.p2(self.data/'2')
        self.assertEqual(p['matrix'],[[101,35],[51,53]])
        self.assertAlmostEqual(p['cards'][0]['value'],64.1666666667)
    def test_pipeline_totais_sem_somar_exportacoes(self):
        folder=self.data/'3';first=next((folder/'outputs/execucoes').iterdir())
        shutil.copytree(first,first.parent/'outra_exportacao')
        p=m.p3(folder)
        self.assertEqual(p['cards'][1]['value'],575)
        self.assertEqual(len(p['tables'][0]['rows']),2)
    def test_governanca_nao_le_segredos_nem_expoe_pseudonimos(self):
        folder=self.data/'4';(folder/'segredos').mkdir();(folder/'segredos/admin.token').write_text('TOKEN-SENTINELA')
        p=m.p4(folder);text=json.dumps(p)
        self.assertNotIn('TOKEN-SENTINELA',text)
        self.assertNotIn('cliente_pseudo',text)
        self.assertEqual(p['cards'][4]['value'],'v0001')
    def test_olist_agregacao_antes_da_contagem(self):
        p=m.olist(self.data/'olist');gs=p['olist_groups']
        self.assertEqual(sum(g['orders'] for g in gs),18)
        self.assertEqual(sum(g['late'] for g in gs),6)
        self.assertEqual(sum(g['revenue'] for g in gs),171000)
    def test_olist_mais_itens_nao_multiplica_pedidos(self):
        f=self.data/'olist/olist_order_items_dataset.csv'
        with f.open('a') as out:out.write('EXEMPLO1,2,5.00\n')
        gs=m.olist(self.data/'olist')['olist_groups']
        self.assertEqual(sum(g['orders'] for g in gs),18)
        self.assertEqual(sum(g['revenue'] for g in gs),171500)
    def test_olist_duplicata_identica_removida(self):
        f=self.data/'olist/olist_orders_dataset.csv';line=f.read_text().splitlines()[1]
        with f.open('a') as out:out.write(line+'\n')
        gs=m.olist(self.data/'olist')['olist_groups']
        self.assertEqual(sum(g['orders'] for g in gs),18)
    def test_olist_duplicata_conflitante_bloqueada(self):
        f=self.data/'olist/olist_orders_dataset.csv';line=f.read_text().splitlines()[1].replace('delivered','canceled')
        with f.open('a') as out:out.write(line+'\n')
        with self.assertRaisesRegex(ValueError,'mesmo ID'):m.olist(self.data/'olist')
    def test_olist_sem_precos_nao_mostra_zero_como_receita(self):
        (self.data/'olist/olist_order_items_dataset.csv').unlink()
        self.assertFalse(m.olist(self.data/'olist')['olist_has_prices'])
    def test_projeto_ausente_nao_inventa_indicadores(self):
        p=m.build({'1':self.root/'ausente'},['1'])['pages'][0]
        self.assertEqual(p['status'],'missing');self.assertEqual(p['cards'],[])
    def test_arquivo_invalido_nao_e_tratado_como_sucesso(self):
        (self.data/'1/outputs/python/indicadores.json').write_text('{invalido')
        self.assertEqual(m.build({'1':self.data/'1'},['1'])['pages'][0]['status'],'error')
    def test_leitura_nao_modifica_fontes(self):
        def hashes():return {str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in self.data.rglob('*') if f.is_file()}
        before=hashes();m.build({k:self.data/k for k in m.ADAPTERS},list(m.ADAPTERS))
        self.assertEqual(before,hashes())
    def test_categoria_com_html_nao_injeta_script(self):
        file=self.data/'1/outputs/python/resumo_categoria.csv'
        file.write_text(file.read_text().replace('Informatica','</script><script>alert(1)</script>'))
        output=self.root/'saida com espaço.html'
        result=m.main(['--projeto','1','--pasta',str(self.data/'1'),'--sem-abrir','--saida',str(output)])
        self.assertEqual(result,0)
        self.assertNotIn('</script><script>alert(1)</script>',output.read_text())
        self.assertIn('\\u003c/script\\u003e',output.read_text())
    def test_sem_modelos_serializados(self):
        (self.data/'olist/outputs/modelo_atraso_olist.joblib').write_bytes(b'nao deve ser carregado')
        self.assertEqual(m.olist(self.data/'olist')['status'],'ok')
    def test_cli_com_caminhos_utf8_e_config(self):
        folder=self.root/'análise com espaços';shutil.copytree(self.data/'2',folder)
        cfg=self.root/'config.json';cfg.write_text(json.dumps({'2':str(folder)}))
        output=self.root/'painel.html'
        self.assertEqual(m.main(['--projeto','2','--config',str(cfg),'--sem-abrir','--saida',str(output)]),0)
        self.assertTrue(output.exists())
    def test_valor_nao_finito_recusado(self):
        (self.data/'1/outputs/python/indicadores.json').write_text('{"vendas":NaN}')
        self.assertEqual(m.build({'1':self.data/'1'},['1'])['pages'][0]['status'],'error')

if __name__=='__main__':unittest.main()
