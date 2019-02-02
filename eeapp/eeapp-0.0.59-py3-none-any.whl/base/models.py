from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User,Group,UserManager,AbstractUser,AbstractBaseUser,PermissionsMixin
from rest_framework.authtoken.models import Token

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from eeapp.base.fields.ImageSetField import ImageSetField

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


class Account(User):
    display_name = models.CharField(max_length=255,default='',verbose_name='昵称')
    VALID = models.BooleanField(default=True)
    role = models.CharField(max_length=10,default='base')

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
        if not self.role:
            self.role = self.get_role()
        super(Account, self).save(*args, **kwargs)
        token = Token.objects.get_or_create(user=self)



#AbstractUser
class BaseUser(AbstractBaseUser):
    display_name = models.CharField(max_length=255,default='',verbose_name='昵称')
    VALID = models.BooleanField(default=True)

    role = models.CharField(max_length=10,default='base')
    wxopenid = models.CharField(max_length=64,default='')
    objects = UManager()
    # objects = UserManager()


    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)


    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True


    def get_role(self):
        return 'base'

    def auth_token(self):
        token,created = Token.objects.get_or_create(user=self)
        return  token.key

    class Meta(User.Meta):
        abstract = True
        # permissions = (
        #     ('base_account_create', 'base create new base'),
        #     ('base_account_fix', 'base edit other base'),
        #     ('base_account_delete', 'base drop other base')
        # )

    def save(self, *args, **kwargs):
        if not self.username:
            if self.email:
                self.username = self.email
        if not self.role:
            self.role = self.get_role()
        super(BaseUser, self).save(*args, **kwargs)
        token = Token.objects.get_or_create(user=self)



class WXUserAuth(models.Model):
    openid = models.CharField(max_length=256,verbose_name='微信openid')
    code = models.CharField(max_length=256,blank=True,verbose_name='code')
    access_token = models.CharField(max_length=256,blank=True,verbose_name='access_token')
    refresh_token = models.CharField(max_length=256,blank=True,verbose_name='refresh_token')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    VALID = models.BooleanField(default=True)


class WXAuthLog(models.Model):
    user = models.ForeignKey(WXUserAuth,on_delete=models.CASCADE,verbose_name='用户')
    openid = models.CharField(max_length=256,verbose_name='微信openid')
    access_token = models.CharField(max_length=256,verbose_name='access_token')
    refresh_token = models.CharField(max_length=256,verbose_name='refresh_token')
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    VALID = models.BooleanField(default=True)






class Log(models.Model):

    content = models.CharField(max_length=255,verbose_name='日志内容',blank=True)
    time = models.DateTimeField(verbose_name='时间',auto_now_add=True)
    mark = models.CharField(max_length=255,verbose_name='操作者',blank=True)

    class Meta:
        abstract = False





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



