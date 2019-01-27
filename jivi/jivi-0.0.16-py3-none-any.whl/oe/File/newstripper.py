from jivi.oe.constants import *
from jivi.fs import *

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
	


class Stripper:
	dos = ['read_file','set_replace_char','strip_string_comments_preproc','strip_rest','create_commands_new']

	def __init__(self,env,fp):
		self.errors = []
		self.replaced = []
		self.commands = []
		self.scopes = []
		self.env = env
		self.fp = File.fp(fp)
		for do in self.dos:
			if not getattr(self,do)():
				self.error("failed to do {do}".format(do=do))
				break
		
		self.write()
		
	read_file_to_replace = ['&glob','&scop']
	

	
	def read_file(self):
		self.txt = File.all_full(self.fp)
		
		if not self.txt: return 0
		for a in self.read_file_to_replace:
			
			for i in range(1,len(a)+1):
				s = a[:i]
				up = s[:-1].lower() + s[-1].upper()
				self.txt = self.txt.replace(up,s.lower())
				
		
		return self.txt
		
		
	
	def set_replace_char(self):
		self.replace_with = 0
		self.replace_with_len = 0
		for i in range(255):
			x = chr(i).lower()
			if self.txt.find(x) == -1 and self.txt.find(x.upper()) == -1:
				self.replace_with = x
				self.replace_with_len = len(x)
				break
				
		return self.replace_with
	def error(self,s):
		print("Stripper\n{fp}\n{s}".format(fp=self.fp,s=s))

	def write(self):
		File.write("out\\" + File.base(self.fp),self.txt)

		
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
		
		
	strip_rest_replacers = ['[',']',',','. ']
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
		self.txt = self.txt.strip()
		return 1
	def create_commands_new(self):
		
		self.ar = []
		new_replaced = []
		self.replace_with_new = '0'
		counter = 0

		last_rep = 0
		do_rep = 0
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
					new_replaced[-1] += ' ' + to_add
				else:
					new_replaced.append(to_add)
					self.ar.append(self.replace_with)
				continue
			if a:
				self.ar.append(a)
				
		self.replaced = new_replaced
		counter
		self.commands = []
		for c in ' '.join(self.ar).split('.'):
			nc = []
			for a in c.strip().split(' '):
				if a == self.replace_with:
					nc.append(counter)
					counter += 1
				else:
					nc.append(a)
			if nc:
				self.commands.append(nc)
		
		return 1
		
	def create_commands_new_old(self):
		
		self.ar = []
		new_replaced = []
		self.replace_with_new = '0'
		counter = 0
		for a in self.txt.split(' '):
			if a == self.replace_with:
				new_replaced.append(self.replaced[counter])
				counter += 1
				self.ar.append(self.replace_with_new)
				continue
			if should_replace(a) or not is_kw(a):
				new_replaced.append(a)
				self.ar.append(self.replace_with_new)
				continue
			if a:
				self.ar.append(a)
				
		self.replaced = new_replaced
		
		self.commands = [c.strip().split(' ') for c in ' '.join(self.ar).split('.')]
		File.jwrite('commands.txt',self.commands)
		
				
	def create_commands(self):

		self.ar = []
		new_replaced = []
		
		counter = 0
		for a in self.txt.split(' '):
			if a == self.replace_with:
				new_replaced.append(self.replaced[counter])
				counter += 1
				self.ar.append(self.replace_with)
				continue
			if should_replace(a):
				new_replaced.append(a)
				self.ar.append(self.replace_with)
				continue
			if a:
				self.ar.append(a)
				
		self.replaced = new_replaced
		
		self.commands = [c.strip().split(' ') for c in ' '.join(self.ar).split('.')]
		File.jwrite('commands.txt',self.commands)
		File.jwrite('replaced.txt',self.replaced)
	
	def get_line(self,pos):
		return self.txt_o.count("\n",0,pos)

	def add_error_at_pos(self,s,pos,*a,**b):
		l = self.get_line(pos)
		if l != None:
			return self.add_error(s + "\nat line {l}".format(l=l+1),*a,**b)
		return self.add_error(s + "\n at pos " + str(pos),*a,**b)

	def add_error(self,s,func=0):
		self.errors.append(s)

	def write_error(self,error_name,s,add=1):
		fp = "out\\" + self.name + "__" + error_name + self.ex
		with open(fp,"w") as f:
			f.write(s)
		if add:
			self.errors.append(fp)
		return fp

