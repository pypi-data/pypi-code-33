from jivi.oe import *
from jivi import *
from jivi.oe.constants import *

  
read_images_tab = {'image' : 'image','image-up' : 'image','image-down' : 'image-down','image-insensitive' : 'image-insensitive'}

# FILE name
   # [{ IMAGE-SIZE | IMAGE-SIZE-CHARS | IMAGE-SIZE-PIXELS }
      # width BY height
# ]
# [ FROM { X n Y n | ROW n COLUMN n }]



# { IMAGE-SIZE | IMAGE-SIZE-CHARS | IMAGE-SIZE-PIXELS }
   # width BY height
# [ FROM { X n Y n | ROW n COLUMN n }]


def read_image(ar,i):
	new_ar = ar[:i]
	ar = ar[i+1:]
	t = {'file' : 0,'from' : []}
	
	
	kw = full_keyword(ar[0])
	if kw == 'file':
		t['file'] = ar[1]
		ar = ar[2:]
		if not ar: return (new_ar + ar,t)
		
		kw = full_keyword(ar[0])
	
	
	
	if kw.find('size') != -1:
		t['w'] = wtp(ar[1],kw.find('pix'))
		t['h'] = htp(ar[3],kw.find('pix'))
		ar = ar[4:]
		if not ar: return (new_ar + ar,t)
		kw = full_keyword(ar[0])
		
	if kw == 'from':
		t['from'] = ar[:4]
		ar = ar[4:]
	
	return (new_ar + ar,t)
	
		
	
def read_images(ob,ar):

	for i,x in enumerate(ar):
		kw = full_keyword(x)
		if kw in read_images_tab:
			ar,image = read_image(ar,i)
			ob.set_attr(read_images_tab[kw],image)
			return read_images(ob,ar)
	return ar
def read_size(ob,ar):
	size_chars = ['size','size-chars']

	for i,x in enumerate(ar):
		kw = full_keyword(x)
		found = 0
		w = 0
		h = 0
		
		if kw in size_chars:
			w = wtp(float(ar[i+1]))
			h = htp(float(ar[i+3]))
			found = 1
		elif kw == 'size-pixels':
			w = (float(ar[i+1]))
			h = (float(ar[i+3]))
			found = 1
		if found:
			ob.set_attr('width',round(w,2))
			ob.set_attr('height',round(h,2))
			
			ar = ar[:i] + ar[i+4:]
			break
	return ar
			

def read_query(ob,ar):
	
	ob.set_attr('query',ar)
	return ar



class view_as:
	all_types = {k : k.replace('-','_') for k in 'fill-in,combo-box,editor,toggle-box,radio-set,text,selection-list,slider'.split(',')}

	def __init__(self,ob,ar):
		self.tab = {}
		self.ob = ob
		self.ar = ar
		self.type = ar[0]
		self.ar = ar[1:]
		if not self.type in self.all_types:
			print(self.type)
			print(self.ar)
			
		self.ar = read_size(ob,self.ar)
		getattr(self,self.all_types[self.type])()
	def fill_in(self):
		pass
	def combo_box(self):
		pass
	def editor(self):
		pass
	def toggle_box(self):
		pass
	def radio_set(self):
		pass
	def text(self):
		pass
	def selection_list(self):
		pass
	def slider(self):
		pass

	def val(self):
		return dict(type=self.type,rest=self.ar)
	
	
to_html_button_format = """<button style="position: absolute; left: {left}px; top: {top}px;height: {height}px; width: {width}px;" title = {label}></button>"""
def to_html_button(tab):

	t = {}
	for a in 'label,left,top,height,width'.split(','):
		t[a] = tab[a] if a in tab else ''
	return to_html_button_format.format(**t)
	
