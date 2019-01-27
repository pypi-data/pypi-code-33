from Stripper import Stripper

from jivi.fs import *

#File.jwrite('kak.json',list(Dir.files(r'C:\develop\l_intex',ex='w',deep=1,full=1)))
# exit()
kak = File.jread('kak.json')
for i,fp in enumerate(kak):
	if i <= 247: continue	
	Stripper(0,fp)
	try:
		Stripper(0,fp)
	except:
		print(i)	
		print(fp)
		exit()
	print(i)
