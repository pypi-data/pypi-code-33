from jivi.oe.Statement.Define.Define import Define
class Worktable(Define):
	type = 'work-table'
	def __init__(self,*a,**b):
		Define.__init__(self,*a,**b)