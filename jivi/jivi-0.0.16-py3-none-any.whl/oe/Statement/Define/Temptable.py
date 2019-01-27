from jivi.oe.Statement.Define.Define import Define
from jivi.oe.Statement.Define.Field import Field

class Temptable(Define):
	type = 'temp-table'
	def __init__(self,*a,**b):
		self.fields = {}
		Define.__init__(self,*a,**b)
		
		
	def pre_init(self):
		Define.pre_init(self)
		to_remove = []
		self.header = []
		
		for ind,a in enumerate(self.ar):
			if a.lower().strip() in ['index','field']:
				break
			to_remove.append(ind)
			self.header.append(a)
		self.remove(*to_remove)
		to_remove = []
		
		tmpvelden = []
		veld = []
		velden = []
		for ind,a in enumerate(self.ar):
			n = a.lower().strip()
			if n == 'index':
				break
			to_remove.append(ind)
			if n == 'field':
				if veld:
					tmpvelden.append(veld)
					velden.append(Field(veld,self.window))
				veld = []
			veld.append(n)
			
		if veld:
			velden.append(Field(veld,self.window))
			tmpvelden.append(veld)
			
		self.tmpvelden = tmpvelden
		for veld in velden:
			self.fields[veld.name.lower()] = veld
		self.remove(*to_remove)
		
		
	def get_field(self,fn):
		if not fn in self.fields:
			print(self.tmpvelden)
			self.Error('field not found' + fn + "\n" + "\n".join(list(self.fields.keys())))
			
			
		return self.fields[fn]
	
