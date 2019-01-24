"""Module to process a list at different levels as well as indent the list values (optional)"""
def process_list(the_list, level = 0):
    for item in the_list:
        if isinstance(item, list):
            process_list(item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(item)

