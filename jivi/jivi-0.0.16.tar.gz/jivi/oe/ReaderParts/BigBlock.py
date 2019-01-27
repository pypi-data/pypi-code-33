from jivi.fs import *
from jivi.oe.Imports import *
"""
	strip comments
	split into
		string
		includes
		pp define

NONE                                               = 0
UNKNOWN                                            = 1
KEYWORD                                            = 2
STRING                                             = 3
STRING_CONCAT                                      = 4
NUMBER                                             = 5
TABLE                                              = 6
FIELD                                              = 7
VAR                                                = 8
BOOLEAN                                            = 9
EXPRESSION                                         = 10
PP_UNKNOWN                                         = 11
PP_SCOP                                            = 12
PP_GLOB                                            = 13
PP_UNDEF                                           = 14
PP_VAR                                             = 15
PP_VAR_CONCAT                                      = 16
PP_PAR                                             = 17
PP_INCL                                            = 18
PP_CONDITION                                       = 19
PP_CONDITIONBLOCK                                  = 20
COMMAND                                            = 21
FILEPATH                                           = 22


"""
from jivi.oe.Imports import *
get_scoped_string_re = re.compile("({([^}{]+)})")
is_scope_local = 7
is_scope_global = 6
is_undefine = 9
is_string = {3 : 1,2 : 1}
is_comment = {1 : 1, -1 : 1}
is_include = {5 : 1, -5 : 1}
is_scope = {is_scope_global : 1, is_scope_local : 1}
preproc_if = 11
preproc_elseif = 21
preproc_else = 31
preproc_endif = 41
preproc_then = 51
is_ppc = {k : 1 for k in [preproc_else,preproc_elseif,preproc_endif,preproc_if,preproc_then]}
string_comment_scopes_ar_ppc = [("/*",1,2),("*/",-1,2),("\"",2,1),("'",3,1),("{",5,1),("}",-5,1),("&glob",6,5),("&scop",7,5),("&undef",9,6),("&if",11,3),("&elseif",21,7),("&else",31,5),("&then",51,5),("&endif",41,6)]
string_appenders = {':%s' % k : 1 for k in 'r,l,c,t,u'.split(',')}
str_numbers = {str(i) : 1 for i in range(10)}
pp_if = "&if"
pp_elseif = "&elseif"
pp_else = "&else"
pp_endif = "&endif"
pp_then = "&then"

def get_find_ar(txt,needlevals):
	ar = []
	for needle,value in needlevals.items():
		la = len(needle)
		index = txt.find(needle)
		while index != -1:
			ar.append((index,value))
			index = txt.find(needle,index+la)

		
	return sorted(ar)
		
		
def create_pp_var_concat(ar):

	new_ar = []
	ret_ar = [PP_VAR_CONCAT,new_ar]
	s = ar[0]

	find_ar = get_find_ar(s,{"{" : 1, "}" : -1})
	l = len(find_ar)
	i = 0
	count = 0
	last_stop_index = 0
	while i < l:
		index,value = find_ar[i]
		stop_index = 0
		i += 1
		if value == 1:
			count = 1
			start_index = index
			while i < l:
				index,value = find_ar[i]
				count += value
				i += 1
				if not count: 
					stop_index = index + 1
					break
			
			if start_index != last_stop_index:
				new_ar.append([STRING,[s[last_stop_index:start_index],NONE]])
			last_stop_index = stop_index
				
			new_ar.append([PP_VAR,s[start_index:stop_index][2:-1].lower().strip()])
			
	s = s[last_stop_index:]
	if s:
		new_ar.append([STRING,[s,NONE]])
		

	do_strings(new_ar)

	return ret_ar
		
	
def create_string_concat(ar):
	new_ar = []
	ret_ar = [STRING_CONCAT,new_ar]
	s = ar[0]
	
	find_ar = get_find_ar(s,{"{" : 1, "}" : -1})
	l = len(find_ar)
	i = 0
	count = 0
	last_stop_index = 0
	while i < l:
		index,value = find_ar[i]
		stop_index = 0
		i += 1
		if value == 1:
			count = 1
			start_index = index
			while i < l:
				index,value = find_ar[i]
				count += value
				i += 1
				if not count: 
					stop_index = index + 1
					break
			
			if start_index != last_stop_index:
				new_ar.append([STRING,[s[last_stop_index:start_index],NONE]])
			last_stop_index = stop_index
				
			new_ar.append([PP_VAR,s[start_index:stop_index][2:-1].lower().strip()])
			
	s = s[last_stop_index:]
	if s:
		new_ar.append([STRING,[s,NONE]])
		


	do_strings(new_ar)

	return ret_ar
	


	
