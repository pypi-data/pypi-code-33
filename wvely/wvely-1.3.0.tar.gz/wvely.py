import sys

"""这是一个打印嵌套列表的函数  增加一个缺省值使level变成一个可变的参数"""
def print_item(items,level=0):
    """循环遍历每一个数据项，如果该数据项仍为列表，则继续调用该函数，否则输出该数据项"""
    for item in items:
        if isinstance(item,list):
            print_item(item,level+1)  #递归调用   python3默认递归深度不能超过100
        else:
            '''输出制表符'''
            for tab_step in range(level):
                print("\t",end='')
            print(item)

#解释器在sys.path搜索模块
print_item(sys.path)