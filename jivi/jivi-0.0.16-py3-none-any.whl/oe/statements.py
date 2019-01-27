from jivi.oe.constants import *

from jivi.fs import *
	
def remove_from_list(ar,to_remove):
	for i in sorted(to_remove,reverse=1):
		ar = ar[:i] + ar[i+1:]
	return ar

INPUT_KEYWORD['view-as'] = 1

class Statement:
	maintype = 'statement'
	type = 'statement'
	def __init__(self,ar,window):
		self.window = window
		self.env = self.window.env
		self.ori = ar[:]
		self.ar = ar
		self.tab = {}
		self.pre_init()
		
		
		self.read_images()

		for a in INPUT_KEYWORD.keys():
			self.read_input(a)
			
		self.read_size()
		
	
	def html(self,textra={},war=[]):
		return ''
	def read_input(self,name,keyword=0):
		if not keyword:
			keyword = name
		
		if not Keyword(keyword):
			print(keyword)
			exit()
		keyword = Keyword(keyword)
		for i,a in enumerate(self.ar[:-1]):
			if Keyword(a) == keyword:
				self.set(name,Alias(self.ar[i+1]))
				self.remove(i,i+1)
				return 1
				
	def pre_init(self):
		pass
			
	def read_size(self):


		for i,x in enumerate(self.ar):
			kw = Keyword(x)
			if kw.find('size') != -1:
				self.set('width',wtp(self.ar[i+1],kw.find('pix') != -1))
				self.set('height',htp(self.ar[i+3],kw.find('pix') != -1))
				return self.remove(i,i+1,i+2,i+3)
	def read_images(self):
		read_images_tab = {'image' : 'image','image-up' : 'image','image-down' : 'image-down','image-insensitive' : 'image-insensitive'}
		
		def read_one():
			lar = len(self.ar)
			for i,x in enumerate(self.ar):
				mainkw = Keyword(x)
				if mainkw in read_images_tab:
					to_remove = [i]
					i += 1
					t = {'file' : 0,'from' : []}
					
				
					def do_next(do_remove=1,forced=0):
						nonlocal i,to_remove
						if forced or i == lar: return (mainkw,t,to_remove)
						i += 1
						if i == lar: return (mainkw,t,to_remove)
						if do_remove: to_remove.append(i)
					
					kw = Keyword(self.ar[i])
					if kw == 'file':
						to_remove.append(i)
						if do_next(): return do_next()
						t['file'] = self.ar[i]
						if do_next(0): return do_next()
						kw = Keyword(self.ar[i])
					
					if kw.find('size') != -1:
						to_remove.append(i)
						if do_next(): return do_next()
						t['w'] = wtp(self.ar[i],kw.find('pix') != -1)
						if do_next(): return do_next()
						t['h'] = htp(self.ar[i],kw.find('pix') != -1)
						if do_next(0): return do_next()
						kw = Keyword(self.ar[i])
						
					if kw == 'from':
						to_remove.append(i)
						if do_next(): return do_next()
						t['from'] = self.ar[i]

					
					return do_next(0,1)
			return (0,0,0)
		mainkw,t,to_remove = read_one()

		while mainkw:
			self.remove(*to_remove)
			if not t['from']:
				del t['from']
			self.set(mainkw,t)
			mainkw,t,to_remove = read_one()
	def set(self,k,v):
		self.tab[k] = v
		setattr(self,k,v)
	def remove(self,*a):
		ar = sorted(a,reverse=1)
		for i in ar:
			self.ar = self.ar[:i] + self.ar[i+1:]
		
		
	def remove_keyword(self,kw):
		for i,a in enumerate(self.ar):
			if Keyword(a) == Keyword(kw):
				self.remove(i)
				break
	def update(self,t):
		for a,b in t.items():
			self.set(a,b)
		
class Define(Statement):
	maintype = 'define'
	
	def __init__(self,*a,**b):
		self.view_as = 0
		
		Statement.__init__(self,*a,**b)
		
		
	def pre_init(self):
		self.name = "unknown"
		self.remove_keyword('define')
		self.remove_keyword('no-undo')
		self.read_input('name',self.type)
		self.set('name',self.name.lower())
class Widget(Define):
	type = 'widget'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)

	def pre_init(self):
		Define.pre_init(self)
		
	
class Frame(Widget):
	type = 'frame'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
		
			
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
			cc = c.lower().strip()
			if cc in wids:
				if war:
					widgets.append((widget,war))
				war = []
				widget = wids[cc]
			elif is_string(cc):
				
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
					
					t = dict(left=ctp(left_val,left_type == 'x'),top=rtp(top_val,top_type == 'y'),aligned='normal')
					if ((i + 5) < len(war)) and Keyword(war[i+5]).find('aligned') != -1:
						t['aligned'] = Keyword(war[i+5])
						to_remove.append(i+5)
			
					
					
					return (t,remove_from_list(war,to_remove))
					
			return ({},war)

		for widget,war in widgets:
			t,war = read_pos(war)
			if not t:
				print(war)
				continue
			self.widgets.append((t,widget,war))
		
	def html(self,textra={},war=[]):
		kak = []
		to_html_frame = """<div class = "frame" style="position: relative; width : 100%; height : 100%">{inner}</div>"""
		
		
		for textra,widget,war in self.widgets:
			if widget:
				kak.append(widget.html(textra,war))
				
		return to_html_frame.format(inner="\n".join(kak))
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
class Browse(Widget):
	type = 'browse'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
					
class Buffer(Widget):
	type = 'buffer'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
					
class Image(Widget):
	type = 'image'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
					
class Rectangle(Widget):
	type = 'rectangle'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)




class Menu(Widget):
	type = 'menu'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)


class Submenu(Widget):
	type = 'sub-menu'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)



to_html_fill_in_format = """<input class = 'inp' type = "text" style="position: absolute; left: {left}px; top: {top}px;height: {height}px; width: {width}px;" value = "{label}">"""

format_label = """<label class = 'hidden lbl' for="{name}">{label}</label>"""

format_withlabel = """
<div style="position: absolute; left: {left}px; top: {top}px">
  {label}
  {input}
</div>
"""


format_input = """<input id = "{name}" type = "text" style="height: {height}px; width: {width}px;" value = "{initial}">"""

def create_tab(ar,t):
	tab = {}
	for a in ar:
		tab[a] = t[a] if a in t else ''
	return tab

class Variable(Widget):
	type = 'variable'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)

	def pre_init(self):
		Widget.pre_init(self)
		self.read_input('datatype','as')
		self.read_input('name','var')
	def html(self,textra={},war=[]):

		tab = {k : v for k,v in self.tab.items()}
		tab.update(textra)
		if 'label' in tab: tab['label'] = nice_string(tab['label'])


		t = create_tab('left,top'.split(','),tab)
		t['input'] = format_input.format(**create_tab('name,height,width,initial'.split(','),tab))
		t['label'] = format_label.format(**create_tab('name,label'.split(','),tab))
		
		return format_withlabel.format(**t)
class Query(Define):
	type = 'query'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)



class Parameter(Define):
	type = 'parameter'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)


class Temptable(Define):
	type = 'temp-table'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)

class Worktable(Define):
	type = 'work-table'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)

class Workfile(Define):
	type = 'workfile'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)

class Dataset(Define):
	type = 'dataset'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)



class Stream(Define):
	type = 'stream'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)
		

class Field:
	type = 'field'
	def __init__(self,t):
		self.tab = t
		for a,b in t.items():
			setattr(self,a,b)