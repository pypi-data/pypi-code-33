"""This is the nesterSpaceHolder.py module, and it contains a function called print_lol()
that prints each item contained in a nested list of any depth."""
def print_lol(l,t=0):
    """
    This function takes a list as an argument and cycles through each item in the list,
    calling itself on items in the list that are nested lists. All items contained in
    the lists are printed.
    A second argument called t is used to determine how many tab stops should be used
    based on an item's depth in the list nesting.
    """
    for i in l:
        if isinstance(i,list):
            print_lol(i,t+1)
        else:
            for tab_stop in range(t):
                print("\t", end='')
            print(i)
