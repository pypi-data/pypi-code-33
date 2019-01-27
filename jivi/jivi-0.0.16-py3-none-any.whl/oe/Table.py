from jivi.oe.Statement.Define.Widget import Widget

class Table:
	def __init__(self):
		self.fields = {}
		self.name = "not set"
		
	def from_json(self,t):
		
		for a,b in t.items():
			setattr(self,a,b)
			
		self.name = self.name.lower().strip()
		return self
		
		
	def get_field(self,fn):
		if not fn in self.fields:
			self.Error('field not found' + fn)
		return self.fields[fn]
	
	def Error(self,s):
		print("Table {name} : {s}".format(name=self.name,s=s))
	
	
	def create_alias_fields(self):
		self.alias_field = {}
		bad = {}
		
		for fieldname,field in self.fields.items():
			for i in range(len(fieldname) - 1,1,-1):
				tmp = fieldname[:i]
				if tmp in self.alias_field:
					bad[tmp] = 1
					del self.alias_field[tmp]
				if tmp in bad: continue
				self.alias_field[tmp] = table

class Field(Widget):
	type = 'field'
	def __init__(self,*a,**b):
		Widget.__init__(self,*a,**b)
		self.fullName = ''
		self.name = ''

	def from_json(self,t):
		conv = [('data_type','datatype'),('view_as','view-as')]
		for van,naar in conv:
			
			t[naar] = t[van]
			del t[van]
			
		
		for a,b in t.items():
			self.set(a,b)
			
		self.fullName = self.table.name + '.' + self.name
		
		self.fullName = self.fullName.lower().strip()
		self.name = self.name.lower().strip()
		
		self.table.fields[self.name] = self

		return self
