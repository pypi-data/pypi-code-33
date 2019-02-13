from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


from ..response import ApiResponse,ApiState,ApiResp
from ..crawl import param_crawl




class ApiAuthView(viewsets.ViewSetMixin,ObtainAuthToken):

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            print('11100')
            username = kwargs.get(self.UserModel.USERNAME_FIELD)
            print('11100---1')

        try:
            user = self.UserModel._default_manager.get_by_natural_key(username)
        except self.UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            self.UserModel().set_password(password)
            raise APIException('用户名或密码错误')
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            else:
                return None

    Token = None
    @property
    def model(self):
        return self.Token.model

    @property
    def UserModel(self):
        return self.Token.model


    def loginResponse(self,user,token):
        data = {'id':user.id}
        data['token'] = token
        return data

    def registResponse(self,user,token):
        return {'id': user.id, 'token': token}

    @action(methods=['post','options','get'], detail=False)
    def register(self, request):
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

            us = model.objects.filter(username=data['username'])
            if us.count() > 0:
                return ApiResponse(ApiState.failed, '用户名已被注册', {})
            newObj = model.objects.create(username=username)
            newObj.set_password(password)
            newObj.save()
            token, created = self.Token.objects.get_or_create(user=newObj)
            data = self.registResponse(newObj, token.key)
            return ApiResponse(ApiState.success, "注册成功", data)
        except Exception as e:
            raise APIException(e)


    @action(methods=['post','options','get'], detail=False)
    @param_crawl(checker={
        'username': {'n': True},  # login | register
        'password': {'n': True},
    })
    def login(self, request, *args, **kwargs):
        # 该处代码参照ObtainAuthToken
        # import time
        # time.sleep(1)
        params = request.api_params

        user = self.authenticate(request,username=params.get('username',''),password=params.get('password',''))
        if user is None:
            return ApiResp(ApiState.failed, "用户名或密码错误", {})
        else:
            # token = self.Token.objects.get(user=user)
            try:
                token, created = self.Token.objects.get_or_create(user=user)
                data = self.loginResponse(user, token.key)
                return ApiResp(ApiState.success, "登录成功", data)
            except Exception as e:
                return ApiResp(ApiState.exception,'登录失败',data)



def AuthView(token):
    class FastAuthView(ApiAuthView):
        Token = token
    return FastAuthView

#
#
# class UserAuthView(viewsets.ViewSetMixin,ObtainAuthToken):
#     authModel = None
#
#
#     def loginResponse(self,user,token):
#         data = {'id':user.id}
#         data['token'] = token
#         return data
#
#     def registResponse(self,user,token):
#         return {'id': user.id, 'token': token}
#
#     @action(methods=['post','options','get'], detail=False)
#     def register(self, request):
#
#         if self.authModel is None:
#             return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
#         model = self.authModel
#         try:
#             #该处代码参照ObtainAuthToken
#             serializer = self.serializer_class(data=request.data,
#                                                context={'request': request})
#             serializer.is_valid(raise_exception=False)
#             data = serializer.data
#
#             username = data.get('username','')
#             password = data.get('password','')
#             if username == '':
#                 return ApiResponse(ApiState.failed, "请输入用户名", {})
#             if password == '':
#                 return ApiResponse(ApiState.failed, "请输入有效的密码", {})
#
#
#             us = model.objects.filter(username=data['username'])
#             if us.count() > 0:
#                 return ApiResponse(ApiState.failed, '用户名已被注册', {})
#
#             newObj = model.objects.create(username=username)
#             newObj.set_password(password)
#             newObj.save()
#             token, created = Token.objects.get_or_create(user=newObj)
#
#             data = self.registResponse(newObj, token.key)
#
#             return ApiResponse(ApiState.success, "注册成功", data)
#         except Exception as e:
#             raise APIException(e)
#
#
#     @action(methods=['post','options','get'], detail=False)
#     def login(self, request, *args, **kwargs):
#         # 该处代码参照ObtainAuthToken
#         # import time
#         # time.sleep(1)
#
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         try:
#             serializer.is_valid(raise_exception=True)
#         except Exception as e:
#             return ApiResponse(ApiState.failed, "用户名或密码错误", {})
#
#         if self.authModel is None:
#             return ApiResponse(ApiState.exception, "login error: TokenAuthView can not be None (authModel inherit from User model class )", "")
#         try:
#             baseUser = serializer.validated_data['user']
#             token, created = Token.objects.get_or_create(user=baseUser)
#             data = self.loginResponse(baseUser,token.key)
#
#             return ApiResponse(ApiState.success, "登录成功", data)
#         except Exception as e:
#             return ApiResponse(ApiState.failed, "用户名或密码错误", {})
#
#
