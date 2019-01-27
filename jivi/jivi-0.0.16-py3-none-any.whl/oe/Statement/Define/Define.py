from jivi.oe.Statement.Statement import Statement


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