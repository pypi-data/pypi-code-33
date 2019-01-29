
###########################函数实现###########################################
def list_all(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            list_all(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):   #使用level的值控制使用制表符的个数
                    print("\t",end="")    #每一层缩进显示一个TAB制表符
            print(each_item)
            
        




