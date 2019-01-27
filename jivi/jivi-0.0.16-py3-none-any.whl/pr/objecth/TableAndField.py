from jivi.pr.Object import Object

from jivi.pr.objecth.Variable import Variable


	



			
	
class Field(Variable):


	def __init__(self,*a,**b):
		table = 0
		if 'table' in b:
			table = b['table']
			del b['table']
		
		Variable.__init__(self,*a,**b)
		if table:
			self.table = table
			self.table.register_field(self)
			

class Table(Object):
	attr = []
	attr.append(dict(n='name',r=1,a='_file-name',lower=1))

	def __init__(self,*a,**b):
		self.fields = {}
		Object.__init__(self,*a,**b)
		
		
	
	def register_field(self,f):
		self.fields[f.name] = f