from jivi.fs import *
from jivi.oe.Helper.Keyword import *
from jivi.oe.Helper.Wrapper import Wrapper
import traceback,sys,re,json
len_KEYWORD_AR = len(KEYWORD_AR)

string_starts = {k : k for k in ['"',"'"]}

CONSTANTS = [
"NONE",
"UNKNOWN",
"KEYWORD",
"STRING",
"STRING_CONCAT",
"NUMBER",
"TABLE",
"FIELD",
"VAR",
"BOOLEAN",
"EXPRESSION",
"PP_UNKNOWN",
"PP_SCOP",
"PP_GLOB",
"PP_UNDEF",
"PP_VAR",
"PP_VAR_CONCAT",
"PP_PAR",
"PP_INCL",
"PP_CONDITION",
"PP_CONDITIONBLOCK",
"COMMAND",
"FILEPATH"]


for i,c in enumerate(CONSTANTS):
	exec(c + " = " + str(i + len_KEYWORD_AR))
	KEYWORD_AR.append(c)
	
	
def Keyword(x):
	s = x.lower().strip()
	return KEYWORD_TAB[s] if s in KEYWORD_TAB else None



DOT = KEYWORD_TAB['.']


def make_readable_ar_helper(ar):
	if isinstance(ar,int): return KEYWORD_AR[ar]
	if not isinstance(ar,list): 
		return ar

	new_ar = []
	for i,xel in enumerate(ar):
		if (not i) and (isinstance(xel,int)):
			new_ar.append(KEYWORD_AR[xel])
		else:
			new_ar.append(make_readable_ar_helper(xel))
			
	
	return new_ar
def make_readable_ar(ar):
	new_ar = []
	for a in ar:
		new_ar.append(make_readable_ar_helper(a))
	return new_ar
	
def print_ar(ar):
	print(make_readable_ar(ar))

def flat_ar(ar):
	new_ar = []
	for a in ar:
	
		if isinstance(a,int):
			new_ar.append(KEYWORD_AR[a])
		else:
			if a[0] == STRING:
				new_ar.append(json.dumps(a[1][0]))
			else:
				new_ar.append(a[1])
	return new_ar

if __name__ == "__main__":
	print("\n".join(["{a} = {i}".format(a=String.minlen(a,50),i=i) for i,a in enumerate(CONSTANTS)]))
	
	