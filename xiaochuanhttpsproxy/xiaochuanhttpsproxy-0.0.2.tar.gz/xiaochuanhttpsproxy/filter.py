#多进程过滤
import requests
import multiprocessing
import os
from getip import getxiciip

lock=multiprocessing.RLock()
def filter(name,iplist):
    '''
    :param name: 进程名
    :param iplist: 分割后的iplist
    :param lock: 锁
    :return:
    '''
    url="https://www.baidu.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    for i in iplist:
        print("进程%d在进行第%d次筛选" % (name, iplist.index(i) + 1))        #提示信息
        proxies={
            "https":i
        }
        try:
            r=requests.get(url=url,headers=headers,proxies=proxies,timeout=2)
            r.encoding="utf-8"
            if r.status_code==200:
                lock.acquire()
                with open("ip.txt", "a+") as f:
                    f.write(i + "\n")
                lock.release()
        except Exception:
            continue
    print("进程%d已完成"%name)

def update(page):
    '''
    更新一次ip.txt
    :param page: 抓取的最大页面
    :return:
    '''
    iplist=getxiciip(page)                                                 #初始ip
    div_list=[iplist[i:i+10] for i in range(0, len(iplist), 10)]       #分割后列表，n*10
    process_length=len(div_list)                                        #总共进程数
    if os.path.exists("ip.txt"):                                        #判断iptxt存在
        os.remove("ip.txt")
    pool=multiprocessing.Pool(processes=4)                              #保持进程池内的进程为4
    for i in range(process_length):
        pool.apply_async(func=filter,args=(i,div_list[i],))               #进程加入进程池
    pool.close()
    pool.join()
    print("==================")
    print("ip提取完毕")
    print("===================")