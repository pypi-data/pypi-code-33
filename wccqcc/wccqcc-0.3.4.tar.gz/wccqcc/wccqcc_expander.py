"""

"""
import wcc
from bs4 import BeautifulSoup
import json
import pymongo
from  pymongo import MongoClient
import time
import traceback
from tqdm import tqdm
import comcom
import pmt
import re
from bson import ObjectId
import os
import jsonfiler
from .getpage import getpage

def diva_has_firm(href):
    return href and re.compile("/firm_").search(href)
def diva_has_pl(href):
    return href and re.compile("/pl_").search(href)
def diva_has_product(href):
    return href and re.compile("/product_").search(href)
def diva_has_bs(href):
    return href and re.compile("/bs_").search(href)




def thread_main(thread_id,job_list,thread_param,thread_results):
    #打开数据连接
    mongo_client = thread_param["mongo_client"]
    com_list = []
    html_dict = []
    for job in job_list:
        expand_flag = False
        job_url = job["url"]
        job_name = job["name"]
        resp_text   = getpage(job_url,encoding="utf-8")
        try:
            if resp_text is None:
                print(job_url+" bad")
                continue                 
            soup    = BeautifulSoup(resp_text, "html.parser")
            divs_list = soup.find_all(href=diva_has_firm)
            tmp_com_list = []
            for diva in divs_list:
                expand_flag = True
                com_name = diva.text
                com_name = com_name.strip()
                com_url  = diva["href"]
                if com_url.endswith(".shtml"):
                    #静态展示网页,不能用
                    expand_flag = True
                    continue
                if "查看样例>" in com_name:
                    com_name = ""
                    expand_flag = True
                    continue
                #"/firm_4b371f9185985521a5a37fa4ec0afd1d"
                #"https://m.qichacha.com/firm_b6d4e73877b088a0bc52e5c729df6ab4.html"
                #"url": "http://service.weibo.com/share/share.php?title=企业内幕：你所不了解的上饶市腾龙网络科技有限公司 | 查企业，就上企查查！&url=http://www.qichacha.com/firm_03e13f3af034d9c763f94720d18e3d4e"
                #"url": "mailto:?subject=企业内幕：你所不了解的上饶市腾龙网络科技有限公司 | 查企业，就上企查查！&body=http://www.qichacha.com/firm_03e13f3af034d9c763f94720d18e3d4e"
                if com_url.startswith("/firm"):
                    com_url = "https://www.qichacha.com"+com_url
                com_url = com_url.replace("m.qichacha.com","www.qichacha.com")
                if "查企业，就上企查查！&url=http://www.qichacha.com" in com_url:
                    com_url = com_url.split("&url=")[1]
                if "查企业，就上企查查！&body=http://www.qichacha.com" in com_url:
                    com_url = com_url.split("&body=")[1]
                if com_url == job_url:
                    continue
                if com_name == "":com_name = "未知"
                tmp_com_list.append({"name":com_name,"url":com_url})
 
            firm_count = len(tmp_com_list)
            com_list.extend(tmp_com_list)
            tmp_com_list = []
            #寻找所有pl
            divs_list = soup.find_all(href=diva_has_pl)
            for diva in divs_list:
                expand_flag = True
                pl_name = diva.text.strip()
                if pl_name == "":pl_name = "未知"
                pl_url  = "https://www.qichacha.com/pl_"+diva["href"].split("/pl_")[-1]
                tmp_com_list.append({"name":pl_name,"url":pl_url})
            pl_count = len(tmp_com_list)
            com_list.extend(tmp_com_list)
            tmp_com_list = []

            #寻找所有product
            divs_list = soup.find_all(href=diva_has_product)
            for diva in divs_list:
                expand_flag = True
                product_name = diva.text.strip()
                if product_name == "":product_name = "未知"
                product_url  = "https://www.qichacha.com/product_"+diva["href"].split("/product_")[-1]
                tmp_com_list.append({"name":product_name,"url":product_url})
            product_count = len(tmp_com_list)
            com_list.extend(tmp_com_list)
            tmp_com_list = []


            #寻找所有的bs
            divs_list = soup.find_all(href=diva_has_bs)
            for diva in divs_list:
                expand_flag = True
                bs_name = diva.text.strip()
                if bs_name == "":bs_name = "未知"
                bs_url  = "https://www.qichacha.com/bs_"+diva["href"].split("/bs_")[-1]
                tmp_com_list.append({"name":bs_name,"url":bs_url})
            boss_count = len(tmp_com_list)
            com_list.extend(tmp_com_list)
            tmp_com_list = []
            mongo_client.comdb.qccurls.update_one({"url":job_url},{"$set":{"expand":1,"fmc":firm_count,"plc":pl_count,"bsc":boss_count,"ptc":product_count}})
            if expand_flag: 
                oss_url = job_url.replace("https://www.qichacha.com/","").replace(".html","")
                try:
                    wcc.uploadHtml(resp_text,url=oss_url)
                except Exception as err:
                    html_dict[oss_url]=resp_text
                    pass
            else:
                #print(job_url+" expand fail")
                pass
        except Exception as err:
            print(com_url+" "+str(err))
            continue

    time_str = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
    jsonfiler.dump(html_dict,"html/html_dict_"+time_str+".json",indent=4)
    thread_results["com_list"].extend(com_list)


