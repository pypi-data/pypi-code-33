from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.


HTTP_CHOICES = [("post","POST"),("get","GET")]



class Tag(models.Model):
    name = models.CharField(max_length=25)
    created =  models.DateTimeField(auto_now=True,null=True,blank=True)
    updated =  models.DateTimeField(auto_now_add=True,null=True,blank=True)

    def __str__(self):
        return self.name

class ApiParam(models.Model):
    params = models.TextField()
    tags = models.ManyToManyField(Tag,blank=True)

    def __str__(self):
        return self.params

    def get_tags(self):
        list1 = []
        for tag in self.tags.all():
            dict1={}
            dict1["id"]=tag.id
            dict1["name"]=tag.name
            list1.append(dict1)
        return list1

API_STATUSES = [("1","under construction"),("2","leaking"),("3","renovation"),("4","ready to use")]
class Api(models.Model):
    url = models.CharField(max_length=200,unique=True)
    desc = models.CharField(max_length=200,null=True,blank=True)
    params = models.ManyToManyField(ApiParam,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    http_type =  models.CharField(max_length=10,choices = HTTP_CHOICES)
    created =  models.DateTimeField(auto_now=True,null=True,blank=True)
    updated =  models.DateTimeField(auto_now_add=True,null=True,blank=True)
    active = models.BooleanField(default=True)
    user = models.ManyToManyField(User,blank=True)
    status = models.CharField(max_length=50,choices=API_STATUSES,default="1")

    def __str__(self):
        return self.url

    def get_params(self):
        params_list = []
        for api_param in self.params.all():
            dict1 = {}
            dict1["inputset_id"] = api_param.id
            dict1["inputset_params"] = eval(api_param.params)
            dict1["inputset_tags"] = api_param.get_tags()
            params_list.append(dict1)
        return params_list
