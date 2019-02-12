#!/usr/bin/env python3
import shutil
import sys
import os
import math

def main():
	columns = shutil.get_terminal_size((80, 20)).columns

	if len(sys.argv) != 2:
		print("invalid number of arguments")
		exit(1)

	if not os.path.isfile('./'+sys.argv[1]):
		print(sys.argv[1]+" does not exist")
		exit(1)

	def print_ruler(f, l=columns, first=False):
		line1 = "----+----+"
		line2 = "    |    |"
		line4 = "---------+"

		print(("+" if first else "")+''.join([line1[(f-1+x)%10] for x in range(min(columns - (1 if first else 0),(10-((f-1)%10))+(math.ceil((l-(10-((f-1)%10)))/10)*10)))]))
		print(("|" if first else "")+''.join([line2[(f-1+x)%10] for x in range(min(columns - (1 if first else 0),(10-((f-1)%10))+(math.ceil((l-(10-((f-1)%10)))/10)*10)))]))
		line = ""
		for x in range(math.floor(min(columns-1, l)/10)):
			line+="{:>9}|".format(10*(math.floor(f/10)+x+1))
		if first:
			print("|"+line)#[:math.floor(((f-1)+(columns-1))/10)*10])
		else:
			print(("{:>9}".format(10*math.ceil(f/10)) if len(str(10*math.floor(f/10)))<=10-f%10 else " "*9)[(f)%10-1:]+"|"+line)#[:math.floor(((f-1)+(columns-1))/10)*10])
		print(("+" if first else "")+''.join([line4[(f-1+x)%10] for x in range(min(columns - (1 if first else 0),(10-((f-1)%10))+(math.ceil((l-(10-((f-1)%10)))/10)*10)))]))

		return f+min(columns - (1 if first else 0), l)


	value = 1
	first = True
	with open(sys.argv[1]) as f:
		print("Total byte count: "+str(os.path.getsize(sys.argv[1])))
		line = " "
		while True:
			c = f.read(1)
			if not c:
				print(line)
				value = print_ruler(value, len(line), first)
				first = False
				break
			if c == '\n':
				c = ' '

			line += c
			if len(line) == columns:
				print(line)
				value = print_ruler(value, len(line), first)
				first = False
				line = ""

if __name__ == "main":
	main()
