#针对企查查的爬虫代码.
import wcc
import requests
from bs4 import BeautifulSoup

def getjson_guquan(url,**kwargs):
    max_try = 10
    timeout = 30
    if "max_try" in kwargs:
        max_try = int(kwargs["max_try"])
    if "timeout" in kwargs:
        timeout = int(kwargs["timeout"])
    resp_json = None
    actual_try = 0
    for k in range(max_try):
        actual_try +=1
        try:
            resp_text = wcc.getpage(url, use_proxy=False,encoding="utf8",timeout=timeout,quiet=True)
            #下面注释的这个方式不对，会把里面双引号都便双引号,我们希望是下面的的方式会保留但双引号
            #resp_text = resp_text.encode('utf-8').decode('unicode-escape')
            #下面的这个方式才是正确的
            #resp_text = resp_text.decode('unicode-escape')
            #这样会留下单引号的字符串，单引号字符串,json.loads解析不了
            print(resp_text)
            resp_json = json.loads(resp_text)
        except Exception as err:
            pass
        if not resp_json:
            continue
        else:
            break
    return resp_json


def getpage(url,**kwargs):
    #先从oss看一下有没有
    """
    oss_url = ""
    if "https://www.qichacha.com" in url:
        oss_url = url.replace("https://www.qichacha.com","http://file.wikicivi.com/html")
    if "http://www.qichacha.com" in url:
        oss_url = url.replace("http://www.qichacha.com","http://file.wikicivi.com/html")
    if ".html" not in oss_url:
        oss_url = oss_url+".html"
    try:
        resp_text = getpage(oss_url,encoding="utf-8",quiet=True)
        if resp_text:
            #print(oss_url + " ok")
            return resp_text
    except Exception as err:
        pass
    """
    max_try = 10
    timeout = 30
    if "max_try" in kwargs:
        max_try = int(kwargs["max_try"])
    if "timeout" in kwargs:
        timeout = int(kwargs["timeout"])
    resp_text = None
    actual_try = 0
    for k in range(max_try):
        actual_try +=1
        try:
            resp_text = wcc.getpage(url, use_proxy='all', timeout=timeout,quiet=True)
        except Exception as err:
            pass
        if not resp_text:
            continue
        if resp_text.startswith("<script>window.location.href='https://www.qichacha.com/index_verify?"):
            continue
        elif resp_text.startswith("<script>window.location.href='http://www.qichacha.com/index_verify?"):
            continue
        #企查查我们还会查询tax_viw接口,在这个接口我们是直接获取json数据
        elif "tax_view" not in url:
            soup = BeautifulSoup(resp_text, "html.parser")
            title_text = soup.find("title").text
            if "503" in title_text:
                continue
            else:
                break
        else:
            break
    if resp_text:
        #print(url + " ok (" + str(actual_try)+"th)")
        pass
    else:
        pass
        #print(url + " error ("+ str(actual_try)+"th)")
    return resp_text

def main():
    url = "https://www.qichacha.com/gs_1473975991543754066"
    resp_html = getpage(url)
    print(resp_html)


if __name__ == "__main__":
    main()

