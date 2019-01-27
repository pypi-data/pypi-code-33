from jivi.oe.Imports import *
exec(Wrapper.main_setter)

from jivi.oe.ReaderParts.BigBlock import get as GetBigBlock



class Compiler(Wrapper):
	
	todofs = ['read_file_first_step','readit_first_step','writeit_first_step']
	todoss = ['read_file_ss','readit_ss','writeit_ss']
	
	todo = todofs
	def __init__(self,main,fp):
		set_main(main)

		self.fp = File.fp(fp).lower().strip()
		self.fp_compiled_first_step = SESSION.fp_compiled(self.fp,1)
		self.fp_compiled_ss = SESSION.fp_compiled(self.fp,0)
		
		self.name = self.fp + "\nCompiler"

		
	def read_file_ss(self):
		self.ar = File.jread(self.fp_compiled_first_step)
		
	def readit_ss(self):
		pass
		
	def writeit_ss(self):
		File.jwrite(self.fp_compiled_ss,self.ar)
	
	def read_file_first_step(self):
		self.txt = File.all_full(self.fp)
		if not self.txt: return 0

		
		return self.txt
		
		
		
		
		

				 
				
	def readit_first_step(self):
		self.ar = [[FILEPATH,self.fp]] + GetBigBlock(self.txt)
		

	def writeit_first_step(self):
		File.jwrite(self.fp_compiled_first_step,self.ar,indent=None)
		#File.jwrite(self.fp_compiled_first_step,make_readable_ar(self.ar))
		
		