""" Function to print recursive lists """
def printList(myList):
	""" Check if is a list and recurse on the list """
	if isinstance(myList, list):
		for each_entry in myList:
			if isinstance(each_entry, list):
				printList(each_entry)
			else:
				print(each_entry);
	else :
		print (myList);
