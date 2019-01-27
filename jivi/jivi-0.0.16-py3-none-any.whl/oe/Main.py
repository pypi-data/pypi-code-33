from jivi.oe.Imports import *
exec(Wrapper.main_setter)


from jivi.oe.Env import Env
from jivi.oe.Session import Session
from jivi.oe.Compiler import Compiler





def log_traceback(ex, ex_traceback=None):
	os.system("\n")
	if ex_traceback is None:
		ex_traceback = ex.__traceback__
	tb_lines = [ line.rstrip('\n') for line in traceback.format_exception(ex.__class__, ex, ex_traceback)]
	print("\n".join(tb_lines))





		
class FPC(Wrapper):
	def __init__(self,MAIN):
		set_main(MAIN)
		self.main = File.dir(os.path.realpath(__file__))
		self.temp = Dir.create(self.main + '_temp')
		self.compiled_first_step = Dir.create(self.main + '_compiled_first_step')
		self.compiled = Dir.create(self.main + '_compiled')
		self.static = Dir.create(self.main + "_static")
		self.data = Dir.create(self.main + '_data')
		
		self.test = r'C:\develop\l_intex\Intex\incl\intex_maintrig_inq_lookup.i' #self.static + 'test.p'
		
class Main:
	FP = 0
	ENV = 0
	SESSION = 0
	REPLACER = Data()
	def __init__(self):
		self.FP = FPC(self)
		self.ENV = Env(self)
		self.SESSION = Session(self)
		self.todocounter = 0
		set_main(self)
		
	def compile_all_helper(self,ar):
		for fp in ar:
			c = Compiler(self,fp)
			c.do()
		self.todocounter -= 1
	def compile_all(self):
		STEPS = 5
		self.todocounter = STEPS
		for ar in Ar.steps(SESSION.all_files,STEPS):
			Thread(self.compile_all_helper,(ar,))
		
		while self.todocounter:
			sleep(1)
		
		
		Wrapper.print_times(Compiler)

	def test(self):
		c = Compiler(self,txt=File.all(FP.test))

	def compile(self,fps):
		for i,fp in enumerate(fps):
			print(fp + "\n")
			try:
				
				c = Compiler(self,fp=fp)
				if not c.do():
					print("failed to compile " + fp)
					c.write_ar_readable()
					exit()
			except Exception as ex:
				print("Main compile error !")
				print(fp)

				log_traceback(ex)
				print("yay")
				return (0,i,fp)
		return (1,0,0)
if __name__ == "__main__":
	MAIN = Main()

	for a in sys.argv[1:]:
		a = a.lower().strip()
		if a in ['ca']:
			MAIN.compile_all()
		elif a in ['t']:
			MAIN.test()