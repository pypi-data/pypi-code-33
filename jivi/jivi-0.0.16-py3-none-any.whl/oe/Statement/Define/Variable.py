from jivi.oe.Statement.Define.Widget import Widget
from jivi.oe.Statement.helpers import *
from json import dumps

from jivi.fs import *
to_html_fill_in_format = """<input class = 'inp' type = "text" style="position: absolute; left: {left}px; top: {top}px;height: {height}px; width: {width}px;" value = "{label}">"""

format_label = """<label class = 'hidden lbl' for="{name}">{label}</label>"""

format_withlabel = """
<div style="position: absolute; left: {left}px; top: {top}px" aligned = "{aligned}">
  {label}
  {input}
</div>
"""


format_input = """<input class = 'inp' id = "{name}" type = "text" style="height: {height}px; width: {width}px;" value = "{initial}">"""

def to_html_fill_in(ob,tab):
	pass

html_tab = {}
html_tab['fill-in'] = to_html_fill_in


class Variable(Widget):
	type = 'variable'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)

	def pre_init(self):
		Widget.pre_init(self)
		self.set_variable()
	def html(self,textra={},war=[]):

		tab = {k : v for k,v in self.tab.items()}
		tab.update(textra)
		if 'label' in tab: tab['label'] = nice_string(tab['label'])
		for a in ['view-as','datatype']:
			if not a in tab:
				File.jwrite('tab.json',tab)
				File.jwrite('ar.json',self.ar)
				File.jwrite('ori.json',self.ori)
				
				
				
				self.Error(a)
				exit()
				
		if tab['view-as'] not in ['fill-in','combo-box','radio-set','toggle-box','editor','text']:
			print(tab['view-as'])
			exit()
		t = create_tab('left,top'.split(','),tab)
		t['input'] = format_input.format(**create_tab('name,height,width,initial'.split(','),tab))
		t['label'] = format_label.format(**create_tab('name,label'.split(','),tab))
		
		t['aligned'] = 'bluh'
		if 'aligned' in tab: t['aligned'] = tab['aligned']
		return format_withlabel.format(**t)