def print_lol(the_list, indent=False, level=0):
    """ 有一个位置参数是the_list，可以是任何列表，第二个参数会插入制表符，默认为0."""
    for each_item in the_list:
        if isinstance(each_item, list):
            """判断the_list中的each_item是不是列表"""
            print_lol(each_item, indent, level+1)
            """递归，将each_item转化为the_list，此处应熟练"""
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
                print(each_item)
