from jivi.oe.Statement.Define.Widget import Define


class Dataset(Define):
	type = 'dataset'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)