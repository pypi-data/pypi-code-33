from jivi.fs import *

class StripperGood:
	
	def __init__(self,env,fp):
		self.errors = []
		self.replaced = []
		self.commands = []
		self.scopes = []
		self.env = env
		self.fp = File.fp(fp)
		for do in self.dos:
			if not getattr(self,do)():
				self.error("failed to do {do}".format(do=do))
				break
		
		self.write()
		
	read_file_to_replace = ['&glob','&scop','&scop']
	

	def read_file(self):
		self.txt = File.all_full(self.fp)
		
		if not self.txt: return 0
		for a in self.read_file_to_replace:
			
			for i in range(1,len(a)+1):
				s = a[:i]
				up = s[:-1].lower() + s[-1].upper()
				self.txt = self.txt.replace(up,s.lower())
				
		
		return self.txt
		
		
	
	def set_replace_char(self):
		self.replace_with = 0
		self.replace_with_len = 0
		for i in range(255):
			x = chr(i).lower()
			if self.txt.find(x) == -1 and self.txt.find(x.upper()) == -1:
				self.replace_with = x
				self.replace_with_len = len(x)
				break
				
		return self.replace_with
	def error(self,s):
		print("Stripper\n{fp}\n{s}".format(fp=self.fp,s=s))

	def write(self):
		File.write("out\\" + File.base(self.fp),self.txt)


	def writer(self):
		File.jwrite('commands.txt',self.commands)
		File.jwrite('replaced.txt',self.replaced)
		self.write_indent()
	
	
			
	def get_line(self,pos):
		return self.txt_o.count("\n",0,pos)

	def add_error_at_pos(self,s,pos,*a,**b):
		l = self.get_line(pos)
		if l != None:
			return self.add_error(s + "\nat line {l}".format(l=l+1),*a,**b)
		return self.add_error(s + "\n at pos " + str(pos),*a,**b)

	def add_error(self,s,func=0):
		self.errors.append(s)

	def write_error(self,error_name,s,add=1):
		fp = "out\\" + self.name + "__" + error_name + self.ex
		with open(fp,"w") as f:
			f.write(s)
		if add:
			self.errors.append(fp)
		return fp

	def write_indent(self):
		to_write = []
		last_c = 0
		for i,c in enumerate(self.commands):
			cc = []
			for x in c:
				if isinstance(x,int):
					cc.append(" ".join(self.replaced[x]))
					last_c = x
				else:
					cc.append(x)
			
			to_write.append("\t"*self.indent[i] + " ".join(cc) + '.')
			if self.indent[i] < 0: break
			
		print(last_c)
		File.write('indent.w',"\n".join(to_write))