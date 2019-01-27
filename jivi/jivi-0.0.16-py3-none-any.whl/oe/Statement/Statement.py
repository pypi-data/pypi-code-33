from jivi.oe.constants import *

INPUT_KEYWORD['view-as'] = 1


class Statement:
	maintype = 'statement'
	type = 'statement'
	def __init__(self,ar=[],window=0):
		self.window = window
		self.env = 0
		if window:
			self.env = self.window.env
		
		
		self.ar = ar
		self.ori = ar[:]
		
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
				if len(self.ar) < i + 3:
					self.Error('woops')
					print(self.ori)
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
	def set_if_none(self,k,v):
		if k in self.tab and self.tab[k]: return
		self.set(k,v)
		
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
			
	def Error(self,s):
		print('-----------------')
		name = self.name if hasattr(self,'name') else "unknown"
		try:
			print(self.window.fp)
		except:
			pass
		print("{type} [{name}] : {s}".format(type=self.type,name=name,s=s))
		print('-----------------')