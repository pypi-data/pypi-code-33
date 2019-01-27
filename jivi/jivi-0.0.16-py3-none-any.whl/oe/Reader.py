from jivi.fs import *
from os import system
from time import time
from jivi.oe.constants import *

def is_decimal(x):
	try:
		s = float(x)
		return 1
	except:
		return 0
		
zoek_ar = [(a,b,len(a)) for a,b in [('/*',1),('*/',-1),('"',2),("'",3),('{',5),('}',-5),('&glob',4),('&scop',4)]]
is_string = {3 : 1,2 : 1}
is_comment = {1 : 1, -1 : 1}
is_include = {5 : 1, -5 : 1}
is_scope = 4
string_appenders = {':%s' % k : 1 for k in 'r,l,c,t,u'.split(',')}
str_numbers = {str(i) : 1 for i in range(10)}

replace_with = ' R'
replace_with_len = len(replace_with)
ignore_scope = 1
do_rep = {k : 1 for k in 'variable,define'.split(',')}

class Reader:
	funcs = 'str_com,make_replaced,do_connected,make_replaced_two,make_ar,set_replaced_txt,make_new_commands_ar,set_indent'.split(',')
	funcs = 'str_com,make_replaced,do_connected,make_replaced_two,make_ar'.split(',')
	
	times = {k : 0 for k in funcs}

	def __init__(self,fp=None,txt=None):
		self.new_commands = 0
		self.errors = []
		self.commands = []
		if fp is not None: 	
			if not self.set_fp(fp):
				return
			
		if txt is not None: self.set_txt(txt)
		for k in self.funcs:
			ss = time()
			getattr(self,k)()
			self.times[k] += time() - ss

	def set_indent(self):
		self.indent = []

	def old_write_o(self):
		self.replaced_txt = [self.txt_o[start:stop] for start,stop,x in self.replaced]
		self.commands_txt = []
		


		for i,c in enumerate(self.commands):

			self.commands_txt.append(c[:])
			for j,cw in enumerate(self.commands_txt[i]):
				
				if isinstance(cw,int):
					self.commands_txt[i][j] = self.replaced_txt[cw]
					
					 
		File.jwrite("o\\" + self.name + ".json",self.commands_txt)
	
	
	def set_replaced_txt(self):
		self.replaced_txt = []
		for start,stop,x in self.replaced:
			txt = self.txt_o[start:stop].strip()
			if txt.endswith(':u'):
				txt = txt[:-2]
			
			self.replaced_txt.append(txt)
			

		
	def make_new_commands_ar(self):
		
		
		
		self.commands_txt = []
		
		new_commands = []

		for i,c in enumerate(self.commands):
			new_commands_ar = []
			replaced_last_one = 0
			found_special = 0
			for j,cw in enumerate(c):
				#found_special = found_special or cw == 'radio-buttons'
				if isinstance(cw,int):
					
					if replaced_last_one:
						new_commands_ar[-1] += self.replaced_txt[cw]
					else:
						new_commands_ar.append(self.replaced_txt[cw])
					replaced_last_one = 1
				
				elif cw.find(',') != -1 or (replaced_last_one and is_decimal(cw)):
					if replaced_last_one:
						new_commands_ar[-1] += cw
					else:
						new_commands_ar.append(cw)
					replaced_last_one = 1
	
					
				elif cw:
					replaced_last_one = 0
					if cw in alias and alias[cw] in do_rep:
						new_commands_ar.append(alias[cw])
					else:
						new_commands_ar.append(cw)
			if new_commands_ar: new_commands.append(new_commands_ar)
			if found_special:
				print(new_commands_ar)
				exit()
		
		self.new_commands = new_commands

	def write_o(self):
		self.replaced_txt = [self.txt_o[start:stop] for start,stop,x in self.replaced]
		self.commands_txt = []
		
		new_commands = []

		for i,c in enumerate(self.commands):
			new_commands_ar = []
			for j,cw in enumerate(c):
				if isinstance(cw,int):
					new_commands_ar.append(self.replaced_txt[cw])
				elif cw:
					new_commands_ar.append(cw)
			if new_commands_ar: new_commands.append(new_commands_ar)
			
		
			
		File.jwrite("o\\" + self.base,new_commands)

		
	def make_ar(self):
		self.txt = self.txt.replace("\n"," ").replace('R',' R ')
		while self.txt.find('  ') != -1:
			self.txt = self.txt.replace('  ', ' ')
		#self.commands = [c.strip().split(' ') for c in rec.sub(' ',self.txt.replace("\n"," ")).replace('R',' R ').split('.')]
		self.commands = [c.strip().split(' ') for c in self.txt.split('.')]
		#self.commands = [[w.strip() for w in c.split(' ') if w.strip()] for c in self.txt.replace("\n", " ").replace('R',' R ').split('.')]
		self.replaced_good_index = 0
		for i,c in enumerate(self.commands):
			for j,cw in enumerate(c):
				if self.commands[i][j] == 'R':
					self.commands[i][j] = self.replaced_good_index
					self.replaced_good_index += 1




	def set_fp(self,fp):
		self.fp 	= File.fp(fp)
		self.name 	= File.name(fp)
		self.base 	= File.base(fp)
		self.ex		= File.ex(fp)
		return self.set_txt(txt= File.all(fp))

	def filter_lines_old(self,lines):
		self.lines = []
		next_append = 0
		self.pre_defines = []
		inum = 0
		while inum < len(lines):
			l = lines[inum].lower().strip()
			if (not l) or l.startswith('&analyze'):
				inum += 1
				continue
			if l.startswith(('&scop','&glob')):
				if not l.endswith('~'):
					self.pre_defines.append(l)
					inum += 1
					continue
				line_ar = [l]
				while l.endswith('~') and inum < len(lines):
					inum += 1
					l = lines[inum].lower().strip()
					line_ar.append(l)
				self.pre_defines.append(" ".join(line_ar))
				inum += 1
				continue
			if l.startswith('&'):
				if not l.endswith('~'):
					self.lines.append(l)
					inum += 1
					continue
				line_ar = [l]
				while l.endswith('~') and inum < len(lines):
					inum += 1
					l = lines[inum].lower().strip()
					line_ar.append(l)
				self.lines.append(" ".join(line_ar))
				inum += 1
				continue
			else:
				self.lines.append(l)
				inum += 1
				continue
	def filter_linesx(self,lines):
		self.lines = []
		next_append = 0
		self.pre_defines = []
		inum = 0
		ll = len(lines) - 1
		while inum < ll:
			inum += 1
			l = lines[inum].lower().strip()
			if (not l) or l.startswith('&analyze'):
				continue
			if l.startswith('&'):
				if not l.endswith('~'):
					self.lines.append(l)
					continue
				line_ar = [l]
				while l.endswith('~') and inum < len(lines):
					inum += 1
					l = lines[inum].lower().strip()
					line_ar.append(l)
				self.lines.append(" ".join(line_ar))
				continue
			else:
				self.lines.append(l)
				continue
	def filter_lines(self,lines):
		self.lines = []
		next_append = 0
		self.pre_defines = []
		inum = -1
		ll = len(lines) - 1
		while inum < ll:
			inum += 1
			l = lines[inum].lower().strip()
			if (not l) or l.startswith('&analyze'):
				continue
			if l.endswith('~'):
				line_ar = [l]
				while l.endswith('~') and inum < len(lines):
					inum += 1
					l = lines[inum].lower().strip()
					line_ar.append(l)
				self.lines.append(" ".join(line_ar))
				continue
			else:
				self.lines.append(l)
				continue

	def set_txt(self,txt):
		if not txt: return False
		txt = txt.replace("\t"," ")
		lines 				= list(txt.splitlines())
		self.filter_lines(lines)
		self.txt 			= "\n".join(self.lines)
		self.txt_o			= self.txt[:]
		self.txt_o_len		= len(self.txt_o)
		return 1

	def str_com(self):

		count = 0
		start_index = 0
		ar = []
		for needle,value,la in zoek_ar:
			index = self.txt.find(needle)
			while index != -1:
				ar.append((index,value))
				index = self.txt.find(needle,index+la)
		ar.sort()
		inum = 0
		lar = len(ar)
		larminone = lar - 1
		temp_ar = []
		last_stop = 0
		self.replaced = []
		while inum < lar:
			start_inum = inum
			start_index,val = ar[inum]
			if val == is_scope:
				
				if (not start_index) or self.txt[start_index - 1:start_index] == "\n":
					stop = self.txt.find("\n",start_index)
					if stop == -1: stop = len(self.txt)
					self.pre_defines.append(self.txt[start_index:stop])
					start = start_index
					self.replaced.append((start,stop,0))
					if start != last_stop:
						temp_ar.append(self.txt[last_stop:start])
					last_stop = stop
				elif ignore_scope:
					inum += 1
				else:
					print(start_index)
					stop = self.txt.find("\n",start_index)
					if stop == -1: stop = len(self.txt)
					print(self.txt[start_index:stop])
					print(self.fp)
					exit()
					

			elif val in is_string:
				inum += 1
				string_val = val
				string_found = 0
				while inum < larminone:
					if (ar[inum][1] != string_val):
						inum += 1
					elif (ar[inum + 1][1] == string_val) and (ar[inum + 1][0] == (ar[inum][0] + 1)):
						inum += 2
					else:
						string_found = ar[inum][0]
						break
				if (not string_found) and (inum < lar) and (ar[inum][1] == string_val):
					string_found = ar[inum][0]
				if string_found and self.txt[string_found + 1:string_found + 3] in string_appenders:
					string_found += 2
					while self.txt[string_found+1] in str_numbers:
						string_found += 1
				if not string_found:
					self.add_error_at_pos("do_str_c_pre : not string_found",start_index,func='add_all_strings')
					string_found = start_index
					inum = start_inum
				start = start_index
				stop = string_found + 1
				if start != last_stop:
					temp_ar.append(self.txt[last_stop:start])
				temp_ar.append(replace_with)
				self.replaced.append((start,stop,replace_with_len))
				last_stop = stop
			elif val in is_include:
				count = val
				inum += 1
				found = 0
				while inum < lar:
					index,val = ar[inum]
					if val in is_include:
						count += val
						if count < 0: print("Error !")
						if not count:
							start = start_index
							stop = index + 1
							if start != last_stop:
								temp_ar.append(self.txt[last_stop:start])
							temp_ar.append(replace_with)
							self.replaced.append((start,stop,replace_with_len))
							last_stop = stop
							found = 1
							break
					inum += 1
				if not found:
					self.add_error_at_pos("do_str_c_pre : is_include not found! started at line ",start_index)
			elif val in is_comment:
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
							start = start_index
							stop = index + 2
							self.replaced.append((start,stop,0))
							if start != last_stop:
								temp_ar.append(self.txt[last_stop:start])
							last_stop = stop
							found_comment = 1
							break
						last_index_plus_one = index + 1
					inum += 1
				if not found_comment:
					self.add_error_at_pos("do_str_c_pre : is_comment not found_comment! started at line ",start_index)
					
			while inum < lar and (ar[inum][0] < last_stop):
				inum += 1
			
			
		temp_ar.append(self.txt[last_stop:])
		self.txt = "".join(temp_ar)

	def make_replaced_two(self):
		self.replaced.sort()
		nr = []
		last_stop = -1
		last_start = -1
		for start,stop,l in self.replaced:
			if last_start < start < last_stop:
				last_stop = max(last_stop,stop)
				nr[-1] = (last_start,last_stop,1)
			else:
				nr.append((start,stop,l))
				last_stop = stop
				last_start = start
		self.replaced = nr

	def make_replaced(self):
		self.replaced.sort()
		nr = []
		last_stop = -1
		last_start = -1
		for start,stop,l in self.replaced:
			if last_start < start < last_stop:
				last_stop = max(last_stop,stop)
				nr[-1] = (last_start,last_stop,1)
			else:
				nr.append((start,stop,l))
				last_stop = stop
				last_start = start
		self.replaced = nr
		self.replaced_helper = []
		n = 0
		for start,stop,l in self.replaced:
			lengte = stop - start - l
			self.replaced_helper.append((start - n,n))
			n += (stop - start) - l
		self.replaced_helper.append((self.txt_o_len + 10,n))

	def get_real_pos_add_ar(self,ar):
		iar = 0
		lar = len(ar)
		if not lar: return ar
		for start,n in self.replaced_helper:
			if start <= ar[iar][0]: continue
			while iar < lar and ar[iar][0] < start:
				ar[iar] = (ar[iar][0] + n,ar[iar][1] + n, ar[iar][2])
				iar += 1
			if iar == lar: break
		return ar

	def do_connected(self):
		temp_ar = []
		self.txt = self.txt.replace(':','.').replace("\n", " ")
		a = self.txt.rfind('.')
		next_dot = 0
		while a != -1:
			bluh = a
			if self.txt[a+1:a+2].strip():
				stop = self.txt.find(' ',a)
				if stop == -1:
					stop = len(self.txt)
				elif stop == next_dot + 1:
					stop -= 1
				bluh = self.txt.rfind(' ',0,a) + 1
				temp_ar.append((bluh,stop))
			next_dot = a
			a = self.txt.rfind('.',0,bluh-1)
		s_ar = []
		last_stop = 0
		other_ar = []
		temp_replaced = []
		for start,stop in reversed(temp_ar):
			if start != last_stop:
				s_ar.append(self.txt[last_stop:start])
			s_ar.append(replace_with)
			temp_replaced.append((start,stop,replace_with_len))
			last_stop = stop
		s_ar.append(self.txt[last_stop:])
		self.txt = "".join(s_ar)
		self.replaced = [a for a in self.replaced if a[2]] + self.get_real_pos_add_ar(temp_replaced)



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
		
		
	def test_replaced(self):
		if len(self.replaced) != self.replaced_good_index:
			self.write_error("test_replaced","\n".join([self.txt_o[start:stop] for start,stop,x in self.replaced]))
			self.errors.append("Count R = %d" % self.txt.count('R'))
			self.errors.append("len_replacers = %d" % len(self.replaced))
	
	def test(self):
		self.test_replaced()
		if not self.errors: return
		self.test_write()
		
		
		
	def test_write(self):
		if self.errors:
			with open("out\\" + self.name + "_errors.txt","w") as f:
				f.write("\n".join([self.fp] + self.errors))
		self.replaced.sort()
		original = self.txt
		for start,stop,l in self.replaced:
			if not l: continue
			original = original.replace('R',self.txt_o[start:stop],1)
			
		
		with open("out\\" + self.base,"w") as f:
			f.write(self.txt)
		self.write_error("original",original)
		self.write_error("txt_o",self.txt_o)
		
		