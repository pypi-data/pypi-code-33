# -*- coding:utf-8 -*-
import os,re

data = []
def find_chinese():
    count = 0
    with open (os.path.join('../','data_path','demo1.txt'),'r') as fb:
        content=fb.readline()
        if re.match(r'(.*[\u4E00-\u9FA5]+)|([\u4E00-\u9FA5]+.*)',):
            data.append(content)
            count += 1

        if not content:
            return count


if __name__ =='__main__':
    count=find_chinese()
    print(data)