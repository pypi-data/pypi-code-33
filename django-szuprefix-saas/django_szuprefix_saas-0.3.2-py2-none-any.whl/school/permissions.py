# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class IsSchoolUser(BasePermission):
    message = "没有权限, 不是学校用户"

    def has_permission(self, request, view):
        assert view.party, "IsSchoolUser permission needs IsSaasWorker permission."
        party = view.party
        valid = hasattr(party, "as_school")
        if valid:
            view.school = party.as_school
        return valid


class IsStudent(IsSchoolUser):
    message = "没有权限, 不是学校学生"

    def has_permission(self, request, view):
        valid = super(IsStudent, self).has_permission(request, view)
        if valid:
            user = request.user
            valid = hasattr(user, "as_school_student")
            if valid:
                view.student = user.as_school_student
        return valid
