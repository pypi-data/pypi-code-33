"""
企查查的爬虫
"""
import os
import re
import time
import json
import requests
from lxml import etree
from tqdm import tqdm
import pymongo
import wcc
import random
import jsonfiler
import pmt
from bs4 import BeautifulSoup
import traceback
import comcom
from tqdm import tqdm
import bson
from bson import ObjectId
def thread_main(thread_id, thread_jobs, thread_params, thread_results):
    col_combasic = thread_params["col_combasic"]
    col_firmkeys = thread_params["col_firmkeys"]
    insert_count = 0
    update_count = 0
    ignore_count = 0
    except_count = 0
    loop_count = thread_params["loop_count"]
    for loopc in range(loop_count+1):
        try:
            cur_time = int(time.time())
            dbrow = col_firmkeys.find_one_and_update({"basic":0}, {"$set":{"basic":cur_time}})
            if not dbrow:
                print("found none urls")
                break
            url = dbrow["url"]
            if ".shtml" in url:
                url = url.replace(".shtml",".html")
            
            cbase_url = url.replace("firm_","cbase_")
            if col_combasic.find_one({"url":cbase_url}):
                print("t"+str(thread_id)+" "+cbase_url+" skip")
                continue
            item = None
            #如果url里出现firm_CN_这种情况,需要转换
            if "firm_" in url and len(url.split("_")) == 3:
                url = "https://www.qichacha.com/firm_" + url.split("_")[2]
            
            
            if re.findall("https://www.qichacha.com/gs_", url):
                pass
            elif "firm_CN_" in url:
                url = url.replace("firm_CN_","firm_")
            elif "firm_YN_" in url:
                url = url.replace("firm_YN_","firm_")
            elif "firm_" in url:
                url = url.replace("firm_","cbase_")
            elif "tax_view" in url:
                print("t"+str(thread_id)+" "+url+" ignore ")
                continue
            else:
                print("t"+str(thread_id)+" "+url+" bad ")
                continue
            #有些地址是https://www.qichacha.com/cbase_05866048402c2e792f7b305e75eb2740 这样的格式.必须规整成.html，否则在get_friminfo里面要读取公司串的那个正则就没法用.
            if ".html" not in url:
                url +=".html"
            """
            从url获取对应的信息，url可以参考：https://www.qichacha.com/firm_8c9f7ddc1a7bcee3d1f7676773fe9404.html
            """
            try:
                resp_text = getpage(url,max_try=30)
                if resp_text is None:
                    return None
            except Exception as err:
                return None
            item = None
            if "gs_" in url:
                item = get_gsinfo(url,resp_text)
            elif "cbase_" in url:
                if "社会组织类型" in resp_text and "法人/负责人" in resp_text:
                    item = get_orginfo(url,resp_text)
                else:
                    item = get_firminfo(url,resp_text)
            if item:
                if comcom.is_combasic(item):
                    thread_results["done_urls"].append(url)
                    thread_results["combasic"].append(item)
                    addinfo = comcom.add_combasic([item])
                    try:
                        thread_results["addinfo"]["insert"]+=addinfo[0]
                        thread_results["addinfo"]["update"]+=addinfo[1]
                        thread_results["addinfo"]["ignore"]+=addinfo[2]
                        thread_results["addinfo"]["except"]+=addinfo[3]
                    except Exception as err:
                        print(err)
                    print("t"+str(thread_id)+" "+url+" ok "+str(addinfo))
                else:
                    print("t"+str(thread_id)+" "+url+" badformat")
            else:
                thread_results["error_urls"].append(url)
                print("t"+str(thread_id)+" "+url+" error")
        except Exception as err:
            thread_results["error_urls"].append(url)
            print(traceback.format_exc())
            print(err)
            continue

def main():
    """
    获取数据库连接
    """
    env_dict = os.environ
    col_firmkeys = None
    col_firmurls = None
    try:
        mongo_data_uri = env_dict["MONGO_DAT_URI"]
        client = pymongo.MongoClient(mongo_data_uri)
        db = client["comdb"]
        col_firmkeys = db["firmkeys"]
        col_firmurls = db["firmkeys"]
    except Exception as err:
        print(err)
        return None
    insert_count = 0
    update_count = 0
    ignore_count = 0
    except_count = 0
    count = col_firmurls.estimated_document_count()
    FETCH_LIMIT = 1000
    loop_count = int(count/FETCH_LIMIT)+1
    cur_id = ObjectId("1c2f5f639dc6d6443dc5adf3")
    for loopc in tqdm(range(loop_count)):
        try:
            dbrow = col_firmurls.find({"_id":{"$gt":cur_id},"url":{"$regex":"http"}}).limit(FETCH_LIMIT).sort("_id",1)
            if not dbrow:
                print("dbrow doc over")
                break
            if list(dbrow) == []:
                print("dbrow doc over")
                break
            for dbdoc in dbrow:
                cur_id = dbdoc["_id"]
                firmurl = dbdoc["url"]
                #https://www.qichacha.com/firm_495caf95354838e68d3b526955083da4.html 
                if len(firmurl) != len("495caf95354838e68d3b526955083da4"):
                    firmkey = firmurl.split("_")[-1].split(".")[0]
                    dbdoc["url"] = firmkey
                    update_count +=1
                    if col_firmurls.find_one({"url":firmkey}):
                        col_firmurls.delete_one({"_id":cur_id})
                        print(str(update_count)+":"+firmurl+"-> deleted")
                    else:
                        col_firmurls.update({"_id":cur_id},{"$set":{"url":firmkey}})
                        print(str(update_count)+":"+firmurl+"->"+firmkey)
                else:
                    ignore_count +=1
        except Exception as err:
            print(traceback.format_exc())
            print(err)
            continue
    print((insert_count,update_count,ignore_count,except_count))

    timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    print(timestr+" over") 

if __name__ == "__main__":
    main()
