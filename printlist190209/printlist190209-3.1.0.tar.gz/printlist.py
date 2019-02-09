"""printlist模块，提供了一个名为printlist()的函数
这个函数的作用是显示列表，其中有可能包含（也可能不包含）嵌套列表。"""
def printlist(isinstance_list,level):
    """这个函数有一个位置参数，名为isinstance_list，这可以是任何python列表，也可以是包含嵌套列表的列表。
    所指定的列表中的每个数据项都会顺序显示在屏幕上，各数据项各占一行"""
    for each_item in isinstance_list:
        if isinstance(each_item,list):
            printlist(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)
