"""
	comments in preproc => verwijder
	comments in strings => NIET !
	


"""

from jivi.oe.constants import *
from jivi.fs import *

from StripperGood import *
ALL_KW = {k : 1 for k in ALIAS.keys()}
for k in DEFINE_TYPES.keys(): ALL_KW[k] = 1


def is_kw(s):
	s = s.lower().strip()
	return s in ALL_KW
from time import time

strip_string_comments_preproc_ar = [(a,b,len(a)) for a,b in [('/*',1),('*/',-1),('"',2),("'",3),('{',5),('}',-5),('&glob',6),('&scop',7)]]
"""
eerst alle strings en comments weg daarna dubbele spaties
"""

is_number_val = 8


is_string = {3 : 1,2 : 1}
is_comment = {1 : 1, -1 : 1}
is_include = {5 : 1, -5 : 1}
is_scope = {6 : 1, 7 : 1}
string_appenders = {':%s' % k : 1 for k in 'r,l,c,t,u'.split(',')}
str_numbers = {str(i) : 1 for i in range(10)}
is_scope_local = 7


def is_decimal(x):
	try:
		s = float(x)
		return 1
	except:
		return 0
		
def should_replace(s):
	if s == '.': return 0
	if is_decimal('0' + s): return 1
	s = s.strip()
	ind = s.find('.',1) 
	if ind != -1 and ind != (len(s) - 1): return 1
	


