def print_item(items):
    for item in items:
        if isinstance(item,list):
            print_item(item)
        else:
            print(item)