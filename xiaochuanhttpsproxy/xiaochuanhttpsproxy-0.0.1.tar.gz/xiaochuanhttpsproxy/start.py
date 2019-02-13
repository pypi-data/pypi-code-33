#调用启动程序
import os

def start(page):
    '''
    :param page:抓取的页数
    :return:
    '''
    path=os.getcwd().split('\\')
    if 'xiaochuanhttpsproxy'==path[len(path)-1]:
        os.system("python enter.py %d"%page)