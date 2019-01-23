# -*- coding:utf-8 -*-
import django_filters
from django_szuprefix.api.permissions import DjangoModelPermissionsWithView
from rest_framework.metadata import SimpleMetadata
from .apps import Config

from . import models, mixins, serializers, importers, helper
from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django_szuprefix.api import mixins as api_mixins
from django_szuprefix.api.helper import register

__author__ = 'denishuang'


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


register(Config.label, 'school', SchoolViewSet)


class TeacherViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    permission_classes = mixins.SchoolMixin.permission_classes+[DjangoModelPermissionsWithView]


register(Config.label, 'teacher', TeacherViewSet)


class GradeViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Grade.objects.all()
    serializer_class = serializers.GradeSerializer


register(Config.label, 'grade', GradeViewSet)


class SessionViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer

    def get_queryset(self):
        return super(SessionViewSet, self).get_queryset().filter(
            school=self.request.user.as_saas_worker.party.as_school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)


register(Config.label, 'session', SessionViewSet)


class ClazzViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Clazz.objects.all()
    serializer_class = serializers.ClazzSerializer
    search_fields = ('name', 'code')
    filter_fields = ('name', 'code', 'entrance_session', 'grade')


register(Config.label, 'clazz', ClazzViewSet)


class MajorViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Major.objects.all()
    serializer_class = serializers.MajorSerializer
    search_fields = ('name', 'code')
    filter_fields = {'code':['exact'], 'name': ['exact', 'in']}


register(Config.label, 'major', MajorViewSet)


class CollegeViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.College.objects.all()
    serializer_class = serializers.CollegeSerializer
    search_fields = ('name', 'code')
    filter_fields = ('code', 'name',)


register(Config.label, 'college', CollegeViewSet)


class StudentViewSet(api_mixins.BatchCreateModelMixin, mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    search_fields = ('name', 'number')
    filter_fields = ('grade', 'clazz', 'number')
    ordering_fields = '__all__'
    permission_classes = mixins.SchoolMixin.permission_classes+[DjangoModelPermissionsWithView]

    # def get_serializer_class(self):
    #     print self.action
    #     if self.action == 'list':
    #         return serializers.CurrentStudentSerializer
    #     return super(StudentViewSet, self).get_serializer_class()

    def get_permissions(self):
        if self.action == 'binding':
            return []
        return super(StudentViewSet, self).get_permissions()

    @decorators.list_route(['post'])
    def pre_import(self, request):
        importer = importers.StudentImporter(self.school)
        data = importer.clean(importer.get_excel_data(request.data['file']))
        return Response(data)

    @decorators.list_route(['post'])
    def post_import(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            importer = importers.StudentImporter(self.school)
            data = importer.run(serializer.data)
            return Response(data)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.list_route(['post'], permission_classes=[])
    def binding(self, request):
        serializer = serializers.StudentBindingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            schools = serializer.save()
            data = serializer.data
            data['schools'] = schools
            return Response(data)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.detail_route(['post'])
    def unbind(self, request):
        helper.unbind(self.get_object())
        return Response({'info': 'success'})


register(Config.label, 'student', StudentViewSet)
