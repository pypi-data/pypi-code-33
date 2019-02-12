"""  This is the “nesterZT.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""

def print_lol(the_list,level):
    """ This function takes a positional argument called “the_list", which is any
    Python list (of, possibly, nested lists). Each data item in the provided list
    is (recursively) printed to the screen on its own line. """
    for x in the_list:
        if isinstance(x, list):
            print_lol(x, level+1)
        else:
            for z in range(level):
                print("\t", end=' ')
            print(x)