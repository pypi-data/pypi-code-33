from jivi.oe.Imports import *
exec(Wrapper.main_setter)


class Session(Wrapper):
	name = "Session"
	todo = ['load_available_char','load_all_files','load_all_files_tab','load_tables','set_replacers']
	
	reload = Data(
					available_chars = 0,
					all_files 		= 0,
					tables			= 0,
					all_files_tab 	= 0
				)
	def __init__(self,MAIN):
		set_main(MAIN)
		
		self.propath = ENV.propath
		
		self.available_chars = []
		FP.available_chars = FP.data + "available_chars.json"
		
		self.all_files = {}
		self.all_files_tab = {}
		FP.all_files = FP.data + "all_files.json"
		FP.all_files_tab = FP.data + "all_files_tab.json"
		FP.tables = FP.data + "tables.json"
		self.tables = {}
		
		self.do(allinfo=0)
		self.info('loaded')

		
		# self.load_t_f(tabs['file'],tabs['field'])
		
	def load_all_files_tab(self):
		if not self.reload.all_files_tab:
			self.all_files_tab = File.jread(FP.all_files_tab)
			
		if self.all_files_tab: return self.all_files_tab
		
		self.all_files_tab = {fp : (i + 1) for i,fp in enumerate(self.all_files)}
		File.jwrite(FP.all_files_tab,self.all_files_tab)
		return self.all_files_tab
	def load_all_files(self):
		if not self.reload.all_files:
			self.all_files = File.jread(FP.all_files)

		if self.all_files: return self.all_files
		t = {}
		for d in self.propath:
			for fp in Dir.files(d,ex=['w','i','p'],full=1,deep=1):
				t[fp.lower().strip()] = 1
		self.all_files = sorted(list(t.keys()))

		
		File.jwrite(FP.all_files,self.all_files)
		return self.all_files
	
	def set_replacers(self):
		for i,a in enumerate(CONSTANTS):
			exec("REPLACER.{a} = self.available_chars[{i}]".format(a=a,i=i))
	
	def load_available_char(self):
		if not self.reload.available_chars:
			self.available_chars = File.jread(FP.available_chars)
		if self.available_chars: return self.available_chars
		self.load_all_files()
		self.available_chars = []
		self.todo_files = list(Ar.steps(self.all_files,50))
		self.todo = len(self.todo_files)
		self.good_chars = []
		self.good_chars_response = []
		for i in range(255):
			if chr(i).lower() == chr(i).upper() and len(chr(i)) and (len(chr(i))) == len(chr(i).strip()):
				self.good_chars.append(chr(i))
				self.good_chars_response.append([1]*self.todo)
		for i in range(self.todo):
			Thread(self.set_available_chars_helper,(i,))
		while self.todo:
			sleep(0.01)
		self.todo = len(self.todo_files)
		for i,char in enumerate(self.good_chars):
			if sum(self.good_chars_response[i]) == self.todo:
				self.available_chars.append(char)
		File.jwrite(FP.available_chars,self.available_chars)
		return self.available_chars

	def set_available_chars_helper(self,i):
		for fp in self.todo_files[i]:
			x = File.all_full(fp)
			if x:
				for j,v in enumerate(self.good_chars):
					if not self.good_chars_response[j][i]: continue
					if x.find(self.good_chars[j]) != -1:
						self.good_chars_response[j][i] = 0
		self.todo -= 1
	

	def fp_compiled(self,fp,first_step=1):
		
		return (FP.compiled_first_step if first_step else FP.compiled) + "{i}.json".format(i=self.all_files_tab[fp])

	def fp_dir(self,fp):
		if not os.path.isdir(fp):
			fp = os.path.join(self.wd,fp)
		if not os.path.isdir(fp):
			return 0
		return os.path.abspath(fp).rstrip(os.sep) + os.sep
		
		

	def load_tables(self):
		if not self.reload.tables:
			self.tables = File.jread(FP.tables)
		if self.tables: return self.tables


		ENV.load_env()
		self.load_t_f(ENV.tabs['file'],ENV.tabs['field'])
		File.jwrite(FP.tables,self.tables)
		return self.tables
		
		
	
		
	def load_t_f(self,tables,fields):
		self.tables = {}
		trecids = {}
		for a in tables:
			name = a['_File-Name'].lower().strip()
			self.tables[name] = dict(tab=a,fields={})
			trecids[a['rrecid']] = name
			
		for field in fields:
			
			name = field['_Field-Name'].lower().strip()
			tablename = trecids[field['_File-recid']]
			self.tables[tablename]['fields'][name] = field
			
	def get_table(self,tn):
		tn = tn.lower()
		if tn in self.tables:
			return self.tables[tn]
		
	def get_field(self,tn,fn=0):
		if not fn:
			ar = tn.split('.')
			if len(ar) == 2:
				return self.get_field(*ar)
			return 0
		table = self.get_table(tn)
		if not table:
			return 0
		fn = fn.lower().strip()
		if fn in table['fields']:
			return table['fields'][fn]
			
	def fp(self,fp):
		if os.path.isfile(fp):
			return os.path.abspath(fp)
		for d in self.propath:
			x = os.path.join(d,fp)
			if os.path.isfile(x):
				return os.path.abspath(x)
		return 0