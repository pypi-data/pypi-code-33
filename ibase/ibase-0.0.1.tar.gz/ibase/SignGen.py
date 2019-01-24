# coding=utf-8

import hashlib
from urllib.parse import urlparse, parse_qs, parse_qsl,urlencode
import string
import requests

class GenSignData():

    def __init__(self):
        self.carappkey = "@7U$aPOE@$"
        sign = ""
        # a = {"_appid":2, _timestamp=sdf, ask=3, cid=2, cname=d, conid=e, deviceid=2, isfirst=2, latitude=df, longitude=df, osver=sdf, pid=2, pm=1, pname=df, projectid=33, refer=d, source=23, userid=2, version=3}
        # sorted()

    # def get_sign_url(self, url):
    #     """
    #     {_appid=app.iphone, _timestamp=1531995896, ask=全景天窗。, cid=110100, cname=北京, conid=, deviceid=f7afe07726d41444b6c449175e14d018e90db0c2, isfirst=0, latitude=39.98532785602838, longitude=116.3187323094177, osver=0, pid=110000, pm=1, pname=北京, projectid=2, refer=, source=0, userid=0, version=9.3.5}
    #     :param url:
    #     :return: _sign
    #     """
    #     u = urlparse(url)
    #     q = parse_qsl(u.query, keep_blank_values=True)
    #     sort_q = sorted(q)
    #     join_q = ""
    #     for x, y in sort_q:
    #         if x == "_sign":
    #             pass
    #         else:
    #             join_q = join_q + x + y
    #     join_q = self.carappkey + join_q + self.carappkey
    #     _sign = self._encrypt_sign(join_q)
    #     new_q = parse_qs(u.query, keep_blank_values=True)
    #     new_q["_sign"] = [_sign]
    #     new_join_q = urlencode(new_q, doseq=True)
    #     print("new_jon_q", new_join_q)
    #     end_u = u._replace(query=new_join_q)
    #     return _sign, end_u.geturl()

    def get_params_sign(self, q):
        sort_q = sorted(q.items())
        join_q = ""
        for x, y in sort_q:
            if x == "_sign":
                pass
            else:
                join_q = join_q + str(x) + str(y)
        join_q = self.carappkey + join_q + self.carappkey
        m2 = hashlib.md5()
        m2.update(join_q.encode("utf-8"))
        sign_d = str(m2.hexdigest())
        _sign = sign_d.upper()
        q["_sign"] = _sign
        return q

    # def _get_sign_query(self, query):
    #     join_q = ""
    #     for x, y in query.items():
    #         join_q = join_q + str(x) + str(y)
    #     join_q = self.carappkey + join_q + self.carappkey
    #     return self._encrypt_sign(join_q)


    # def _encrypt_sign(self, querys):
    #     m2 = hashlib.md5()
    #     m2.update(querys.encode("utf-8"))
    #     sign_d = str(m2.hexdigest())
    #     return sign_d.upper()



if __name__ == '__main__':
    g = GenSignData()
    # url = "https://newsbj.app.autohome.com.cn/carhelper_v9.3.0/news/carhelper.ashx?userid=0&pm=2&source=3&thinktype=&ask=%E5%AE%9D%E6%9D%A5&pname=%E5%8C%97%E4%BA%AC&osver=0&cname=%E5%8C%97%E4%BA%AC&_timestamp=1532416054&latitude=39.98533139448861&projectid=2&conid=S4EVqiw0ss84oVtGm&version=9.5.0&refer=&cid=110100&deviceid=f7afe07726d41444b6c449175e14d018e90db0c2&isfirst=0&longitude=116.3187476653883&pid=110000&_appid=app"
    # _, new_url = g.get_sign_url(url)
    # print(_)
    # old_res = requests.get(url)
    # print("old_url:" ,old_res.json())
    # new_res = requests.get(new_url)
    # print("new_url:", new_res.json())
    # print(new_url)
    query = {'userid': '0', 'pm': '2', 'source': '3', 'thinktype': '', 'ask': '宝来', 'pname': '北京', 'osver': '0', 'cname': '北京', '_timestamp': '1532416054', 'latitude': '39.98533139448861', 'projectid': '2', 'conid': 'S4EVqiw0ss84oVtGm', 'version': '9.5.0', 'refer': '', 'cid': '110100', 'deviceid': 'f7afe07726d41444b6c449175e14d018e90db0c2', 'isfirst': '0', 'longitude': '116.3187476653883', 'pid': '110000', '_appid': 'app'}
    m = g.get_params_sign(query)
    r = requests.get(url="https://newsbj.app.autohome.com.cn/carhelper_v9.3.0/news/carhelper.ashx",
                 params=m)
    print(m)
    print(r.json())



