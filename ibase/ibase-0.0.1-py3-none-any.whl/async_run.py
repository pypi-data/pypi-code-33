import threading
import subprocess
import time


# def run_comm(comm):
#     """执行comm"""
#     try:
#         p = subprocess.Popen(
#             comm,
#             stdin=subprocess.PIPE,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             shell=True,
#             # start_new_session=True
#         )
#         return p
#     except Exception as e:
#         print("执行失败：%s\n 命令：%s" % (e, comm))
#
#
# def haha(m):
#     comm = "C:\\Users\\wh\\.venv\\AutoCreateScript\\Scripts\\python.exe test_image.py %s" % m
#     p = run_comm(comm)
#     print("*" * 10, "start", "*" * 10)
#     for x in p.stdout.readlines():
#         print(x)
#     for y in p.stderr.readlines():
#         print(y)
#     return
#
# def one_by_one():
#     for x in range(20):
#         haha("abc")
#
# def haha_run():
#     startTime = time.time()
#     print("start:", time.ctime())
#     one_by_one()
#     endTime = time.time()
#     print("end:  ", time.ctime())
#     timeToken = "%.3f" %(endTime - startTime)
#     print(timeToken)
#
# # haha_run()
# #
# startTime = time.time()
# print("start:", time.ctime())
# for x in range(20):
#     t = threading.Thread(target=haha,args=("abc",))
#     t.start()
#     # t.join()
# print("current has %d threads" % (threading.activeCount() - 1))
# endTime = time.time()
# print("end:  ", time.ctime())
# timeToken = "%.3f" %(endTime - startTime)
# print(timeToken)

import requests
callback_url = 'http://192.168.225.225/testsystem/caseinfo/backinfo/19173/3893/13365.do'
# report  = {'interface_name': '这里是类描述', 'case_name': 'TestImage', 'case_url': '获取CASE失败', 'req_time': '2018-12-28 10:44:43', 'time_token': '208.452', 'http_status': None, 'head_ip': 'fe80::4087:f766:405e:28e6%7', 'result_status': '请求异常', 'content': None}
# res = requests.post(url=callback_url, data=report)
# print(res.status_code)
url = "http://www.baidu.com"
res = requests.get(url)
print(res.headers.get("Content-Type") == "application/json")
