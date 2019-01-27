from Environment import Environment
from jivi.fs import *

tables = File.jread('out.json')
tt = time()




alias_table = {}
bad = {}

for tablename in tables:
	tmp = tablename[0]
	for i in range(1,len(tablename)):
		tmp += tablename[i]
		
		if tmp in alias_table:
			bad[tmp] = 1
			del alias_table[tmp]
		if tmp in bad: continue
		alias_table[tmp] = 1
		


print(time() - tt)


def test():
	tablename = "ordrln"
	for i in range(len(tablename) - 1,1,-1):
		print(tablename[:i])
		
	
	


exit()
shortcut_link = r"C:\Users\jorisv\Desktop\Intex_links\local\MEC.lnk"

x = Environment(shortcut_link)