from Imports import *
"""

UNKNOWN                                            = 0
KEYWORD                                            = 1
STRING                                             = 2
NUMBER                                             = 3
TABLE                                              = 4
FIELD                                              = 5
VAR                                                = 6
BOOLEAN                                            = 7
EXPRESSION                                         = 8
PP_UNKNOWN                                         = 9
PP_SCOP                                            = 10
PP_GLOB                                            = 11
PP_UNDEF                                           = 12
PP_VAR                                             = 13
PP_PAR                                             = 14
PP_INCL                                            = 15
COMMAND                                            = 16

"""
from jivi.oe.ReaderParts.BigBlock import get as GetBigBlock
def check_ar(ar):
	good = 1
	for x in ar:
		if isinstance(x,list):
			if not check_ar(x): return 0
			continue
		if len(x) == 1: continue
		if x.endswith(":"): return 0
		if x.endswith("."): return 0
	return 1
	
	

def check_ar(ar):
	ret = []
	for a in ar:
		if not isinstance(a,list): continue
		if a[0] == PP_INCL and a[1][1]:
			ret.append(a[1][1])
	return ret
def old():

	for fp in Dir.files("_compiled",ex="json",full=1):
		a = File.jread(fp)
		
		if not check_ar(a):
			print(fp)
			exit()
				
	all = []
		
	for fp in Dir.files("_compiled",ex="json",full=1):
		a = File.jread(fp)
		all += check_ar(a)


	File.jwrite("all.json",all)
	
	
	
	
	
	
	
	
	
def do(rest):
	ar = GetBigBlock(rest)
	
	args = dict(ar=[],tab={})
	while rest:
		ar = rest.split(" ")
		first_word = ar[0]
		
		if first_word.startswith("&") and len(ar) > 2 and ar[1] == "=":
			rest = " ".join(ar[2:]).strip()
			if rest[0] in string_starts:
				
				index = rest.find(rest[0],1)
				args['tab'][first_word[1:].lower().strip()] = rest[1:index]
				rest = rest[index:]
			
				print(args)
				exit()
		else:
			args['ar'].append(first_word)
			rest = " ".join(ar[1:])
	
	
	


for fp in Dir.files("_compiled",ex="json",full=1):
	a = File.jread(fp)
	if not a: continue
	for x in a:
		if isinstance(x,int): continue
		if x[0] == PP_INCL and x[1][1]:
			print(x[1])
	
	