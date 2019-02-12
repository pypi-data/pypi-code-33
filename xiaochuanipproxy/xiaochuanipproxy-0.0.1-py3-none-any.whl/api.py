import random

def getip():
    '''
    :return:返回一个提取文件中的随机ip
    '''
    iplist=[]
    with open("ip.txt") as f:
        iplist=f.readlines()
    r=random.randint(1,len(iplist)-1)
    return iplist[r].strip()
