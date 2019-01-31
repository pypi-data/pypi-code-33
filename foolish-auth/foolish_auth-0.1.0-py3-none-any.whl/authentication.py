# -*- coding: utf-8 -*-
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class FoolishAuthentication(BaseAuthentication):
    """
    只是简单的认可请求头中携带的用户信息，然后创建一个不保存的零时用户。
    此APP只能用于带有认证功能的API网关背后，用于简化系统内部的用户认证。
    """

    def authenticate(self, request):
        username = request.META.get('HTTP_FOOLISH_AUTH')
        print(username)
        if username is None:
            raise AuthenticationFailed

        user = User(username=username)

        return user, username
