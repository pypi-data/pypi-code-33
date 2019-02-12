from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,HttpResponse
from django.views.decorators.csrf import csrf_exempt

from eeapp.jsonapi.crawl import param_crawl
from requests import Request,Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view,action

from eeapp.jsonapi.crawl import param_crawl
from eeapp.rest.response import ApiResponse,ApiState

from rest_framework import viewsets
from .models import WXUserAuth
#
# from ..models import AdminUser,MemberUser,WXUserAuth
# from .serializer import MemberAuthSimpleSerializer

from django.conf import settings



import requests

wx_merch_id = settings.WX_MERCHID
wx_merch_key = settings.WX_MERCHKEY
wx_app_id = settings.WX_APPID
wx_secret = settings.WX_APPSECRET

class WXAuthView(viewsets.GenericViewSet):
    authentication_classes = []
    permission_classes = []
    serializer_class = None
    user_model = None


    def get(self,request):
        return HttpResponse("false")


    @param_crawl(checker={
        'code': {'n': False},
        'refresh_token': {'n': False}
    })
    @action(detail=False, methods=['post', 'get'])
    def auth(self,request):
        code = request.api_params.get('code', '')
        refresh_token = request.api_params.get('refresh_token', '')
        print(request.api_params)

        if len(code) > 0:
            resp = self.get_openid(code)
            print("-----get open id")
            if resp['state'] == ApiState.success:

                a_token = resp['data']['access_token']
                o_id = resp['data']['openid']
                r_token = resp['data']['refresh_token']
                return self.get_userinfo(a_token,r_token,o_id)
            else:
                return ApiResponse(state=resp['state'],detail=resp['detail'],data=resp['data'])
        if len(refresh_token) > 0:
            resp = self.refresh_openid(refresh_token)

            if resp['state'] == ApiState.success:
                a_token = resp['data']['access_token']
                r_token = resp['data']['refresh_token']
                o_id = resp['data']['openid']


                return self.get_userinfo(a_token,r_token,o_id)
            else:
                return ApiResponse(state=resp['state'],detail=resp['detail'],data=resp['data'])
        return ApiResponse(state=ApiState.failed, detail='检查code 或 refresh_token', data='')





    def get_openid(self, code):
        url = 'https://api.weixin.qq.com/sns/oauth2/access_token'
        info = {
            'appid': wx_app_id,
            'secret': wx_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        respone = requests.get(url, params=info)
        status_code = respone.status_code
        if status_code == 200:
            info = respone.json()

            try:
                errcode = info.get('errcode', 0)
                if errcode == 0:
                    try:
                        openid = info['openid']
                        access_token = info['access_token']
                        refresh_token = info['refresh_token']
                        auth = WXUserAuth()
                        try:
                            auth = WXUserAuth.objects.get(openid=openid)
                        except WXUserAuth.DoesNotExist:
                            pass
                        auth.openid = openid
                        auth.access_token = access_token
                        auth.refresh_token = refresh_token
                        auth.save()
                        print('save auth refresh_token:', refresh_token)
                    except Exception as e:
                        pass
                    return {'state':ApiState.success, 'detail':'获取成功', 'data':info}
                else:
                    return {'state':ApiState.failed, 'detail':info.get('errmsg', ''), 'data':''}
            except Exception as e:
                return {'state':ApiState.failed, 'detail':e.__str__(), 'data':''}
        return {'state':ApiState.failed, 'detail':str(status_code), 'data':{}}




    def refresh_openid(self,refresh_token):

        url = 'https://api.weixin.qq.com/sns/oauth2/refresh_token'
        info = {
            'appid': wx_app_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        print("refresh_openid:",info);

        respone = requests.get(url, params=info)
        code = respone.status_code
        if code == 200:
            info = respone.json()
            try:
                errcode = info.get('errcode', 0)
                if errcode == 0:

                    try:
                        openid = info['openid']
                        access_token = info['access_token']
                        refresh_token = info['refresh_token']
                        auth = WXUserAuth()
                        try:
                            auth = WXUserAuth.objects.get(openid=openid)
                        except WXUserAuth.DoesNotExist:
                            pass
                        auth.openid = openid
                        auth.access_token = access_token
                        auth.refresh_token = refresh_token
                        auth.save()
                        print('save auth refresh_token:',refresh_token)
                    except Exception as e:
                        pass

                    return {'state':ApiState.success, 'detail':'获取成功', 'data':info}
                else:
                    return {'state':ApiState.failed, 'detail':info.get('errmsg', ''), 'data':''}
            except Exception as e:

                return {'state':ApiState.failed, 'detail':e.__str__(), 'data':''}
        return {'state':ApiState.failed, 'detail':str(code), 'data':{}}




    def get_userinfo(self, access_token,refresh_token, openid):
        url = 'https://api.weixin.qq.com/sns/userinfo'
        info = {
            'access_token': access_token,
            'openid': openid,
            'lang': 'zh_CN',
        }
        print("will get_userinfo:",info);

        auth = WXUserAuth()

        try:
            auth = WXUserAuth.objects.get(openid=openid)
        except WXUserAuth.DoesNotExist:
            pass
        auth.openid = openid


        auth.access_token = access_token

        respone = requests.get(url, params=info)

        respone.encoding = "utf-8"
        status_code = respone.status_code

        # info ="""
        # wx userinfo response:\n
        # code:%d\n
        # json:%s
        # """ % (status_code,respone.json())
        # print(info)


        if status_code == 200:
            info = respone.json()
            info['refresh_token'] = refresh_token
            try:

                errcode = info.get('errcode', 0)
                print("errcode:",errcode)
                if errcode == 0:
                    try:

                        user = self.user_model.objects.get(wx_open_id=openid);
                        print("user:", user.wx_open_id)

                        userinfo = self.get_serializer_class()(instance=user).data

                        userinfo['wx'] = info
                        user.nickname = info['nickname']
                        user.avatar = info['headimgurl']
                        user.save()
                        # print('auth user:',userinfo)
                        try:
                            auth.save()
                        except Exception as e:
                            print("auth save error",e)
                        return ApiResponse(state=ApiState.success, detail='获取成功', data=userinfo)
                    except self.user_model.DoesNotExist:
                        try:
                            user = self.user_model()
                            user.wx_open_id = openid
                            user.nickname = info['nickname']
                            user.avatar = info['headimgurl']
                            print("new user:", user)

                            user.save()

                            userinfo = self.get_serializer_class()(instance=user).data
                            userinfo['wx'] = info
                            userinfo['is_new_user'] = True

                            # print('auth new user:', userinfo)
                            try:
                                auth.save()
                            except Exception as e:
                                print("auth save error", e)

                            return ApiResponse(state=ApiState.success, detail='获取成功', data=userinfo)
                        except Exception as e:
                            ApiResponse(state=ApiState.failed, detail=e.__str__(), data='')
                else:

                    return ApiResponse(state=ApiState.failed, detail=info.get('errmsg', ''), data='')
            except Exception as e:
                return ApiResponse(state=ApiState.failed, detail=e.__str__(), data='')
        return ApiResponse(state=ApiState.failed, detail=str(status_code), data={})




