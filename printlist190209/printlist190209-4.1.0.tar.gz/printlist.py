import sys

"""
printlist模块，提供了一个名为printlist()的函数
这个函数的作用是显示列表，其中有可能包含（也可能不包含）嵌套列表。
"""

def printlist(isinstance_list,indent=False,level=0,flag=sys.stdout):
    """
    isinstance_list指向参数：可以指向任何python列表，也可以是包含嵌套列表的列表；
    indent缩进功能参数：由用户控制缩进功能是否开启
    level缩进控制参数：由用户控制每层嵌套列表Tab个数，缺省为0
    flag数据写入位置参数：用于标识数据写入的文件位置，缺省值sys.stdout,为print写入的默认位置，通常为屏幕
    所指定的列表中的每个数据项都会顺序显示在屏幕上，各数据项各占一行
    """
    for each_item in isinstance_list:
        if isinstance(each_item,list):
            printlist(each_item,indent,level+1,flag)
        else:
            if indent:
                """ for循环可以替代为print("\t"*level,end=' ') """
                for tab_stop in range(level):
                    print("\t",end='',file = flag)        #end=''作为print()BIF的一个参数会关闭其默认行为，即在输入中自动包含换行
            print(each_item,file = flag)
