from jivi.oe.Statement.Define.Widget import Widget
from jivi.oe.Statement.helpers import *


to_html_button_format = """<button name = "{name}" style="position: absolute; left: {left}px; top: {top}px;height: {height}px; width: {width}px;" title = "{label}"></button>"""
class Button(Widget):
	type = 'button'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)

				
	def html(self,textra={},war=[]):
		t = {}
		tab = {k : v for k,v in self.tab.items()}
		tab.update(textra)
		if 'label' in tab: tab['label'] = nice_string(tab['label'])
		for a in 'label,left,top,height,width,name'.split(','):
			t[a] = tab[a] if a in tab else ''
		return to_html_button_format.format(**t)