def wccqcc_doexpand(THREAD_N,expand_type,expand_count):
    env_dict = os.environ
    mongo_data_uri = env_dict["MONGO_DAT_URI"]
    job_list = []
    client = pymongo.MongoClient(mongo_data_uri)
    result = client.comdb.qccurls.find({"type":expand_type,"expand":None}).limit(expand_count)
    job_list.extend(list(result))
    if job_list == []:
        print("no data found for "+expand_type)
        exit()
    thread_results = pmt.domt(thread_main,THREAD_N,job_list,{"mongo_client":client},{"com_list":[]})
    com_list = thread_results["com_list"]
    
    qcc_url_dict = {
        "firm":[],"bs":[],"product":[],"pl":[],"zone":[],"gs":[]        
    }
    new_com_list = []
    
    
    for com_item in com_list:
        if com_item["name"] == "":
            print(com_item)
            continue
        com_url = com_item["url"]
        new_com_item = {"name":com_item["name"],"url":com_item["url"]}
        if "firm_"      in  com_url:qcc_url_dict["firm"].append(new_com_item)
        if "bs_"        in  com_url:qcc_url_dict["bs"].append(new_com_item)
        if "product_"   in  com_url:qcc_url_dict["product"].append(new_com_item)
        if "pl_"        in  com_url:qcc_url_dict["pl"].append(new_com_item)
        if "gs_"        in  com_url:qcc_url_dict["gs"].append(new_com_item)
        if "zonecompany_" in  com_url:qcc_url_dict["zone"].append(new_com_item)
    
    time_str = time.strftime("%Y-%m-%d_%H%M%S", time.localtime())
    for k,v in qcc_url_dict.items():
        if v!=[]:
            result = comcom.add_qccurls(v)
        else:
            result = (0,0,0,0)
        print(time_str+" "+expand_type+"->"+k+" "+str(result)+"/"+str(expand_count))

    jsonfiler.dump(com_list,"data/com_list_"+time_str+".json",indent=4)

if __name__ == "__main__":
    FIRM_BATCH_N = 100
    PL_BATCH_N = 100
    GS_BATCH_N = 100
    PRODUCT_BATCH_N = 100
    BS_BATCH_N = 1000
    #do_expand("firm",FIRM_BATCH_N)
    #do_expand("gs",GS_BATCH_N)
    #do_expand("pl",PL_BATCH_N)
    wccqcc_doexpand(100,"bs",BS_BATCH_N)
    #do_expand("product",PRODUCT_BATCH_N)
