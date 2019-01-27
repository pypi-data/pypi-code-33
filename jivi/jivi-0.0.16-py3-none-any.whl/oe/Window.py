from jivi.oe import *
from jivi.fs import *
from jivi.oe.ArHelper import ArHelper
from jivi.oe.ArHelper import StatementReader as SR

from jivi.oe.Statement.definer import statement
from jivi.oe.Statement.Define.Field import Field

start_str = """
<html>
	<head>
		<script>if (typeof module === 'object') {window.module = module; module = undefined;}</script>
		<script type="text/javascript" src="src/js/jquery.js"></script>
		<script type="text/javascript" src="src/js/lib.js"></script>
		<script type="text/javascript" src="src/js/js.js"></script>
		<script type="text/javascript" src="src/js/prog.js"></script>
		<link rel="stylesheet" type="text/css" href="src/css/lib.css">
		<script>if (window.module) module = window.module;</script>
	</head>
	
	<body>
	"""
	
end_str = """</body></html>"""

class Window:
	steps = ['set_oeReader','set_window','set_defines','write']
	def __init__(self,env,fp):
		self.env = env
		self.fp = File.fp(fp).lower()
		self.window = {}
		self.frames = {}
		self.widgets = {}
		self.temptables = {}
		self.fp_out = "out\\" + File.name(self.fp) + ".html"
		if not File.exists(self.fp_out):
				
			for a in Window.steps:
				if not getattr(self,a)():
					print(self.fp)
					print('failed ' + a)
					break
		
	def write(self):
		for frame in self.frames.values():
			File.write(self.fp_out,start_str + frame.html() + end_str)
			break
		return 1
		
	def get_table(self,tn):
		if tn in self.temptables:
			return self.temptables[tn]
		return self.env.get_table(tn)
	
	def get_field_widget(self,tn,fn,noerror=0):
		table = self.get_table(tn)
		if not table:
			if noerror: return 0
			self.Error('table not found ' + tn)
			return 0
		return table.get_field(fn)
		
		
	def get_widget(self,oriname,noerror=0):


		name = oriname.lower().strip()
		if name in self.defines:
			return self.defines[name]
			
		ar = name.split('.')
		if len(ar) == 2:
			return self.get_field_widget(tn=ar[0],fn=ar[1],noerror=noerror)
		
		if noerror: return 0
		self.Error('widget not found ' + oriname)
		

	
	def set_defines(self):
		self.defines = {}
		self.frames = {}
		for a in self.commands:
			if not a: continue
			if Keyword(a[0]) == 'define':
				d = statement(a,self)
				if d.type == 'frame':
					if d.name in self.frames:
						self.frames[d.name].widget_ar += d.widget_ar
						self.frames[d.name].update(d.tab)
						
					else:
						self.frames[d.name] = d
				elif d.type == "temp-table":
					self.temptables[d.name.lower().strip()] = d
				elif d.name not in self.defines:
					self.defines[d.name] = d
					
				continue
				
		return 1
	def set_oeReader(self):
		self.oeReader = Stripper(self.fp)
		self.commands = self.oeReader.commands
		
			
		return 1
		
	def set_window(self):
		found = self.strip_command(['create','window'],1)
		if not found: return 0
		self.window_index = self.strip_command_last_found_index
		found = ArHelper.strip_until(found,'assign')
		if not found: return 0
		self.window = SR.assign(found)
		return self.window
			
	
	
			
	def strip_command(self,ar,fullblock=1):
		for i,c in enumerate(self.commands):
			for j,cl in enumerate(c):
				if cl == ar[0] and ArHelper.same(c[j:],ar):
					ret_val = c[j:]
					if fullblock:
						self.commands = self.commands[:i] + self.commands[i+1 :]
					else:
						self.commands[i] = self.commands[i][:j] + self.commands[i][j+len(ar):]
					self.strip_command_last_found_index = i
					return ret_val
		

	def Error(self,s):
		print('-----------------')
		print("Window [{name}] : {s}".format(name=self.fp,s=s))
		print('-----------------')