def do_strings(ar):
	for i,a in enumerate(ar):
		if not isinstance(a,list): continue
		if a[0] == STRING:
			index = a[1][0].find("{&")
			if index == -1: continue
			ar[i] = create_string_concat(a[1])
		elif a[0] == PP_VAR:
			index = a[1].find("{&")
			if index == -1: continue
			ar[i] = create_pp_var_concat([a[1]])
		elif a[0] == PP_CONDITIONBLOCK:
			for j,b in enumerate(a[1][0]):
				do_strings(ar[i][1][0][j])
			for j,b in enumerate(a[1][1]):
				do_strings(ar[i][1][1][j])
			
				
			
class PP_Conditionblock:
	condition_starts = {k : 1 for k in [pp_if,pp_elseif,pp_else]}
	condition_stops = {k : 1 for k in [pp_else,pp_elseif]}

	@staticmethod
	def has_ppc(ar):
		for i,a in enumerate(ar):
			if isinstance(a,list) and a[0] == PP_CONDITION:
				return i + 1

	@staticmethod
	def find_stop(ar,start=0):
		started = 0
		count = 0
		for i in range(start,len(ar)):
			x = ar[i]
			if isinstance(x,list) and x[0] == PP_CONDITION:
				if x[1] == "&if":
					count +=1
				elif x[1] == "&endif":
					count -= 1
				if count and (not started): started = 1
				if started and (not count):
					return i + 1

	def __init__(self,ar):
		self.ori = ar[:]
		self.ar = ar[:-1]
		self.condition_statements = []
		self.code_blocks = []
		self.ret_ar = [[PP_CONDITIONBLOCK,[self.condition_statements,self.code_blocks]]]

	def do(self):
		while self.ar:
			ll = len(self.ar)
			self.read_condition()
			self.read_code_block()
			if ll == len(self.ar):
				print("Failing ! PP_Conditionblock")
				print_ar(self.ar)
				print_ar(self.ori)
				exit()
		for i,block in enumerate(self.code_blocks):
			start_index = PP_Conditionblock.has_ppc(block)
			while start_index:
				start_index -= 1
				stop_index = PP_Conditionblock.find_stop(block,start=start_index)
				if not stop_index:
					print("do_ppc stop_index not found ! \n" + str(block[start_index:]))
					exit()
				self.code_blocks[i] = block[:start_index] + PP_Conditionblock(block[start_index:stop_index]).do() + block[stop_index:]
				start_index = PP_Conditionblock.has_ppc(self.code_blocks[i])
		return self.ret_ar

	def read_code_block(self):
		count = 0
		for i,a in enumerate(self.ar):
			if not (isinstance(self.ar[i],list) and self.ar[i][0] == PP_CONDITION): continue
			x = self.ar[i]
			if x[1] == pp_if:
				count += 1
				continue
			if x[1] in self.condition_stops:
				if not count:
					self.code_blocks.append(self.ar[:i])
					self.ar = self.ar[i:]
					return
				continue
			if x[1] == pp_endif:
				count -= 1
				continue
		if not count:
			self.code_blocks.append(self.ar)
			self.ar = []

	def read_condition(self):
		if not (self.ar and isinstance(self.ar,list) and self.ar[0][0] == PP_CONDITION and self.ar[0][1] in self.condition_starts): return
		if self.ar[0][1] == pp_else:
			self.ar = self.ar[1:]
			return
		count = 0
		for i,a in enumerate(self.ar):
			if not i: continue
			if not (isinstance(self.ar[i],list) and self.ar[i][0] == PP_CONDITION): continue
			x = self.ar[i]
			if x[1] == pp_if:
				count += 1
				continue
			if x[1] == pp_then:
				if not count:
					cs = self.ar[1:i]
					self.ar = self.ar[i+1:]
					#print(make_readable_ar(self.ar))
					#print(make_readable_ar(cs))
					self.condition_statements.append(cs)
					return
				continue
			if x[1] == pp_endif:
				count -= 1
				continue
		return None

