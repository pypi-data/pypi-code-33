from jivi.oe.Statement.Define.Define import Define

class Workfile(Define):
	type = 'workfile'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)