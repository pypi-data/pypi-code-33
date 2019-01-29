from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ccc.marketing.campaigns.api.permissions import IsHigherUserOrOwnerOrReadOnly
from ccc.mixin import AuthParsersMixin
from ccc.users.api.serializers import UserModelSerializer, AddSubUserSerializer, ViewSubUserSerializer
from ccc.users.models import UserProfile


class UpdateAccount(UpdateAPIView, AuthParsersMixin):
    queryset = UserProfile.objects.all()
    serializer_class = UserModelSerializer


class UserViewSet(ModelViewSet, AuthParsersMixin):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticated, IsHigherUserOrOwnerOrReadOnly)
    serializer_class = UserModelSerializer

    """You can also get/add sub users through the 'api/users/sub/' endpoint, it carries an optional query param of ?user,
    if the query param is not supplied it performs the operation on the authenticated user"""

    @action(methods=['post', 'get'], detail=False, url_path='sub')
    def add_sub_user(self, request, **kwargs):
        pk = request.query_params.get('parent')
        if pk:
            user = get_object_or_404(UserProfile, pk=pk)
        else:
            user = request.user
        if request.method == 'GET':
            queryset = user.children.all()
            return Response(ViewSubUserSerializer(queryset, many=True).data, status=status.HTTP_200_OK)
        # Handle Post
        data = dict(request.data).copy()
        data.update({'is_active': False, 'parent': user.pk})
        serializer = AddSubUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
