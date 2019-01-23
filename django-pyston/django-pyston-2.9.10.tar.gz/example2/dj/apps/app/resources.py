from rest_framework import serializers
from rest_framework import viewsets
from rest_framework_recursive.fields import RecursiveField


from .models import User, Issue


class UserSerializer(serializers.ModelSerializer):

    solving_issue = RecursiveField('IssueSerializer')
    watched_issues = serializers.ManyRelatedField(child_relation=RecursiveField('IssueSerializer'))

    class Meta:
        model = User
        fields = ('id', 'created_at', 'email', 'contract', 'first_name', 'last_name', 'is_superuser', 'test',
                  'solving_issue', 'watched_issues')



class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class IssueSerializer(serializers.ModelSerializer):

    solver = RecursiveField('UserSerializer')
    #watched_by = RecursiveField('UserSerializer', many=True)

    class Meta:
        model = Issue
        fields = ('id', 'created_at', 'name', 'created_by', 'solver', 'leader', 'watched_by')


class IssueViewSet(viewsets.ModelViewSet):

    queryset = Issue.objects.all()
    serializer_class = IssueSerializer