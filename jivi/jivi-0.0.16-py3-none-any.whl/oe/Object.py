

class Object:
	
	def __init__(self,env,type,name):
		self.env = env
		self.type = type
		self.name = name
		
		
		
	def html(self):
		return "no html"
		
		
	def error(self,s):
		print("[{type}]{name} : {s}".format(type=self.type,name=self.name,s=s))
	
	