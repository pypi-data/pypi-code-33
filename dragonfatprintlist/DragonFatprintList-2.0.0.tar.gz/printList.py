"""This is print nested list function"""
def printList(the_list,level=0):
	for item in the_list:
		if isinstance(item,list):
			printList(item,level+1)
		else:
                                                for tab_stop in range(level):
                                                        print("\t",end=' ')
			print(item)


			
