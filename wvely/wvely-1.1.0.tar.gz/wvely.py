'''这是一个用来输出嵌套列表的函数 '''
def print_item(items,level):
    '''遍历列表中的每一个数据项  如果有数据项是列表重新调用该函数  否则就输出该数据项'''
    for item in items:
        if isinstance(item,list):
            print_item(item,level+1)
        else:
            '''使用Level的值来控制使用多少个制表符'''
            for tab_step in range(level):
                print('\t',end='')
            print(item)