# -*- coding:utf-8 -*-
from rest_framework.decorators import list_route, detail_route
from django_szuprefix_saas.saas.mixins import PartyMixin
from django_szuprefix_saas.school.permissions import IsStudent
from .apps import Config

__author__ = 'denishuang'
from . import models, serializers
from rest_framework import viewsets, filters
from django_szuprefix.api.helper import register


class CourseViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    search_fields = ('name', 'code')
    filter_fields = ('is_active', 'category', 'code')
    ordering_fields = ('is_active', 'title', 'create_time')

    @list_route(['get'], permission_classes=[IsStudent])
    def for_student(self, request):
        # major = self.student.majors.first()
        courses = self.student.all_courses
        # courses = self.party.course_courses.filter(is_active=True, majors__in=self.student.majors.all())
        page = self.paginate_queryset(courses)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


register(Config.label, 'course', CourseViewSet)


class CategoryViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    search_fields = ('name', 'code')
    filter_fields = ('code', 'name')


register(Config.label, 'category', CategoryViewSet)


class ChapterViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer
    search_fields = ('name',)
    filter_fields = ('course',)


register(Config.label, 'chapter', ChapterViewSet)
