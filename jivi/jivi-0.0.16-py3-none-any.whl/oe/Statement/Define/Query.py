from jivi.oe.Statement.Define.Define import Define
class Query(Define):
	type = 'query'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)