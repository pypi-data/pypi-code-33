from jivi.fs import *

class Zoeker:
	def __init__(self,needles=[],files=[]):
		self.needles = needles
		self.files = files
		
		
	def start(self):
		self.needles = [s.lower() for s in self.needles]
		
		self.files_split = list(Ar.steps(self.files,50))
		self.todo = len(self.files_split)
		self.files_found = [{} for i in range(self.todo)]
		
		for i in range(self.todo):
			Thread(self.do,(i,))
			
		while self.todo:
			sleep(1)
			
		found = {}
		for a in self.files_found:
			found.update(a)
		self.files_found = sorted(list(found.keys()))
		
		self.stop()
		
		
	def stop(self):
		print("\n".join(self.files_found))
		
	def check_file(self,fp):
		s = File.all(fp)
		if not s: return 0
		s = s.lower()
		
		for n in self.needles:
			if s.find(n) != -1: return 1
		
			
	def do(self,i):
		for fp in self.files_split[i]:
			fp = File.fp(fp).lower()
			if self.check_file(fp):
				self.files_found[i][fp] = 1
			
		self.todo = self.todo - 1
		
		
	def scanDirs(self,dir,threads=20,**t):

		t['deep'] = 0
		t['full'] = 1
		
		def scanDir(i):
			for fp in self.dirs_to_scan[i]:
				fp = File.fp(fp).lower()
				
				self.files_found[i] += list(Dir.files(fp,**t))
				
			self.todo = self.todo - 1
		
		self.dirs_to_scan = list(Ar.steps(list(Dir.dirs(dir,full=1)),threads))
		self.todo = len(self.dirs_to_scan)
		self.files_found = [[] for i in range(self.todo)]
		
		for i in range(self.todo):
			Thread(scanDir,(i,))
			
		while self.todo:
			sleep(1)
			
		found = []
		for a in self.files_found:
			found += a
		self.files_found = sorted(list(set(found)))
		
	def zoek(self,needles=[]):
		
result = zoeker.zoek(needles=['incompleet'])