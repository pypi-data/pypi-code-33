from jivi.oe.constants import *
from jivi.fs import *

def remove_from_list(ar,to_remove):
	for i in sorted(to_remove,reverse=1):
		ar = ar[:i] + ar[i+1:]
	return ar



		


def create_tab(ar,t):
	tab = {}
	for a in ar:
		tab[a] = t[a] if a in t else ''
	return tab

	