class Stripper(StripperGood):
	dos = ['read_file','set_replace_char','strip_string_coment','do_preproc','remove_preproc_conditions','strip_rest','create_commands','create_indent']
	dos = ['read_file','set_replace_char','strip_string_coment']
	

		
	def strip_string_coment(self):
		ignore_indexes = {}
		index = self.txt.find('~')
		while index != -1:
			ignore_indexes[index+1] = 1
			index = self.txt.find('~',index+1)
	
	
	def remove_preproc_conditions(self):
		index_now = self.txt.find('&')
		while index_now != -1:
			stop_index = self.txt.find(" ",index_now)
			txt = self.txt[index_now:stop_index]
			print(txt)
			exit()
			shouldbreak = 0
			if stop_index == -1: 
				stop_index = len(self.txt)
				shouldbreak = 1
			
			r = self.txt[index_now:stop_index].rstrip()


		
	def strip_string_comments_preproc(self):
		ignore_indexes = {}
		index = self.txt.find('~')
		while index != -1:
			ignore_indexes[index+1] = 1
			index = self.txt.find('~',index+1)
		
		
		
		count = 0

		ar = []
		for needle,value,la in strip_string_comments_preproc_ar:
			index = self.txt.find(needle)
			while index != -1:
				ar.append((index,value))
				index = self.txt.find(needle,index+la)
		
		
		ar.sort()
		inum = 0
		lar = len(ar)
		larminone = lar - 1
		temp_ar = []
		
		add_to_replaced = 0
		start_index_replaced = 0
		stop_index_replaced = 0
		last_stop = 0
		while inum < len(ar):
			
			start_inum = inum
			start_index_replaced,val = ar[inum]
			stop_index_replaced = 0
			if val in is_scope:
				stop_index_replaced = self.txt.find("\n",start_index_replaced)
				shouldbreak = 0
				if stop_index_replaced == -1: 
					stop_index_replaced = len(self.txt)
					shouldbreak = 1
				
				r = self.txt[start_index_replaced:stop_index_replaced].rstrip()
					
						
				while r.endswith('~'):
					r = r[:-1]
					if shouldbreak:
						break
					stop_index_replaced = self.txt.find("\n",stop_index_replaced + 1)
					shouldbreak = 0
					if stop_index_replaced == -1: 
						stop_index_replaced = len(self.txt)
						shouldbreak = 1
					r = self.txt[start_index_replaced:stop_index_replaced].rstrip()
				
				add_to_replaced = 0
				self.scopes.append(((val == is_scope_local),r))
		
				
			elif val in is_string:
				add_to_replaced = 1
				inum += 1
				string_val = val
				string_found = 0
				while inum < larminone:
					if (ar[inum][1] != string_val) or (ar[inum][0] in ignore_indexes):
						inum += 1
					elif (ar[inum + 1][1] == string_val) and (ar[inum + 1][0] == (ar[inum][0] + 1)):
						inum += 2
					else:
						string_found = ar[inum][0]
						break
				if (not string_found) and (inum < lar) and (ar[inum][1] == string_val):
					string_found = ar[inum][0]
				if string_found and self.txt[string_found + 1:string_found + 3].lower() in string_appenders:
					string_found += 2
					
					while self.txt[string_found+1] in str_numbers:
						string_found += 1
				if not string_found:
					self.add_error_at_pos("do_str_c_pre : not string_found",start_index_replaced,func='add_all_strings')
					string_found = start_index_replaced
					inum = start_inum
				
				start = start_index_replaced
				stop_index_replaced = string_found + 1

			elif val in is_include:
				add_to_replaced = 1
				count = val
				inum += 1
				found = 0
				while inum < lar:
					index,val = ar[inum]
					if val in is_include:
						count += val
						if count < 0: print("Error !")
						if not count:
							start = start_index_replaced
							stop_index_replaced = index + 1

							found = 1
							break
					inum += 1
				if not found:
					self.add_error_at_pos("do_str_c_pre : is_include not found! started at line ",start_index_replaced)
			elif val in is_comment:
				add_to_replaced = 0
				last_index_plus_one = 0
				count = val
				inum += 1
				found_comment = 0
				while inum < lar:
					index,val = ar[inum]
					if val in is_comment and last_index_plus_one != index:
						count += val
						if count < 0: print("Error !")
						if not count:
							start = start_index_replaced
							stop_index_replaced = index + 2
							found_comment = 1
							break
						last_index_plus_one = index + 1
					inum += 1
				if not found_comment:
					self.add_error_at_pos("do_str_c_pre : is_comment not found_comment! started at line ",start_index_replaced)
					
					
			while inum < lar and (ar[inum][0] < stop_index_replaced):
				inum += 1
			if last_stop != start_index_replaced:
				temp_ar.append(self.txt[last_stop:start_index_replaced])
			if add_to_replaced:
				self.replaced.append(self.txt[start_index_replaced:stop_index_replaced])
				temp_ar.append(self.replace_with)
			last_stop = stop_index_replaced
				
		temp_ar.append(self.txt[stop_index_replaced:])
		self.txt = "".join(temp_ar)
		return len(self.errors) == 0
		
	strip_rest_replacers = ['[',']',',','. ','(',')']
	strip_rest_replacers_ends = 'procedure,function,case,for,triggers'.split(',')
	

	
	def strip_rest(self):
		index_now = self.txt.find('&')
		while index_now != -1:

			stop_index = self.txt.find("\n",index_now)
			shouldbreak = 0
			if stop_index == -1: 
				stop_index = len(self.txt)
				shouldbreak = 1
			
			r = self.txt[index_now:stop_index].rstrip()
				
					
			while r.endswith('~'):
				r = r[:-1]
				if shouldbreak:
					break
				stop_index = self.txt.find("\n",stop_index + 1)
				shouldbreak = 0
				if stop_index == -1: 
					stop_index = len(self.txt)
					shouldbreak = 1
				r = self.txt[index_now:stop_index].rstrip()
				
			self.txt = self.txt[:index_now] + self.txt[stop_index:]
			index_now = self.txt.find('&')
		self.txt = self.txt.replace("\t"," ").replace("\n"," ").lower().replace(self.replace_with,' ' + self.replace_with + ' ').replace(':','.')
		for a in self.strip_rest_replacers:
			self.txt = self.txt.replace(a,' ' + a + ' ')

		
		while self.txt.find('  ') != -1:
			self.txt = self.txt.replace('  ',' ')
		for a in self.strip_rest_replacers_ends:
			self.txt = self.txt.replace(' end ' + a,' end ')

		self.txt = self.txt.replace(' forward ',' end ')
		while self.txt.find('  ') != -1:
			self.txt = self.txt.replace('  ',' ')
		self.txt = self.txt.strip()
		return 1

	indent_starts_anywhere = ['do','case','repeat']
	indent_starts = ['function','procedure']
	indent_starts_special = ['for']
	indent_starts_special_good = ['then','else']
	indent_starts_ends = ['triggers']

	def create_indent(self):
		self.indent = []
		indent = 0
		for a in (self.commands):
			if a and not isinstance(a[0],list):
				if a[0] in self.indent_starts:
					indent += 1
			for i,x in enumerate(a):
				if x == 'end':
					indent -= 1
				elif x in self.indent_starts_anywhere:
					indent += 1
				elif x in self.indent_starts_special:
					if not i or (a[i-1] in self.indent_starts_special_good):
						indent += 1
				elif x in self.indent_starts_ends:
					if i == (len(a) - 1):
						indent += 1
			self.indent.append(indent)
		if indent:
			self.writer()
			self.error(indent)
			exit()
		return 1

	

	def create_commands(self):
		
		self.ar = []
		new_replaced = []
		self.replace_with_new = '0'
		counter = 0

		last_rep = 0
		do_rep = 0
		reps = []
		for a in self.txt.split(' '):
			last_rep = do_rep
			do_rep = 0
			
			if a == self.replace_with:
				to_add = self.replaced[counter]
				counter += 1
				do_rep = 1

			elif should_replace(a) or not is_kw(a):
				to_add = a
				do_rep = 1
				
			if do_rep:
				if last_rep:
					new_replaced[len(new_replaced) - 1].append(to_add)
				else:
					new_replaced.append([to_add])
					self.ar.append(self.replace_with)
				continue
			if a:
				self.ar.append(Alias(a.lower().strip()))
				
		self.replaced = new_replaced
		counter = 0
		self.commands = []
		for c in ' '.join(self.ar).split('.'):
			ar = c.strip().split(' ')
			if not ar: continue
			start_ar = []
			first = 0
			
			for i,x in enumerate(ar):
				if x == self.replace_with: 
					start_ar.append(counter)
					counter += 1
					first = i + 1
					continue
				
				break
			if first:
				self.commands.append(start_ar)
				ar = ar[first:]

				
			nc = []
			for a in ar:
				if a == self.replace_with:
					nc.append(counter)
					counter += 1
				else:
					nc.append(a)
			if nc:
				self.commands.append(nc)
		
		
	
		return 1
	