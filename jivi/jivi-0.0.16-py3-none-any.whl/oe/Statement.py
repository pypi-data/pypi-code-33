from jivi.oe.constants import *
from jivi.oe.statements import *



define_tab = {k.lower() : v for k,v in dict(Dataset=Dataset,stream=Stream,Workfile=Workfile,Query=Query,Menu=Menu,Parameter=Parameter,Frame=Frame,Button=Button,Browse=Browse,Buffer=Buffer,Image=Image,Rectangle=Rectangle,Variable=Variable).items()}
define_tab['temp-table'] = Temptable
define_tab['sub-menu'] = Submenu
define_tab['work-table'] = Worktable




not_implented = {}

def define(ar,window):
	global not_implented
	for i,a in enumerate(ar):
		type = DefineType(a)
		if not type: continue
	
		if not type in define_tab:
			not_implented[type] = 1
		else:
			return define_tab[type](ar,window)
		break

statements = {}
statements['define'] = define

		

def statement(ar,window):
	if not ar: return 0
	kw = Keyword(ar[0])
	if not kw:
		print("statement start is not a keyword {start}".format(start=ar[0]))
		return 0
	if not kw in statements:
		print("statement keyword {kw} not yet implemented".format(kw=kw))
		return 0
		
	return statements[kw](ar,window)