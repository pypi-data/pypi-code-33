'''This is an example funciton for trial.
It prints all netsted list.'''
import sys

def print_lol(the_list,indent=False,level=1,file=sys.stdout):
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,indent,level+1,file=file)
        else:
            if(indent):
                for i in range(level):
                    print("\t",end='',file=fn)
            print(item)
