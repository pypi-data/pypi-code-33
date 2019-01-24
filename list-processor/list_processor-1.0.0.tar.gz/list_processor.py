"""Module to process a list at different levels as well as indent the list values (optional)"""
def process_list(the_list):
    for item in the_list:
        if isinstance(item, list):
            process_list(item)
        else:
            print(item)

