# coding=utf-8 

import os
import re
import shutil

# 是否为图片
def isimage(filePath):
    ext = os.path.splitext(filePath)[1]
    return ext == '.png' or ext == '.jpg' or ext == '.jpeg' or ext == '.gif'

def filename(filePath, orgin_name):
    name = os.path.split(filePath)[1]
    # 搜索的图片名字有后缀，直接返回
    if orgin_name.endswith('.png'):
        return name
    # 把图片的后缀去掉
    name = name.replace('@2x.png', '')
    namev = name.replace('@3x.png', '')
    return name


def find_image(project_path, image_name, ressult):
    paths = os.listdir(project_path)
    for aCompent in paths:
        aPath = os.path.join(project_path, aCompent)
        ext = os.path.splitext(aPath)[1]
        if os.path.isdir(aPath):
            find_image(aPath, image_name, ressult)
        elif os.path.isfile(aPath) and isimage(aPath):
            if filename(aPath, image_name) == image_name:
                ressult.add(aPath)
                print("🔍 查找到一张图片在：%s"%(aPath))
                break 