"""This is print nested list function"""
def printList(the_list):
	for item in the_list:
		if isinstance(item,list):
			printList(item)
		else:
			print(item)
