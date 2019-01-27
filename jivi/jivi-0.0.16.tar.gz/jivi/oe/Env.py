from jivi.oe.Imports import *
exec(Wrapper.main_setter)

import configparser,os,win32com.client,datetime
from jivi.oe.Compiler import Compiler
from jivi.oe.Session import Session


shortcut_link = r"C:\Users\jorisv\Desktop\Intex_links\local\MEC.lnk"






class Env(Wrapper):
	name = "Env"
	todo = ['read_link','set_arg','set_sections']
	file_types=['ininame','pf']
	sections=['Startup','Colors','fonts']
	reload = Data(
					env = 0
				)

	def __init__(self,pMAIN,link=shortcut_link):
		set_main(pMAIN)


		
		FP.p_database_structure = File.fp('p_database_structure.p',FP.static)
		self.all_files = {}
		self.link = File.fp(link)
		self.global_scopes = {}
		self.do(allinfo=0)
		self.info('loaded')

	def read_link(self):
		shell = win32com.client.Dispatch("WScript.Shell")
		self.shortcut = shell.CreateShortCut(self.link)
		self.path = self.shortcut.Targetpath
		self.wd = self.shortcut.WorkingDirectory
		return 1

	def set_arg(self):
		self.arg = {}
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

	def set_sections(self):
		self.propath = []
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

	def fp_dir(self,fp):
		if not os.path.isdir(fp):
			fp = os.path.join(self.wd,fp)
		if not os.path.isdir(fp):
			return 0
		return os.path.abspath(fp).rstrip(os.sep) + os.sep
	def run_reload_env(self):
		new_args = {k : v for k,v in self.arg.items()}
		new_args['p'] = FP.p_database_structure
		new_args['T'] = FP.temp
		new_args = ["-{k} {v}".format(k=k,v=v) for k,v in new_args.items()]
		
		os.system("{path} {new_args}".format(path=self.path,new_args=" ".join(new_args)))
		
	def load_tabs(self):
		files = [(name,FP.temp + name + ".json") for name in ['ttField','ttIndex','ttIndexField','ttFile','ttFont','ttSession']]
		self.tabs = {}
		for name,fp in files:
			t = File.joread(fp)
			if t == None: return None
			self.tabs[name[2:].lower()] = t
			
		return 1
	def load_env(self):
		if not self.reload.env:
			if self.load_tabs(): return 1
		self.run_reload_env()
		return self.load_tabs()


		