"""nester.py: Este módulo realiza operações aninhadas sobre listas.
	Para testar execute: nester.print_lol(['teste1', ['teste1.1', 'teste1.2', ['teste1.2.1', 'teste1.2.2', 'teste1.2.3'], 'teste1.3'], 'teste2'], 2)
"""

import sys

def print_lol(the_list, indent=False, level=0, out=sys.stdout):
	"""Imprime na tela cada item da lista"""
	for each_item in the_list:
		if isinstance(each_item, list): #verifica se o item é uma instância da list
			print_lol(each_item, indent, level + 1, out) #aumenta o endentamento do nivel
		else:
			if indent:
				for num in range(level):
					print("\t", end = '', file=out)
			print(each_item, file=out)