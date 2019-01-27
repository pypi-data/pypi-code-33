from jivi.fs import *
x = File.jread(r'C:\tools\py64\Lib\site-packages\jivi\oe\File\replaced.txt')
print(x[403])
x = File.jread(r'C:\tools\py64\Lib\site-packages\jivi\oe\File\commands.txt')

ind = 0
for a in x:
	for c in a:
		if isinstance(c,int):
			if c != ind:
				print(c)
				exit()
			ind += 1