import os

class bashify:

	def __init__(self, name = None, lines = None, runNow = True):
		self.runNow = runNow
		if name != None and lines != None and runNow == True:
			self.printBashFile(name, lines)
			self.makeExecutable(name)
			self.runExecutable(name)
		if name != None:
			self.name = name
		if lines != None:
			self.lines = lines
			
		

	def printBashFile(self, name, lines):
		if self.runNow == False:
			n = self.name
			l = self.lines
		else:
			n = name
			l = lines

		with open("./" + n + ".sh", "w") as f:
			f.write("#!/bin/bash\n\n")
			for i in range(len(l)):
				f.write(l[i] + "\n")

	def makeExecutable(self, name):
		if self.runNow == False:
			n = self.name
		else:
			n = name

		os.system("chmod +x " + n + ".sh")

	def runExecutable(self, name = None):
		if self.runNow == False or name == None:
			n = self.name
		else:
			n = name
		return os.system("./" + n + ".sh")