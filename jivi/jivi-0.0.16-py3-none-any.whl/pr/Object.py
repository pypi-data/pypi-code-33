	

from .Viewas import viewas

class HasHelper:
	def __init__(self,ob):
		self.ob = ob
		
	def __getattr__(self,k):
		ob = getattr(self,'ob')
		if k == 'ob': return ob
		return k in ob.t
		

class Object:
	attr = []
	attr.append(dict(n='name',r=1,lower=1))

	
	can_set = {}
	name = "unknown"
	error_pause = 0
	def __init__(self,env=0,window=0,tab={}):
		self.error_pause = 0
		self.errors = []
		self.set_attr()
		self.env = env
		self.has = HasHelper(self)
		self.t = {}
		self.window = window
		try:
			self.session = self.env.session
		except:
			pass
		
		if window:
			self.env = self.window.env
		if tab:
			self.set_tab(tab)
		
		self.va = viewas(self)
			
			
	def set_attr(self):
		self.attibute = {}
		self.can_set = {}
		
		default = dict(r=0,s=1,a=0,lower=0)
		classes = type(self).mro()[:-1]
		attr = {}
		self.main_object = classes[0]
		if not hasattr(self.main_object,'ignore'):
			self.main_object.ignore = {}
		
		self.type = classes[0].__name__
		for cl in classes:
			if not hasattr(cl,'attr'): continue
			for t in cl.attr:

				n = t['n'].lower()
				if not n in self.attibute:
					self.attibute[n] = {}
					self.attibute[n].update(default)
					
				if 'a' in t:
					for x in t['a'].split(','):
						x = x.lower()
						if not x: continue
						if x in self.can_set and self.can_set[x] != n:
							self.error('set_attr {x} already set to {old} not {new}'.format(x=x,old=self.attr_alias[x],new=n))
						
						self.can_set[x] = n
				self.can_set[n] = n
				self.attibute[n].update(t)
		
				

		

		
	def set(self,a,b):
		a = a.lower()
		if not a in self.can_set:
			if not a in self.main_object.ignore:
				self.main_object.ignore[a] = 1
			else:
				return
				
			return self.error("cant set " + a)
			
		attr = self.attibute[self.can_set[a]]
		if attr['lower']:
			b = b.lower().strip()
		setattr(self,attr['n'],b)
		self.t[attr['n']] = b
		
	def set_tab(self,tab={}):

				
		self.error_pause = 1
		for a,b in tab.items():
			self.set(a,b)
		
		self.error_resume()
		
	def error_resume(self):
		self.error_pause = 0
		if not self.errors: return
		self.error(" ".join(self.errors))
		self.errors = []
	def html(self):
		return "no html"
		
		
	def error(self,s):
		if self.error_pause:
			self.errors.append(s)
			return
		print("[{type}]{name} : {s}".format(type=self.type,name=self.name,s=s))
	
	
	def __setattr__(self,k,v):
		if not k in self.can_set:
			return object.__setattr__(self,k,v)
		self.t[self.attibute[self.can_set[k]]['n']] = v
		return object.__setattr__(self,self.attibute[self.can_set[k]]['n'],v)
	
	
	def htp(self,*a,**b):
		return self.session.htp(*a,**b)
		
	def wtp(self,*a,**b):
		return self.session.wtp(*a,**b)

	def ctp(self,*a,**b):
		return self.session.ctp(*a,**b)

	def rtp(self,*a,**b):
		return self.session.rtp(*a,**b)
		
	def ptc(self,*a,**b): 		return self.session.ptc(*a,**b)