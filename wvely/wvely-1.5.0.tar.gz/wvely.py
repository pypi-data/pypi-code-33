import sys

"""这是一个打印嵌套列表的函数  为参数增加一个缺省值使其变成一个可选的参数"""
def print_item(items,indent = False,level=0):
    """循环遍历每一个数据项，如果该数据项仍为列表，则继续调用该函数，否则输出该数据项"""
    for item in items:
        if isinstance(item,list):
            print_item(item,indent,level+1)  #递归调用   python3默认递归深度不能超过100
        else:
            '''输出制表符   默认不打开缩进'''
            if indent:
                for tab_step in range(level):
                    print("\t",end='')   #end='' 关闭Print函数的自动换行
            print(item)

#解释器在sys.path搜索模块
#print_item(sys.path)