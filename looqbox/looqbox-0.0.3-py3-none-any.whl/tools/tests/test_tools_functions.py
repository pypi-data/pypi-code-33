import unittest
from looqbox.objects.looq_table import ObjTable
from looqbox.tools.tools import *
import pandas as pd


class TestDataComp(unittest.TestCase):

    def test_data_comp(self):
        """
        Test data_comp function
        """
        table1 = ObjTable(data=pd.DataFrame({'Loja': ['SP', 'RJ', 'BH'],
                                             'Quantidade': [100, 310, 89],
                                             'Vendas': [2500, 5300, 1750]}))

        table1.value_format = {'Quantidade': 'number:0',
                               'Vendas': 'number:2'}

        table1.total = {'Loja': 'Total',
                        'Quantidade': sum(table1.data['Quantidade']),
                        'Vendas': sum(table1.data['Vendas'])}

        table2 = ObjTable(data=pd.DataFrame({'Loja': ['SP', 'RJ', 'BH'],
                                             'Quantidade': [30, 400, 120],
                                             'Vendas': [950, 6000, 2200]}))

        table2.value_format = {'Quantidade': 'number:0',
                               'Vendas': 'number:2'}

        table2.total = {'Loja': 'Total',
                        'Quantidade': sum(table2.data['Quantidade']),
                        'Vendas': sum(table2.data['Vendas'])}

        table = data_comp(table1, table2, by='Loja')

        self.assertEqual(pd.DataFrame({'Loja': ['SP', 'RJ', 'BH'],
                                       'Quantidade_P1': table1.data['Quantidade'],
                                       'Quantidade_P2': table2.data['Quantidade'],
                                       'D_Quantidade': (table1.data['Quantidade'] -
                                                        table2.data['Quantidade']) / table2.data['Quantidade'],
                                       'Vendas_P1': table1.data['Vendas'],
                                       'Vendas_P2': table2.data['Vendas'],
                                       'D_Vendas': (table1.data['Vendas'] -
                                                    table2.data['Vendas']) / table2.data['Vendas']}).all().all(),
                         table.data.all().all())

        self.assertDictEqual({'Loja': 'Total',
                              'Quantidade_P1': sum(table1.data['Quantidade']),
                              'Quantidade_P2': sum(table2.data['Quantidade']),
                              'D_Quantidade': -0.09272727272727277,
                              'Vendas_P1': sum(table1.data['Vendas']),
                              'Vendas_P2': sum(table2.data['Vendas']),
                              'D_Vendas': 0.04371584699453557},
                             dict(table.total))

        self.assertDictEqual({'Quantidade_P1': table1.value_format['Quantidade'],
                              'Quantidade_P2': table1.value_format['Quantidade'],
                              'D_Quantidade': 'percent:2',
                              'D_Vendas': 'percent:2',
                              'Vendas_P1': table1.value_format['Vendas'],
                              'Vendas_P2': table1.value_format['Vendas']},
                             table.value_format)

        self.assertRaises(Exception, data_comp, 'sjdhka', table2, by='Loja')

        self.assertRaises(Exception, data_comp, table1, 'kjdfhdskj', by='Loja')

        table1.value_format = None
        table = data_comp(table1, table2, by='Loja')

        self.assertEqual(None, table.value_format)

    def test_transpose_data(self):
        """
        Test transpose_data function
        """
        table = ObjTable(data=pd.DataFrame({'Código': [2121], 'Preço': [25.70], 'Estoque': [21],
                                            'ABC Global': ['A1'], 'Tipo de Produto': ['OTC'],
                                            'Mg': [750], 'Fabricante': ['J & J'], 'Qtd. Comprimidos': [20]}))

        table.value_format = {'Código': 'number:0', 'Preço': 'number:2', 'Estoque': 'number:0',
                              'Mg': 'number:0', 'Qtd. Comprimidos': 'number:0'}

        table.value_style = {'Código': {'color': 'blue'}, 'Tipo de Produto': {'color': 'yellow'}}

        #TODO: add value_link test

        transposed_table = transpose_data(table, ['Atributo', 'Valor'])

        self.assertEqual(pd.DataFrame({'Atributo': ['Código', 'Preço', 'Estoque', 'ABC Global', 'Tipo de Produto', 'Mg',
                                           'Fabricante', 'Qtd. Comprimidos'],
                              'Valor': [2121, 25.7, 21, 'A1', 'OTC', 750, 'J & J', '20']}).all().all(),
                         transposed_table.data.all().all())

        self.assertDictEqual({'0': 'number:0', '1': 'number:2', '2': 'number:0', '5': 'number:0', '7': 'number:0'},
                             transposed_table.row_format)

        self.assertDictEqual({'0': {'color': 'blue'}, '4': {'color': 'yellow'}}, transposed_table.row_style)

