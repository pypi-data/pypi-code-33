from jivi.fs import *
import configparser
import os
import sys
import win32com.client
from jivi.oe.Table import Table,Field

def jread(fp,encoding='utf-8'):
	with open(fp,"r",encoding=encoding) as f:
		s = f.read()
		a = json.loads(s)
		return a
"""
wd
arg
propath
"""



shortcut_link = r"C:\Users\jorisv\Desktop\Intex_links\local\MEC.lnk"


class Environment:
	def __init__(self,fp=shortcut_link,file_types=['ininame','pf'],sections=['Startup','Colors','fonts'],temp_dir="C:\\temp\\"):
		self.file_types = file_types
		self.sections = sections
		self.temp_dir = temp_dir
		shell = win32com.client.Dispatch("WScript.Shell")
		self.shortcut = shell.CreateShortCut(fp)
		self.path = self.shortcut.Targetpath
		self.wd = self.shortcut.WorkingDirectory
		self.arg = {}
		self.propath = []
		self.set_arg()
		self.set_sections()
		self.set_fields_and_tables()
		self.set_files()

	def get_field(self,fn):
		fn = fn.lower()
		return self.fields[fn] if fn in self.fields else 0

	def get_table(self,fn):
		fn = fn.lower()
		return self.tables[fn] if fn in self.tables else 0

	def get_table_name(self,fn):
		fn = fn.lower()
		return fn if fn in self.tables else 0

	def get_field_widget(self,fn):
		return self.get_field(fn)

	def set_arg(self):
		arg = [a for a in [a.strip() for a in self.shortcut.Arguments.split(' ')] if a]
		meep = []
		key = 0
		for a in arg:
			if a.startswith('-'):
				if key:
					self.arg[key] = ' '.join(meep)
					meep = []
				key = a[1:]
			elif key:
				meep.append(a)
		if key:
			self.arg[key] = ' '.join(meep)
		for k,v in self.arg.items():
			if not hasattr(self,k):
				setattr(self,k,v)
		for a in self.file_types:
			if a in self.arg:
				if not os.path.isfile(self.arg[a]):
					self.arg[a] = os.path.join(self.wd,self.arg[a])

	def get_fp(self,rel_fp):
		rel_fp = rel_fp.lower().strip().replace("/","\\")
		return self.files_pp[rel_fp]

	def len_chars(self,s,font):
		if not font in self.font_lenght:
			print("Environment : font not found {font}".format(font=font))
			return 0
		font = self.font_lenght[font]
		l = 0
		for a in s:
			if not a in font:
				print("Environment len_chars {a} not found!".format(a=a))
				continue
			l += font[a][1]
		return l

	def len_pixels(self,s,font):
		if not font in self.font_lenght:
			print("Environment : font not found {font}".format(font=font))
			return 0
		font = self.font_lenght[font]
		l = 0
		for a in s:
			if not a in font:
				print("Environment get_length_pixels {a} not found!".format(a=a))
				continue
			l += font[a][0]
		return l

	def set_fields_and_tables(self):
		new_args = {k : v for k,v in self.arg.items()}
		new_args['p'] = r"C:\prog\jv\py\dbstruct.p"
		new_args = ["-{k} {v}".format(k=k,v=v) for k,v in new_args.items()]
		#os.system("{path} {new_args}".format(path=self.path,new_args=" ".join(new_args)))
		tabs = {}
		for a in ['ttField','ttIndex','ttIndexField','ttFile','ttFont']:
			tabs[a[2:].lower()] = jread(r"C:\temp\{a}.json".format(a=a))[a]
		self.fields = {}
		self.tables = {}
		self.indexes = {}
		file_by_recid = {}
		self.font_lenght = {}
		
		
		
		#fi cc cl pl
		for a in tabs['font']:
			fi = a['fi']
			cc = a['cc']
			
			pl = a['pl']
			if not fi in self.font_lenght:
				self.font_lenght[fi] = {}
			self.font_lenght[fi][cc] = [pl, pl / 7]

		def get_key(k,type):
			k = k.lstrip('_').replace('-','_').lower().strip()
			if k.startswith(type):
				k = k[len(type) + 1:]
			return k

		def check_tab(tab,required,defaults):
			for k,v in defaults.items():
				if not k in tab:
					tab[k] = v
			for a in required:
				if not a in tab: return 0
			return tab
		for t in tabs['file']:
			tab = {get_key(k,'file') : v for k,v in t.items()}
			tab = check_tab(tab,['rrecid','name'],{})
			if not tab: continue
			tab['name'] = tab['name'].lower()
			table = Table().from_json(tab)
			self.tables[table.name] = table
			file_by_recid[tab['rrecid']] = table
		for t in tabs['field']:
			tab = {get_key(k,'field') : v for k,v in t.items()}
			tab = check_tab(tab,['rrecid','name','file_recid'],dict(label=0,format=0))
			if not tab: continue
			if not 'name' in tab or (not tab['name']): continue
			tab['name'] = tab['name'].lower()
			table = file_by_recid[tab['file_recid']] if tab['file_recid'] in file_by_recid else 0
			if not table: continue
			tab['table'] = table
			field = Field().from_json(tab)
			self.fields[field.fullName] = tab
		
		
		
		
		
		self.alias_table = {}
		bad = {}
		
		for tablename,table in self.tables.items():
			table.create_alias_fields()
			for i in range(len(tablename) - 1,1,-1):
				tmp = tablename[:i]
				if tmp in self.alias_table:
					bad[tmp] = 1
					del self.alias_table[tmp]
				if tmp in bad: continue
				self.alias_table[tmp] = table
				
				
		
				
	def set_files(self):
		self.files = []
		tab = {}
		self.files_pp = {}
		for d in self.propath:
			for fp in Dir.files(d,ex=['w','p','i'],full=1,deep=1):
				fp = fp.lower()
				tab[fp] = 1
		for fp in tab.keys():
			pp = []
			for p in self.propath:
				if fp.startswith(p):
					file_pp = fp[len(p):]
					if not file_pp in self.files_pp:
						self.files_pp[file_pp] = fp
					pp.append(file_pp)
			self.files.append(dict(fp=fp,pp=pp,ex=File.ex(fp).lower()))

	def fp(self,fp):
		if os.path.isfile(fp):
			return os.path.abspath(fp)
		for d in self.propath:
			x = os.path.join(d,fp)
			if os.path.isfile(x):
				return os.path.abspath(x)
		return 0

	def fp_dir(self,fp):
		if not os.path.isdir(fp):
			fp = os.path.join(self.wd,fp)
		if not os.path.isdir(fp):
			return 0
		return os.path.abspath(fp).rstrip(os.sep) + os.sep

	def set_sections(self):
		config = configparser.ConfigParser(strict=0)
		config.read(self.arg['ininame'])
		for a in self.sections:
			t = {}
			sn = a.lower()
			if a in config:
				ca = config[a]
				for x in ca:
					t[x.lower()] = ca[x]
			setattr(self,sn,t)
		for a in self.startup['propath'].split(','):
			fp = self.fp_dir(a.strip())
			if fp:
				self.propath.append(fp.lower())
				
				
				
pixels_per_row = 26
pixels_per_col = 7
	
def htp(x,dontconv=0):
	try:
		f = float(x)
	except:
		return None
	if dontconv: return f
	return pixels_per_row * f
	
def wtp(x,dontconv=0):
	try:
		f = float(x)
	except:
		return None
	if dontconv: return f
	return pixels_per_col * f

def ctp(x,dontconv=0):
	try:
		f = float(x)
	except:
		return None
	if dontconv: return f
	return pixels_per_col * ( f - 1)

def rtp(x,dontconv=0):
	try:
		f = float(x)
	except:
		return None
	if dontconv: return f
	return pixels_per_row * ( f - 1)