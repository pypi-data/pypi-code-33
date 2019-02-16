from rest_framework.viewsets import ViewSet,ModelViewSet
from rest_framework.decorators import action

from ..model.Images import ImageModel
from ..models import TestModel,OptionsModel

from .serializer import TestModelSerializer,OptionModelSerializer
from meapp.api.response import ApiState,ApiResponse,OnePagination



class ImageView(ViewSet):
    @action(methods=['post','options'], detail=False)
    def upload(self, request):
        try:
            img = ImageModel(image=request.FILES.get('file'))
            img.save()
            resp = ApiResponse(ApiState.success, "上传成功",img.url)
            return resp
        except Exception as e:
            return ApiResponse(ApiState.failed, "上传失败", '')






class OptionsView(ModelViewSet):
    serializer_class = OptionModelSerializer
    pagination_class = OnePagination
    def get_queryset(self):
        objs = OptionsModel.objects.all()
        return objs


class TestModelView(ModelViewSet):
    serializer_class = TestModelSerializer
    def get_queryset(self):
        objs = TestModel.objects.all()
        # try:
        #     order_index = self.request.GET['order[0][column]']
        #     order_p = "columns[%s][data]" % order_index
        #     order = self.request.GET[order_p]
        #
        #     order_up =  self.request.GET['order[0][dir]']
        #     if order_up == 'desc':
        #         objs = TestModel.objects.order_by("-%s"%order)
        #     else:
        #         objs = TestModel.objects.order_by(order)
        #
        #     key = self.request.GET['search[value]']
        #     print('order is %s'%order)
        #     print('search:%s' % key)
        #     objs = objs.filter(name__contains=key)
        # except Exception as e:
        #     print(e)
        #
        # objs = objs.filter(name__contains='')
        return objs


