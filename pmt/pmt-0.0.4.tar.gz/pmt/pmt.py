#Wikicivi Crawler Client SDK
import os
import time
import datetime
import os,sys
import json
import re
import traceback
import threading

#创建thread_count个线程,均匀分担thread_jobs里的负载.
def domt(thread_func,max_threads,thread_jobs,thread_params,thread_result,main_thread_life = -1):
    THREAD_N = max_threads
    if max_threads > len(thread_jobs):
        THREAD_N = len(thread_jobs)
    try:
        time0 = int(time.time())
        thread_load_list = []
        for k in range(THREAD_N):
            thread_load_list.append({"tid":k%THREAD_N+1000,"jobs":[]})

        cur_K= 0
        for job in thread_jobs:
            thread_load_list[cur_K%THREAD_N]["jobs"].append(job)
            cur_K +=1

        threads = []
        for thread_load in thread_load_list:
            if len(thread_load["jobs"]) == 0:
                continue
            thread = threading.Thread(target=thread_func,args=(thread_load["tid"],thread_load["jobs"],thread_params,thread_result))    
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            cur_time = int(time.time())
            if main_thread_life > 0 and cur_time - time0 > main_thread_life:
                #如果主线程过了寿命,就要立刻全部退出.
                break
            thread.join()           #主线程等待 ta线程结束才继续执行
       
        time1 = int(time.time())
        return thread_result
    except Exception as err:
        print(traceback.format_exc())
        print(err)
        return []


def demo_thread_main(
        #第一个参数必须是整形的thread_id,
        thread_id,
        #第二个参数必须是一个list,list里面每个job的格式是main和thread_main之间约定好的
        thread_jobs,
        #第三个参数必须是dict,里面存放着main让thread_main之间传的参数,比如mongo数据库的句柄
        thread_params,
        #第四个参数必须是dict,main传给thread_main的结果数组,以备thread_main把结果写到这个数组里在最后让main总结
        thread_result):
    for job in thread_jobs:
        print("t"+str(thread_id)+"  "+job["name"]+" "+str(thread_params))
        thread_result["names"].append(job["name"])


def main():
    com_list = [
        {'name':'测试1_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试2_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试3_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试4_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试5_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试6_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试7_北京科技有限公司','tags':["tag1","tag2"]},
        {'name':'测试8_北京科技有限公司','tags':["tag1","tag2"]}
    ]
    #下面这个多线程调用的演示案例，用4个线程把com_list里的name都打印出来，并把所有name抽到一个list里
    THREAD_N = 4
    thread_result = domt(demo_thread_main,THREAD_N,com_list,{"线程参数1":"参数值1"},{"names":[]})
    print(thread_result)


if __name__ == '__main__':
    main()

