from Imports import *

from Main import Main
from Compiler import Compiler
#Compiler.todo = Compiler.todoss

exec(Wrapper.main_setter)
M = Main()



set_main(M)
c = Compiler(M,r'c:\\develop\\l_intex\\framework\\prg\\mainimag.w').do()

exit()
for fp in SESSION.all_files:
	x = File.all(SESSION.fp_compiled(fp,1))
	if x.find("{&") != -1:
		print(SESSION.fp_compiled(fp,1))

		
		
exit()

for fp in SESSION.all_files:
	
	if File.ex(fp).lower() == "w":
		c = Compiler(M,fp)
		c.do()
		exit()