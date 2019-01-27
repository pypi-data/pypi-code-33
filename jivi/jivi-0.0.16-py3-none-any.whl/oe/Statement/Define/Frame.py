from jivi.oe.Statement.Define.Widget import Widget
from jivi.oe.Statement.helpers import *

class Frame(Widget):
	type = 'frame'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
		self.widgets = 0
			
	def pre_init(self):
		Widget.pre_init(self)
		i = len(self.ar) - 1
		with_ar = []
		while i != -1:
			if self.ar[i] == 'with':
				with_ar = self.ar[i+1:]
				self.ar = self.ar[:i]
				break
			i -= 1
			
		self.widget_ar = self.ar[:]
		self.ar = with_ar[:]
		

		
	def set_widgets(self,wids):
		widgets = []
		
		war = []
		widget = 0
		
		for i,c in enumerate(self.widget_ar):
			wid = self.window.get_widget(c,1)
			if wid:
				if war:
					widgets.append((widget,war))
				war = []
				widget = wid
			elif is_string(c):
				
				if (not i) or ((((i + 1) < len(self.widget_ar)) and (Keyword(self.widget_ar[i+1]) == 'view-as')) and (not Keyword(self.widget_ar[i-1]) in INPUT_KEYWORD)):
					if war:
						widgets.append((widget,war))
					widget = 0
					war = []
			
			if c: war.append(c)
		
		if war:
			widgets.append((widget,war))
		
		self.read_widgets(widgets)
		
		
	def read_widgets(self,widgets):
		self.widgets = []
		def read_pos(war):
			for i,a in enumerate(war):
				if Keyword(a) == 'at':
					to_remove = [i,i+1,i+2,i+3,i+4]
					top_type = Keyword(war[i+1])
					top_val = war[i+2]
					
					
					
					left_type = Keyword(war[i+3])
					left_val = war[i+4]
					t = dict(top=rtp(top_val,top_type == 'y'),left=ctp(left_val,left_type == 'x'),aligned='normal')
					if t['top'] is None: self.Error("read_pos top is None " + top_val)
					if t['left'] is None: 
						self.Error("read_pos left is None " + left_val)
						t['left'] = 0
						
					
					if ((i + 5) < len(war)) and Keyword(war[i+5]).find('aligned') != -1:
						t['aligned'] = Keyword(war[i+5])
						to_remove.append(i+5)
			
					if t['aligned'] == 'colon-aligned':
						t['left'] += ( 2 * pixels_per_col )
					
					return (t,remove_from_list(war,to_remove))
					
			return ({},war)

		for widget,war in widgets:
			t,war = read_pos(war)
			if not t:
				self.Error("position not found " + str(war))
				continue
			self.widgets.append((t,widget,war))
		
	def html(self,textra={},war=[]):
		if self.widgets == 0:
			self.set_widgets(self.window.defines)
		kak = []
		to_html_frame = """<div class = "frame" style="position: relative; width : 100%; height : 100%">{inner}</div>"""
		
		
		for textra,widget,war in self.widgets:
			if widget:
				kak.append(widget.html(textra,war))
				
		return to_html_frame.format(inner="\n".join(kak))