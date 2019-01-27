from jivi.oe.Statement.Define.Define import Define

class Parameter(Define):
	type = 'parameter'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)