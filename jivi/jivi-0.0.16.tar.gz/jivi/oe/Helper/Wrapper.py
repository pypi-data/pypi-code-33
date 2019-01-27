from time import time
import sys
from jivi.fs import *


class Wrapper:
	times = {}
	done_init = 0

	main_setter = File.all(File.fp("main_setter.py",File.dir(os.path.realpath(__file__))))
	
	def error(self,s):
		self.has_error = 1
		try:
			self.before_error()
		except:
			pass
		print(String.minlen(self.name,30) + ' ' + str(s))
	
	def info(self,s):

		print(String.minlen(self.name,20) + String.minlen('info',10) + ' ' + str(s))

	def do(self,todo=0,allinfo=0):
		todo = self.todo if not todo else todo
		mainclass = type(self).mro()[:-1][0]
		if not hasattr(mainclass,"helpertimes"):
			mainclass.helperstarted = time()
			mainclass.helpertimes = {}
		for do in todo:
			if not do in mainclass.helpertimes:
				mainclass.helpertimes[do] = []
		for do in todo:
			ss = time()
			if allinfo:
				self.info("Doing {do}".format(do=do))
			
			if (getattr(self,do)() == False):
				self.error("failed to do {do}".format(do=do))
				return 0
			mainclass.helpertimes[do].append(time() - ss)
			
		if allinfo:
			Wrapper.print_times(mainclass)
		return 1
	
	@staticmethod
	def print_times(mainclass):
		print("\n\n")
		print("printing times for " + mainclass.__name__)
		for k,ar in mainclass.helpertimes.items():
			tsum = sum(ar) * 10000
			tsum = int(tsum)
			t = int(tsum / len(ar))
			tsum = str(tsum)
			t = str(t)
			t = t + (10 - len(t))*" "
			tsum = tsum + (10 - len(tsum))*" "
			
	
			k = k + (50 - len(k))*" "	
			print("{k}  {tsum} {t}".format(k=k,tsum=tsum,t=t))
			
		print(time() - mainclass.helperstarted)
		print("\n\n")