from jivi.fs import *
from os import system
from time import time
from jivi.oe.constants import *
from jivi.oe.Reader import Reader

"""
	proc
	func
	vars
	mainblock
	
	widget
		...
		trigger
		
	



"""

zoek_ar = [(a,b,len(a)) for a,b in [('/*',1),('*/',-1),('"',2),("'",3),('{',5),('}',-5),('&glob',4),('&scop',4)]]
is_string = {3 : 1,2 : 1}
is_comment = {1 : 1, -1 : 1}
is_include = {5 : 1, -5 : 1}
is_scope = 4

replace_with = ' R'
replace_with_len = len(replace_with)
str_numbers = {str(i) : 1 for i in range(10)}
string_appenders = {':%s' % k : 1 for k in 'r,l,c,t,u'.split(',')}
class Filereader:
	functions = ['set_txt','strip_string_comment','write_all']
	
	def __init__(self,fp,env=0):
		self.errors = []
		self.base = File.base(fp)

		self.env = env

			
			

		
		
		self.fp = File.fp(fp)
		self.replaced = []
		self.txt = ""
		self.original = ""
		self.pre_defines = []
		for a in self.functions:
			if not getattr(self,a)():
				self.add_error('failed ' + a)
				break
		
	def set_write_fp(self):
		if self.env:
			pass
		else:
			self.fp_error = Dir.create("fre") + self.base
			self.fp_out = Dir.create("fro") + self.base
			
		File.delete(self.fp_error)
		File.delete(self.fp_out)
	def write_error(self):
		File.delete(self.fp_error)
		if not self.errors: return
		File.write(self.fp_error,"\n".join(self.errors))
		
	def write_all(self):
		self.set_write_fp()
		self.write_error()
		self.write_out()
		
	def write_out(self):
		
		File.write(self.fp_out,self.txt)
	
	def set_txt(self):
		self.txt = File.all(self.fp)
		if not self.txt: return False
		lines = []
		for line in self.txt.replace("\t"," ").splitlines():
			line = line.strip()
			linelow = line.lower()
			if linelow.startswith('&analyze'): continue
			lines.append(line)
			
		self.lines = []
		
		concat = 0
		for line in lines:
			old_concat = concat

			concat = line.endswith('~')
			if concat:
				line = line[:-1]
			
			if old_concat:
				self.lines[-1] += line
				continue
			
			self.lines.append(line)
			
		
				
				
				
		self.original = "\n".join(self.lines)
		self.txt = self.original[:]
		return 1

			
	def strip_string_comment(self):

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
					if string_found and self.txt[string_found + 1:string_found + 3].lower() in string_appenders:
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
			return 1
			

	def get_line(self,pos):
		return self.original.count("\n",0,pos)

	def add_error_at_pos(self,s,pos,*a,**b):
		l = self.get_line(pos)
		if l != None:
			return self.add_error(s + "\nat line {l}".format(l=l+1),*a,**b)
		return self.add_error(s + "\n at pos " + str(pos),*a,**b)



	def add_error(self,s,*a,**b):
		self.errors.append(s)
		
		
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