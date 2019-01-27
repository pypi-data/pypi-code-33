import json,re,os,math,subprocess,sys
from time import time,sleep
from datetime import datetime,timedelta
from _thread import start_new_thread as Thread
from math import ceil


from datetime import datetime,timedelta

try:
	import pytz
	
except:
	pass



pabs = os.path.abspath
def print_keys(t):
	print("\n".join(list(t.keys())))
def pjoin(*args): return pabs(os.path.join(*args))

DEFAULT_ENCODING = 0
def Decode(b):
	for a in [DEFAULT_ENCODING] + ['cp1252','ascii','utf-8','latin-1']:
		try:
			s = b.decode(a)
			return s
		except:
			pass
	
def Popen(s):
	try:
		process = subprocess.Popen(s, stdout=subprocess.PIPE,shell=1)
		stdout, stderr = process.communicate()
		if stderr: print(stderr)
		
		stdout = Decode(stdout)
		for x in stdout.splitlines():
			yield x.strip()
	except:
		pass
	

DEFAULT_ENCODING = "cp850" #'cp' + list(Popen('chcp'))[0].split(' ')[-1]

def Command(cmd):
	process = subprocess.Popen(cmd, shell = True)
	stdout, stderr = process.communicate()
	

	
def Pause():
	os.system('pause')
	
	
def input_yes_no(question, default="yes"):
	valid = {"yes": True, "y": True, "ye": True,"no": False, "n": False}
	if default is None:
		prompt = " [y/n] "
	elif default == "yes":
		prompt = " [Y/n] "
	elif default == "no":
		prompt = " [y/N] "
	else:
		raise ValueError("invalid default answer: '%s'" % default)

	while True:
		sys.stdout.write(question + prompt)
		choice = input().lower()
		if default is not None and choice == '':
			return valid[default]
		elif choice in valid:
			return valid[choice]
		else:
			sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
							 
							 


class Data:
	_standard = {"__class__": 1, "__delattr__": 1, "__dict__": 1, "__dir__": 1, "__doc__": 1, "__eq__": 1, "__format__": 1, "__ge__": 1, "__getattribute__": 1, "__gt__": 1, "__hash__": 1, "__init__": 1, "__init_subclass__": 1, "__le__": 1, "__lt__": 1, "__module__": 1, "__ne__": 1, "__new__": 1, "__reduce__": 1, "__reduce_ex__": 1, "__repr__": 1, "__setattr__": 1, "__sizeof__": 1, "__str__": 1, "__subclasshook__": 1, "__weakref__": 1, "_set": 1, "_standard": 1, "items": 1}
	
	def __init__(self,**t):
		self._set(**t)
	def _set(self,**t):
		for a,b in t.items(): setattr(self,a,b)
	def items(self):
		for a in dir(self):
			if not a in self._standard:
				yield a,getattr(self,a)
				



class Time:
	breaks = 0
	def __init__(self,name=None,func=None,amount=1000):
		self.name = name + " - " if name else ""
		self.start = time()
		self.stop_time = 0
		if func:
			for i in range(amount):
				func()
			self.stop()
		
				
	def stop(self):
		self.stop_time = time()
		print(self.passed)
		
				
	def tussenstop(self,n=""):
		self.breaks += 1
		print(self.passed,"[%d %s]" % (self.breaks,n))
	
	
	@property
	def passed(self,x=""):
		d = self.stop_time if self.stop_time else time()
		d -= self.start
		return self.name + x + str(timedelta(seconds=d))


		



			
			
			
class Ar:
	@staticmethod
	def split(ar,c):
		for i in range(0, len(ar), c):
			yield ar[i:i + c]
	@staticmethod
	def steps(ar,steps=10):
		c = ceil(len(ar)/steps)
		if c == 0: return
		for i in range(0, len(ar), c):
			yield ar[i:i + c]
	
	@staticmethod
	def filter(ar,strip=1):
		for x in ar:
			x = str(x).strip()
			if x:
				yield x
		
		

def difx(A,B,C):

	a = A.__dict__
	b = B.__dict__
	c = C.__dict__
	
	dif = {}
	for x in b.keys():
		if not x in c:
			dif[x] = 1
	for x in a.keys():
		if x in dif:
			del dif[x]
		
	print("\n".join(list(dif.keys())))
			
		
def dif(A,B,C):

	a = A.__dict__
	b = B.__dict__
	c = C.__dict__
	
	dif = {}
	for x in c.keys():
		if x in b:
			dif[x] = 1
	for x in a.keys():
		if x in dif:
			del dif[x]
		
	print("\n".join(list(dif.keys())))
	
