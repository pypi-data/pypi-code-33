#抓取
import requests
import re

def getxiciip(maxpage):
    '''
    获取西刺代理的ip
    :param maxpage:获取的最大页面数,一页100个ip
    :return: iplist,ip列表
    '''
    iplist=[]
    page=1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }
    ipstr="\d+\.\d+\.\d+\.\d+"
    poststr="<td>\d+</td>"
    while page<=maxpage:
        url = "http://www.xicidaili.com/wn/%d" % page
        r = requests.get(url=url, headers=headers)
        ip=re.findall(ipstr,r.text)     #ip是只含ip不含端口的列表
        port=re.findall(poststr,r.text) #port是形如<td>8000</td>的端口列表
        realport=[]                     #真正存放ip的列表
        for i in port:
            realport.append(i[4:-5])
        for i in range(len(realport)):
            iplist.append(ip[i]+":"+realport[i])
        page+=1
    print("西刺代理提取完毕")
    return iplist