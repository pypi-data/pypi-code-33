import pieqt
import sys
def mad_import(modules):
	for module in modules:
		libs = [m[0] for m in filter(lambda a: type(a[1]) == type(module), module.__dict__.items())]
		for lib in libs:
			__import__(lib)
		generate_import_module(libs,module)
		generate_from_modules_import_all(libs)
		#return libs



def generate_import_module(libs,module):
	dic = module.__dict__.items()
	moduleNames = []
	roukzouk = []
	for key in dic:
		for lib in libs:
			print(key[1])
			if key[1]!=None and lib in str(key[1]) and 'from' not in str(key[1]):
				print(True)
				roukzouk.append(str(key[1]))
				# sys.exit()
			if key[1] != None:
				d=str(key[1])+'s'
			moduleNames.append(d)

	print('-'*100)
	import_line_text = ""
	for import_line in roukzouk:
		for lib in libs:
			import_line = import_line[import_line.find(lib):].rstrip("'>")
			print(import_line)
			import_line_text+="import "+import_line+"\n"
	with open("runtime_python_imports.py", "w") as runtime_python_imports:
		runtime_python_imports.write(import_line_text)

def generate_from_modules_import_all(libs):
	import_line_from_text = ""
	for lib in libs:
		import_line_from_text += "from "+lib+" import *\n"
	with open("runtime_python_imports_from.py", "w") as runtime_python_imports_from:
		runtime_python_imports_from.write(import_line_from_text)

# import importlib
# for module in moduleNames:
# 	if module not in {'__name__','__doc__','__package__','__loader__','__spec__','__file__','__cached__','__builtins__'}:
# 		importlib.import_module(module)
# print(QApplication)

mad_import([pieqt])