class Reader:
	def __init__(self,txt):
		self.txt = txt
		self.read()

	def find_all_ar(self,x):
		ar = []
		index = self.txt.find(x)
		while index != -1:
			ar.append(index)
			index = self.txt.find(x,index+1)
		return ar
	read_file_to_replace = ['&glob','&scop','&undef','&elseif','&then','&endif','&if']

	def read(self):
		if not self.txt: return 0
		for a in self.read_file_to_replace:
			for i in range(1,len(a)+1):
				s = a[:i]
				up = s[:-1].lower() + s[-1].upper()
				self.txt = self.txt.replace(up,s.lower())
		return self.txt

	def scs_get_ar(self):
		ar = []
		for needle,value,la in string_comment_scopes_ar_ppc:
			index = self.txt.find(needle)
			while index != -1:
				ar.append((index,value))
				index = self.txt.find(needle,index+la)
		
		return sorted(ar)
	strip_rest_replacers = ['[',']',',','. ',' .','(',')','=']
	strip_rest_replacers_ends = 'procedure,function,case,for,triggers,finally'.split(',')

	def parse_include(self,txt):
		para_tab = {}
		para_ar = []
		ar = get(txt)
		if not ar: return []
		fp = ar[0]
		if isinstance(fp,list):
			if fp[0] == UNKNOWN:
				fp = fp[1]
			elif fp[0] == STRING:
				fp = fp[1][0]
			else:
				self.error("weird parse_include " + str(fp))
				exit()
		else:
			self.error("weird parse_include " + str(fp))
			exit()
		ar = ar[1:]
		if ar:
			ar = flat_ar(ar)
			while ar:
				if ar[0].startswith("&"):
					if len(ar) > 2 and ar[1] == "=":
						para_tab[ar[0][1:].lower().strip()] = ar[2]
						para_ar.append(ar[2])
						ar = ar[3:]
						continue
					else:
						self.error("weird parse_include " + str(txt))
						exit()
				elif ar[0] == "=":
					self.error("weird parse_include === " + str(txt))
					exit()
				else:
					para_ar.append(ar[0])
					ar = ar[1:]
		full_tab = {}
		for k,v in para_tab.items():
			full_tab["&" + k] = v
		for i,a in enumerate(para_ar):
			full_tab[str(i + 1)] = a
		return [[PP_INCL,[fp,full_tab]]]

	def parse_unknown(self,s):
		sar = [""]
		for l in s.split("\n"):
			if l.lower().strip().startswith("&ana"): continue
			sar.append(l)
		sar.append("")
		txt = " ".join(sar).lower().replace("\t"," ").replace(': ','. ')
		for a in self.strip_rest_replacers:
			txt = txt.replace(a,' ' + a + ' ')
		while txt.find('  ') != -1:
			txt = txt.replace('  ',' ')
		for a in self.strip_rest_replacers_ends:
			txt = txt.replace(' end ' + a,' end ')
		txt = txt.replace(' forward ',' end ')
		while txt.find('  ') != -1:
			txt = txt.replace('  ',' ')
		while txt.find('..') != -1:
			txt = txt.replace('..','.')
		ar = []
		for a in txt.strip().split(" "):
			a = a.lower().strip()
			if not a: continue
			kw = Keyword(a)
			if kw != None:
				ar.append(kw)
			else:
				ar.append([UNKNOWN,a])
		return ar

	def get_it(self):
		self.file_scopes = {}
		ignore_indexes = {}
		for a in self.find_all_ar('~'):
			if not a in ignore_indexes:
				ignore_indexes[a+1] = 1
		ar = self.scs_get_ar()
		count = 0
		inum = 0
		lar = len(ar)
		larminone = lar - 1
		self.new_txt_ar = []
		to_add = 0
		start_index_replaced = 0
		stop_index_replaced = 0
		last_stop = 0

		def get_next_stop_blank_or_new_line(index):
			rindex = len(self.txt)
			for a in [" ","\n","."]:
				ind = self.txt.find(a,index)
				if ind != -1 and ind < rindex: rindex = ind
			return rindex

		def read_until_blank(index):
			while self.txt[index+1:index+2] == " ":
				index += 1
			return index
		while inum < lar:
			start_inum = inum
			start_index_replaced,val = ar[inum]
			stop_index_replaced = 0
			if val == is_undefine:
				stop_index_replaced = self.txt.find(" ",start_index_replaced)
				stop_index_replaced = read_until_blank(stop_index_replaced)
				found_index = stop_index_replaced
				stop_index_replaced = get_next_stop_blank_or_new_line(found_index + 1)
				to_add = [[PP_UNDEF,self.txt[found_index+1:stop_index_replaced].lower().strip()]]
			elif val in is_ppc:
				stop_index_replaced = get_next_stop_blank_or_new_line(start_index_replaced)
				txt = self.txt[start_index_replaced:stop_index_replaced].lower().strip()
				to_add = [[PP_CONDITION,txt]]
			elif val in is_scope:
				stop_index_replaced = self.txt.find("\n",start_index_replaced)
				shouldbreak = 0
				if stop_index_replaced == -1:
					stop_index_replaced = len(self.txt)
					shouldbreak = 1
				r = self.txt[start_index_replaced:stop_index_replaced].rstrip()
				while r.endswith('~'):
					if shouldbreak:
						break
					stop_index_replaced = self.txt.find("\n",stop_index_replaced + 1)
					shouldbreak = 0
					if stop_index_replaced == -1:
						stop_index_replaced = len(self.txt)
						shouldbreak = 1
					r = self.txt[start_index_replaced:stop_index_replaced].rstrip()
				scopename = 0
				scopenamear = r.replace('~','').split(' ')
				scopevalue = 0
				for i,x in enumerate(scopenamear):
					if not i: continue
					scopename = x.lower().strip()
					if not scopename: continue
					scopevalue = ' '.join(scopenamear[i+1:])
					break
				type = PP_GLOB
				if val == is_scope_local:
					type = PP_SCOP
				to_add = [[type,[scopename,scopevalue]]]
			elif val in is_string:
				inum += 1
				string_val = val
				string_found = 0
				string_txt = 0
				string_format = NONE
				while inum < larminone:
					if (ar[inum][0] in ignore_indexes):
						next_ind = ar[inum][0] + 1
						inum += 1
					elif (ar[inum][1] != string_val):
						inum += 1
					elif (ar[inum + 1][1] == string_val) and (ar[inum + 1][0] == (ar[inum][0] + 1)):
						inum += 2
					else:
						string_found = ar[inum][0]
						break
				if (not string_found) and (inum < lar) and (ar[inum][1] == string_val):
					string_found = ar[inum][0]
				if string_found:
					string_txt = self.txt[start_index_replaced:string_found+1]
				if string_found and self.txt[string_found + 1:string_found + 3].lower() in string_appenders:
					string_format = self.txt[string_found + 2:string_found + 3].lower()
					string_found += 2
					while self.txt[string_found+1] in str_numbers:
						string_found += 1
						string_format += self.txt[string_found+1]
				if not string_found:
					x = self.txt.find("\n",start_index_replaced + 1)
					self.info(self.txt[start_index_replaced:x])
					self.add_error_at_pos("do_str_c_pre : not string_found",start_index_replaced)
					string_found = start_index_replaced
					string_txt = self.txt[start_index_replaced:string_found+1]
					inum = start_inum
				start = start_index_replaced
				stop_index_replaced = string_found + 1
				string_txt = string_txt[1:-1]
				to_add = [[STRING,[string_txt,string_format]]]
			elif val in is_include:
				count = val
				inum += 1
				found = 0
				while inum < lar:
					index,val = ar[inum]
					if val in is_include:
						count += val
						if count < 0: self.error("Error !")
						if not count:
							start = start_index_replaced
							stop_index_replaced = index + 1
							found = 1
							break
					inum += 1
				if not found:
					self.add_error_at_pos("do_str_c_pre : is_include not found! started at line ",start_index_replaced)
				txt = self.txt[start_index_replaced:stop_index_replaced][1:-1].strip()
				if txt[:1] == '&':
					to_add = [[PP_VAR,txt[1:].lower()]]
				else:
					to_add = self.parse_include(txt)
			elif val in is_comment:
				to_add = []
				last_index_plus_one = 0
				count = val
				inum += 1
				found_comment = 0
				while inum < lar:
					index,val = ar[inum]
					if val in is_comment and last_index_plus_one != index:
						count += val
						if count < 0: self.error("Error !")
						if not count:
							start = start_index_replaced
							stop_index_replaced = index + 2
							found_comment = 1
							break
						last_index_plus_one = index + 1
					inum += 1
				if not found_comment:
					x = self.txt.find("\n",start_index_replaced + 1)
					self.error(self.txt[start_index_replaced:x])
					self.add_error_at_pos("do_str_c_pre : is_comment not found_comment! started at line ",start_index_replaced)
			else:
				 self.error('val not found')
				 self.error(val)
			while (start_inum == inum) or (inum < lar and (ar[inum][0] < stop_index_replaced)):
				inum += 1
			rest_txt = self.txt[last_stop:start_index_replaced].strip()
			if rest_txt:
				self.new_txt_ar += self.parse_unknown(rest_txt)
			if to_add:
				self.new_txt_ar += to_add
			last_stop = stop_index_replaced
		rest_txt = self.txt[stop_index_replaced:].strip()
		if rest_txt:
			self.new_txt_ar += self.parse_unknown(rest_txt)
		while self.has_ppc():
			self.do_ppc()
		do_strings(self.new_txt_ar)
		return self.new_txt_ar

	
		

	def do_ppc(self):
		count = 0
		ppc_stop_index = PP_Conditionblock.find_stop(self.new_txt_ar,start=self.ppc_index)
		if not ppc_stop_index:
			self.error("do_ppc ppc_stop_index not found ! \n" + str(self.new_txt_ar[self.ppc_index:]))
			exit()
		self.new_txt_ar = self.new_txt_ar[:self.ppc_index] + PP_Conditionblock(self.new_txt_ar[self.ppc_index:ppc_stop_index]).do() + self.new_txt_ar[ppc_stop_index:]

	def has_ppc(self):
		for i,a in enumerate(self.new_txt_ar):
			if isinstance(a,list) and a[0] == PP_CONDITION:
				self.ppc_index = i
				return 1

def get(txt,nice=0):
	ar = Reader(txt).get_it()
	if nice:
		return make_readable_ar(ar)
	return ar