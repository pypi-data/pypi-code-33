#针对企查查的爬虫代码.
import wcc
import json
import random
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
    resp_text = ""
    actual_try = 0
    for k in range(max_try):
        actual_try +=1
        try:
            resp_text = wcc.getpage(url, use_proxy='all', encoding="utf8", timeout=timeout, quiet=True)
            #下面注释的这个方式不对，会把里面双引号都便双引号,我们希望是下面的的方式会保留但双引号
            #resp_text = resp_text.encode('utf-8').decode('unicode-escape')
            #下面的这个方式才是正确的
            #resp_text = resp_text.decode('unicode-escape')
            #这样会留下单引号的字符串，单引号字符串,json.loads解析不了
            # print(resp_text)
            #如果ip被封,resp_text仅仅回一个[],如果是小个体户,回一个none
            if resp_text == "[]":
                print("[]"+str(k))
                resp_json = None
                continue
            if resp_text == None:
                print("none resp_text")
                continue

            """
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
            <title>503错误页面</title>
            哎呀，网页君累坏了
            """
            if "<title>503错误页面</title>" in resp_text:
                print("503错误页面")
                continue 
            resp_json = json.loads(resp_text)
        except Exception as err:
            print(err)
            print(resp_text)
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
    quiet = True
    if "max_try" in kwargs:
        max_try = int(kwargs["max_try"])
    if "timeout" in kwargs:
        timeout = int(kwargs["timeout"])
    if "quiet" in kwargs:
        quiet = kwargs["quiet"]
 
    resp_text = None
    actual_try = 0
    for k in range(max_try):
        actual_try +=1
        try:
            use_proxy_rand = int(random.random()*100)%10
            if use_proxy_rand == 1:
                resp_text = wcc.getpage(url, use_proxy=False, timeout=timeout,quiet=True)
            else:
                resp_text = wcc.getpage(url, use_proxy='all', timeout=timeout,quiet=True)
        except Exception as err:
            if not quiet: print(str(k)+":"+str(err))
            pass
        if not resp_text:
            if not quiet: print(str(k)+":"+str(resp_text))
            continue
        if resp_text.startswith("<script>window.location.href='https://www.qichacha.com/index_verify?"):
            if not quiet: print(str(k)+":"+str(resp_text))
            resp_text = None
            continue
        elif resp_text.startswith("<script>window.location.href='http://www.qichacha.com/index_verify?"):
            if not quiet: print(str(k)+":"+str(resp_text))
            resp_text = None
            continue
        elif "<h1>504 Gateway Time-out</h1>" in resp_text:
            if not quiet: print(str(k)+":"+str(resp_text))
            resp_text = None
            continue
        #企查查我们还会查询tax_viw接口,在这个接口我们是直接获取json数据
        elif "tax_view" not in url:
            soup = BeautifulSoup(resp_text, "html.parser")
            title_text = soup.find("title").text
            if "503" in title_text:
                if not quiet: print(str(k)+":"+str(resp_text))
                resp_text = None
                continue
            else:
                break
            #<h1>504 Gateway Time-out</h1>
            if "504" in title_text:
                if not quiet: print(str(k)+":"+str(resp_text))
                resp_text = None
                continue
            else:
                break
        else:
            break
    if resp_text:
        if not quiet: print(url + " ok (" + str(actual_try)+"th)")
        pass
    else:
        pass
        if not quiet: print(url + " error ("+ str(actual_try)+"th)")
    return resp_text

def main():
    # url = "https://www.qichacha.com/gs_1473975991543754066"
    # resp_html = getpage(url)
    # print(resp_html)

    url = 'https://www.qichacha.com/cms_guquanmap3?keyNo=ddf362a127c95bdc33cead6773a46af8'
    getjson_guquan(url)


if __name__ == "__main__":
    main()