to_html_fill_in_format = """<input type = "text" style="position: absolute; left: {left}px; top: {top}px;height: {height}px; width: {width}px;" value = {label}>"""
def to_html_fill_in(tab):

	t = {}
	for a in 'label,left,top,height,width'.split(','):
		t[a] = tab[a] if a in tab else ''
	if not t['label']: t['label'] = '""'
	return to_html_fill_in_format.format(**t)

class Widget:
	has_datatype = {k : 1 for k in ['parameter','variable']}
	def __init__(self,ar,left=0,top=0,extra=[]):
		
		self.original = ar[:]
		self.ar = ar
		self.tab = dict(left=left,top=top)
		self.view_as = 0
		self.type = 0
		
		self.strip_keyword('def')
		self.succes = self.do()
		self.tab['rest'] = self.ar
		
		
		
	def set_size(self):
		read_size(self)
	@property
	def html(self):
		if not self.succes: return ''
		
		if self.type == 'button':
			return to_html_button(self.tab)
			
		if self.view_as and 'type' in self.view_as and self.view_as['type'] == 'fill-in':

			return to_html_fill_in(self.tab)
		return ""
		
		
	def do(self):

		if not self.set_type_and_name():
			self.Error('failed to set set_type_and_name')
			print(self.ar)
			return 0
		
		if self.type in self.has_datatype:
			if not self.set_datatype():
				return 0
		
		if self.type == 'temp-table':
			self.read_tt()
			return
		

		self.set_query()
		self.set_view_as()
		self.ar = read_images(self,self.ar)
		
		self.set_init()
		self.set_attr('format',self.read_one('format'))
		self.set_singles()
		
		self.ar = read_size(self,self.ar)
		self.set_vals()
		self.set_images()
		
		
		return 1
	def read_tt(self):
		self.ar = []
	def set_query(self):
		for i,a in enumerate(self.ar):
			if full_keyword(a) == 'query':
				read_query(self,self.ar[i+1:])

				self.ar = self.ar[:i]
				break
		
	def set_images(self):
		pass
	def set_vals(self):
		for i,a in enumerate(self.ar):
			kw = full_keyword(a)
			if kw in input_keywords:
				self.set_attr(kw,self.ar[i+1])
				self.ar = self.ar[:i] + self.ar[i+2:]
				return self.set_vals()
	def set_singles(self):
		
		for i,a in enumerate(self.ar):
			kw = full_keyword(a)
			if kw in keyword_single:
				self.set_attr(kw,1)
				self.ar = self.ar[:i] + self.ar[i+1:]
				return self.set_singles()
	
	def set_view_as(self):
		for i,a in enumerate(self.ar):
			if full_keyword(a) == 'view-as':
				tmpx = self
				self.view_as = view_as(tmpx,self.ar[i+1:]).val()
				
				self.ar = self.ar[:i]
				break

		

		
	def set_init(self):
		self.init = self.read_one('init')
		return self.init
	def make_tab(self):
		self.left = self.ar
		return {k : getattr(self,k) for k in self.new_tab_attr}
	

		
	def read_one(self,kw):
		kw = full_keyword(kw)
		for i,a in enumerate(self.ar):
			if full_keyword(a) == kw:
				val = self.ar[i+1]
				self.ar = self.ar[:i] + self.ar[i+2:]
				return val
	
	def set_datatype(self):
		return self.set_attr('datatype',self.read_one('as'))

	
	
	
	def set_attr(self,k,v):
		setattr(self,k,v)
		self.tab[k] = v
		return v
	
	def set_type_and_name(self):
		for i,a in enumerate(self.ar):
			if a in define_types:
				self.set_attr('type',define_types[a])
				self.set_attr('name',self.ar[i+1])
				self.ar = self.ar[:i] + self.ar[i+2:]
				return 1
		
	def strip_keyword(self,kw):
		kw = full_keyword(kw)
		for i,ar_kw in enumerate(self.ar):
			if full_keyword(ar_kw) == kw:
				self.ar = self.ar[:i] + self.ar[i+1:]
				break
				
	def Error(self,s):
		print(self.original)
		print(s)
