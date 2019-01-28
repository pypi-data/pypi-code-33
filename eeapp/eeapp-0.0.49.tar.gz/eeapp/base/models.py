from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User,Group,UserManager,AbstractUser
from rest_framework.authtoken.models import Token

from .fields.ImageSetField import ImageSetField

# print(__name__)


class UManager(UserManager):
    def get_queryset(self):
        return super().get_queryset().filter(VALID=True)

class SafeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(VALID=True)


class Model(models.Model):
    VALID = models.BooleanField(default=True)
    objects = SafeManager()
    class Meta:
        abstract = True


class Account(AbstractUser):
    display_name = models.CharField(max_length=255,default='',verbose_name='昵称')
    VALID = models.BooleanField(default=True)

    account_role = models.CharField(max_length=10,default='base')
    wxopenid = models.CharField(max_length=64,default='')
    objects = UManager()


    def get_role(self):
        return 'base'

    def auth_token(self):
        token,created = Token.objects.get_or_create(user=self)
        return  token.key

    class Meta(User.Meta):
        abstract = True
        permissions = (
            ('base_account_create', 'base create new base'),
            ('base_account_fix', 'base edit other base'),
            ('base_account_delete', 'base drop other base')
        )

    def save(self, *args, **kwargs):
        if not self.username:
            if self.email:
                self.username = self.email
        self.account_role = self.get_role()
        super(Account, self).save(*args, **kwargs)
        token = Token.objects.get_or_create(user=self)




class SuperAccount(Account):
    class Meta:
        abstract = False
        db_table = 'super_account'




class OptionsModel(models.Model):
    name = models.CharField(max_length=64,blank=False,verbose_name='名称')
    value = models.CharField(max_length=20,blank=False,verbose_name='值')



class TestModel(models.Model):
    hobby_choice = (
        ('music', '音乐'),
        ('sport', '运动'),
        ('film', '电影'),
        ('tour', '旅游'),
    )


    email = models.EmailField(max_length=70,blank=True,verbose_name='邮箱')
    name = models.CharField(max_length=20,blank=False,verbose_name='名称')
    covers = ImageSetField(blank=True,verbose_name='封面')
    sex = models.CharField(choices=(('boy','男'),('girl','女'),('unknown','未知')),verbose_name='性别',max_length=10,default='unknown')
    hobbies = models.CharField(verbose_name='爱好',max_length=50,blank=True)
    time = models.TimeField(verbose_name='时间')
    birthday = models.DateField(verbose_name='生日')


    # over_time = models.DateTimeField(blank=True,verbose_name='过期时间')



