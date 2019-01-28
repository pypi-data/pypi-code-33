# 列表中嵌套列表
animal=["大猩猩",["老虎","狮子","雪豹","猫咪"],"猪","刺猬",[["长颈鹿","梅花鹿"],["企鹅","北极熊","海豹"]]]
'''
print("1.表中嵌套列表：",animal[1][3])
print(animal[4][1][2])
print(animal)


print("=================================第一层======================================")
for animal_a in animal:
    print(animal_a)
    
print("=================================第二层======================================")
for animal_a in animal:
    if(isinstance(animal_a,list)):    #判断animal_a是否为list类型
        for animal_b in animal_a:
            print(animal_b)
    else:
        print(animal_a)

print("=================================第三层======================================")
for animal_a in animal:
    if(isinstance(animal_a,list)):
        for animal_b in animal_a:
            if(isinstance(animal_b,list)):
                for animal_c in animal_b:
                    print(animal_c)
            else:
                print(animal_b)
    else:
        print(animal_a)
'''

###########################函数实现###########################################
def list_all(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            list_all(each_item)
        else:
            print(each_item)
            
        
    




