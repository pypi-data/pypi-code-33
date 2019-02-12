from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


try:
    from ..response import ApiResponse,ApiState
except:
    from ...rest.response import ApiResponse, ApiState



class ApiAuthView(viewsets.ViewSetMixin,ObtainAuthToken):

    Token = None
    @property
    def model(self):
        return self.Token.model


    def loginResponse(self,user,token):
        data = {'id':user.id}
        data['token'] = token
        return data

    def registResponse(self,user,token):
        return {'id': user.id, 'token': token}

    @action(methods=['post','options','get'], detail=False)
    def register(self, request):
        print("======DD",self.Token)
        if self.model is None:
            return ApiResponse(ApiState.exception, "login error: ApiAuthView can not be None (authModel inherit from User model class )", "")
        model = self.model
        try:
            #该处代码参照ObtainAuthToken
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=False)
            data = serializer.data

            username = data.get('username','')
            password = data.get('password','')
            if username == '':
                return ApiResponse(ApiState.failed, "请输入用户名", {})
            if password == '':
                return ApiResponse(ApiState.failed, "请输入有效的密码", {})
            print('-----001')

            us = model.objects.filter(username=data['username'])
            if us.count() > 0:
                print('-----002')

                return ApiResponse(ApiState.failed, '用户名已被注册', {})
            print('-----00-02021',model.objects.all())

            newObj = model.objects.create(username=username)
            print('-----model.objects-02021',model.objects)

            newObj.set_password(password)
            newObj.save()
            print('-----003')

            token, created = self.Token.objects.get_or_create(user=newObj)
            print('-----004')

            data = self.registResponse(newObj, token.key)
            return ApiResponse(ApiState.success, "注册成功", data)
        except Exception as e:
            raise APIException(e)


    @action(methods=['post','options','get'], detail=False)
    def login(self, request, *args, **kwargs):
        # 该处代码参照ObtainAuthToken
        # import time
        # time.sleep(1)

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return ApiResponse(ApiState.failed, "用户名或密码错误", {})

        if self.authModel is None:
            return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
        try:
            baseUser = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=baseUser)
            data = self.loginResponse(baseUser,token.key)

            return ApiResponse(ApiState.success, "登录成功", data)
        except Exception as e:
            return ApiResponse(ApiState.failed, "用户名或密码错误", {})





class UserAuthView(viewsets.ViewSetMixin,ObtainAuthToken):
    authModel = None


    def loginResponse(self,user,token):
        data = {'id':user.id}
        data['token'] = token
        return data

    def registResponse(self,user,token):
        return {'id': user.id, 'token': token}

    @action(methods=['post','options','get'], detail=False)
    def register(self, request):

        if self.authModel is None:
            return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
        model = self.authModel
        try:
            #该处代码参照ObtainAuthToken
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=False)
            data = serializer.data

            username = data.get('username','')
            password = data.get('password','')
            if username == '':
                return ApiResponse(ApiState.failed, "请输入用户名", {})
            if password == '':
                return ApiResponse(ApiState.failed, "请输入有效的密码", {})


            us = model.objects.filter(username=data['username'])
            if us.count() > 0:
                return ApiResponse(ApiState.failed, '用户名已被注册', {})

            newObj = model.objects.create(username=username)
            newObj.set_password(password)
            newObj.save()
            token, created = Token.objects.get_or_create(user=newObj)

            data = self.registResponse(newObj, token.key)

            return ApiResponse(ApiState.success, "注册成功", data)
        except Exception as e:
            raise APIException(e)


    @action(methods=['post','options','get'], detail=False)
    def login(self, request, *args, **kwargs):
        # 该处代码参照ObtainAuthToken
        # import time
        # time.sleep(1)

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return ApiResponse(ApiState.failed, "用户名或密码错误", {})

        if self.authModel is None:
            return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
        try:
            baseUser = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=baseUser)
            data = self.loginResponse(baseUser,token.key)

            return ApiResponse(ApiState.success, "登录成功", data)
        except Exception as e:
            return ApiResponse(ApiState.failed, "用户名或密码错误", {})


