# -*- coding:utf-8 -*-
# author : 'denishuang'
from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from django_szuprefix.auth.serializers import UserSerializer

from django_szuprefix_saas.saas.serializers import PartySerializer
from . import models, mixins
from rest_framework import serializers

import logging

log = logging.getLogger("django")


class SchoolSerializer(IDAndStrFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.School
        fields = ('name', 'type', 'create_time')


class TeacherSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('name',)


class GradeSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Grade
        fields = ('name',)


class SessionSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Session
        fields = ('name',)


class MajorSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    college_name = serializers.CharField(source="college.name", read_only=True)

    class Meta:
        model = models.Major
        # exclude = ('party',)
        fields = ('name', 'code', 'college', 'college_name', 'create_time')


class CollegeSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.College
        fields = ('name', 'code', 'create_time')


class ClazzSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    entrance_session_name = serializers.CharField(source="entrance_session.name", label="入学年份", read_only=True)
    student_names = serializers.JSONField(label="学生名单", required=False)

    class Meta:
        model = models.Clazz
        fields = ('name', 'entrance_session', 'entrance_session_name', 'code',
                  'primary_teacher', 'grade', 'grade_name', 'teacher_names', 'student_names','courses')


class ClazzSmallSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Clazz
        fields = ('id', 'name', 'grade', 'entrance_session', 'url')


class StudentSerializer(IDAndStrFieldSerializerMixin, mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    clazz_name = serializers.CharField(source="clazz.name", read_only=True)

    class Meta:
        model = models.Student
        fields = ('id', 'name', 'number', 'clazz', 'clazz_name', 'grade', 'grade_name', 'url', 'courses')


class CurrentStudentSerializer(mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    school = serializers.StringRelatedField()
    clazz = serializers.StringRelatedField()
    grade = serializers.StringRelatedField()
    entrance_session = serializers.StringRelatedField()

    class Meta:
        model = models.Student
        fields = ('name', 'number', 'grade', 'entrance_session', 'clazz', 'school')


class CurrentTeacherSerializer(mixins.SchoolSerializerMixin, serializers.ModelSerializer):
    school = SchoolSerializer()

    class Meta:
        model = models.Teacher
        fields = ('name', 'school')


class StudentBindingSerializer(serializers.Serializer):
    mobile = serializers.CharField(label="手机号", required=True)
    number = serializers.CharField(label="学号", required=True)
    name = serializers.CharField(label="姓名", required=True)
    the_id = serializers.IntegerField(label="指定ID", required=False)

    def validate(self, data):
        assert 'request' in self.context, 'needs context[request]'
        self.request = self.context['request']
        self.cur_user = cur_user = self.request.user
        if cur_user.has_usable_password():
            raise serializers.ValidationError("当前帐号已绑定过,不能重复绑定")
        mobile = data['mobile']
        number = data['number']
        name = data['name']
        the_id = data.get('the_id')
        qset = models.Student.objects.filter(number=number, name=name)
        ss = []
        for s in qset:
            user = s.user
            if hasattr(user, 'as_person') and getattr(user, 'as_person').mobile == mobile:
                if not the_id or s.id == the_id:
                    ss.append(s)
        if not ss:
            raise serializers.ValidationError("相关账号不存在, 可能查询信息不正确, 或者还未录入系统")
        elif len(ss) == 1:
            user = ss[0].user
            if user.has_usable_password():
                raise serializers.ValidationError("该帐号已绑定过,不能重复绑定")
        data['students'] = ss
        return data

    def save(self):
        students = self.validated_data['students']
        if len(students) == 1:
            student = students[0]
            user = student.user
            from django_szuprefix.auth.signals import to_bind_user
            from django.contrib.auth import login
            from django.db import transaction
            log.info("StudentBindingSerializer bind user %s to %s" % (self.cur_user, user))
            with transaction.atomic():
                to_bind_user.send(self, old_user=self.cur_user, new_user=user)
                user.set_password(student.number)
                user.save()
            from django.contrib.auth import BACKEND_SESSION_KEY
            login(self.request, user, backend=self.request.session[BACKEND_SESSION_KEY])
        return [unicode(s.school) for s in students]
