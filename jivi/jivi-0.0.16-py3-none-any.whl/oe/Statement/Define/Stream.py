from jivi.oe.Statement.Define.Define import Define



class Stream(Define):
	type = 'stream'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)