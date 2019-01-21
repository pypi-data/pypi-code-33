""" Function to print recursive lists """
def printList(myList, level):
	""" Check if is a list and recurse on the list """
	if isinstance(myList, list):
		for each_entry in myList:
			if isinstance(each_entry, list):
				printList(each_entry, level + 1)
			else:
                                for each_level in range(level):
                                        print("\t", end='')
				print(each_entry);
	else :
		print (myList);
