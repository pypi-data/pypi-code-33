""" Function to print recursive lists """
def printList(myList, nested = False, level=0):
	""" Check if is a list and recurse on the list """
	if isinstance(myList, list):
		for each_entry in myList:
			if isinstance(each_entry, list):
				printList(each_entry, nested, level + 1)
			else:
				if nested:
					for each_level in range(level):
						print("\t", end='')
				print(each_entry)
	else :
		print (myList);
