#coding=utf-8
__author__ = 'zhuxietong'
from rest_framework.exceptions import APIException
import re
from rest_framework.decorators import list_route
from django.core.files.base import ContentFile
import datetime
import functools


import random, string
def GenString(length=10):
	numOfNum = random.randint(1,length-1)
	numOfLetter = length - numOfNum
	#选中numOfNum个数字
	slcNum = [random.choice(string.digits) for i in range(numOfNum)]
	#选中numOfLetter个字母
	slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
	#打乱这个组合
	slcChar = slcNum + slcLetter
	random.shuffle(slcChar)
	#生成密码
	genPwd = ''.join([i for i in slcChar])
	return genPwd


# n 是否必须参数 ， t 为参数转换类型  id 为正则检查id ,k 为返回的dict的key，model对象的属性对应

seller_login = {
    'username':{'n':True,'t':'str','id':'username'},
    'password':{'n':True,'t':'str'},
    'email':{'n':True,'t':'str'},
}

api_shop_create = {
    'tag':{},
    'area':{'k':'area_id'},
    'address':{},
    'street':{'n':False},
}

PARAM_CHECK = {
    'default':{'reg':r'','lost_info':'缺少参数','dis_match_info':"参数检查错误",'type':str},
    'username':{'reg':r'','lost_info':'缺少用户名','dis_match_info':"用户名格式不正确！",'type':str},
    'password':{'reg':r'','lost_info':'缺少密码','dis_match_info':"密码包含特殊字符！",'type':str},
    'address':{'reg':r'','lost_info':'缺少详细地址','dis_match_info':"地址内容检查无法通过",'type':str},
    'street':{'reg':r'','lost_info':'缺少街道地址','dis_match_info':"街道内容检查错误！",'type':str},
    'email':{'reg':r'','lost_info':'缺少邮箱','dis_match_info':"邮箱格式错误",'type':str},
    'token':{'reg':r'','lost_info':'缺少token','dis_match_info':"token 错误！",'type':str},
    'tag':{'reg':r'','lost_info':'缺少标签','dis_match_info':"标签内容验证失败",'type':str},
    'name':{'reg':r'','lost_info':'缺少名称','dis_match_info':"名称出错",'type':str},
    'mobile':{'reg':r'','lost_info':'缺少电话号码','dis_match_info':"电话号码错误",'type':str},
    'price':{'reg':r'','lost_info':'缺少价格参数','dis_match_info':"价格格式错误",'type':float},
    'description':{'reg':r'','lost_info':'缺少描述参数','dis_match_info':"描述验证失败",'type':str},

}



def __get_nil_info(check_id):
    item = PARAM_CHECK[check_id]
    return item['lost_info']
def __get_dismatch_info(check_id):
    item = PARAM_CHECK[check_id]
    return item['dis_match_info']

def __get_checkValue(check_id,value):
    item = PARAM_CHECK[check_id]
    reg = item['reg']
    if reg:
        matchObj = re.match(reg, value)
        if matchObj:
            return value
        else:
            raise APIException(__get_dismatch_info(check_id))

    return value

def __convert(raw,type):
    # print(type)
    if type==int:
        # print(int(raw))
        return int(raw)
    if type==float:
        return float(raw)
    return raw

def param_parser(request,checker):

    if not checker:
        return

    return_data = {}
    raw_data = request.GET
    if not raw_data:
        raw_data = request.POST
    if not raw_data:
        raw_data = request.data
    for key,dict in checker.items():
        check_id = key
        need = True
        p_type = 'str'
        p_key = key


        if 'id' in dict:
            check_id = dict['id']
        if not check_id in PARAM_CHECK:
            check_id = 'default'
        if 'n' in dict:
            need = dict['n']
        if 't' in dict:
            p_type = dict['t']
        if 'k' in dict:
            p_key = dict['k']
        if need:
            if not key in raw_data:
                print('11')
                raise APIException(__get_nil_info(check_id)+ "  '" + key + "'")
            else:

                print('12')
                value = raw_data[key]
                if value:
                    checkedV = __get_checkValue(check_id,value)
                    return_data[p_key] = __convert(checkedV,p_type)
                else:
                    print('13')
                    raise APIException(__get_nil_info(check_id))
        else:
            if key in raw_data:
                value = raw_data[key]
                if value:
                    checkedV = __get_checkValue(check_id,value)
                    return_data[p_key] = __convert(checkedV,p_type)
                else:
                    raise APIException(__get_nil_info(check_id))


        request.api_params = return_data
    # return (True,'ok',return_data)


def param_crawl(checker=None,keys=None,do_route=False):
    if not checker:
        keys = ['get'] if (keys is None) else keys
        if keys:
            checker = {}
            for key in keys:
                checker[key] = {}
    if do_route:
        def decrector(f):
            @functools.wraps(f)
            def fct(self, *args, **kwargs):
                param_parser(self.request,checker=checker)
                return f(self,*args, **kwargs)
            return fct
        return decrector
    else:
        def decrector(f):
            @functools.wraps(f)
            def fct(self, *args, **kwargs):
                param_parser(self.request,checker=checker)
                try:
                    return f(self,*args, **kwargs)
                except Exception as e:
                    pass
            return fct
        return decrector



def __image_load(request,IClass,fileKey,param):
    if request.method == 'POST':
        param_parser(request,param)
        object = IClass()
        save(object,request.api_params)

        try:
            file_content = ContentFile(request.FILES[fileKey].read())
            str = request.FILES[fileKey].name
            date = datetime.datetime.now()
            timeStr = date.strftime('%y%m%d%H%M%S')
            name = timeStr+GenString(length=15)
            filename = name + '.' + str.split('.')[-1]
            object.slug = name
            object.image.save(filename, file_content)
            request.param_image = object
        except Exception as e:
            raise APIException(e)

def load_image(IClass,fileKey,param):
    def decrector(f):
        @functools.wraps(f)
        def fct(self, *args, **kwargs):
            __image_load(self.request,IClass,fileKey,param)
            return f(self,*args, **kwargs)
        return fct
    return decrector

# def param_crawl(checker=None,keys=None,do_route=True):
#     if not checker:
#         keys = ['get'] if (keys is None) else keys
#         if keys:
#             checker = {}
#             for key in keys:
#                 checker[key] = {}
#     if do_route:
#             @list_route(methods=['get','post',])
#             def decrector(f):
#                 def fct(self,request, *args, **kwargs):
#                     print request
#                     param_parser(request,checker=checker)
#                     return f(self,request,*args, **kwargs)
#                 return fct
#             return decrector
#     else:
#             def decrector(f):
#                 def fct(self,request, *args, **kwargs):
#                     print request
#                     param_parser(request,checker=checker)
#                     return f(self,request,*args, **kwargs)
#                 return fct
#             return decrector

def save(obj,atrributes):
    for key,value in atrributes.items():
        if hasattr(obj,key):
            setattr(obj,key,value)


