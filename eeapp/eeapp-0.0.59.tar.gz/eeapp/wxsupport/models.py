from django.db import models

# Create your models here.

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




class WXPayNotice(models.Model):
    order_no = models.CharField(max_length=32,verbose_name='订单编号',default='')
    time_end = models.CharField(max_length=20,blank=True,null=True)
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    body = models.TextField(default='',verbose_name='订单Notice数据')
    status_choice = (
        (10, '未支付'),
        (20, '已支付'),
        (30, '失效'),
        (90, '未知'),
    )
    status = models.SmallIntegerField(choices=status_choice, verbose_name='状态', default=90)

    class Meta:
        ordering = ['-create_time', ]

class WXPayOrder(models.Model):
    notice = models.OneToOneField(WXPayNotice,on_delete=models.CASCADE,blank=True,null=True,verbose_name='支付回调条通知')
    order_no = models.CharField(max_length=32,verbose_name='订单编号',default='')
    body = models.TextField(default='',verbose_name='订单POST数据')
    scene_info = models.TextField(verbose_name='场景信息',default='')
    create_time = models.DateTimeField(auto_now_add=True ,verbose_name='创建时间')
    finish_time = models.DateTimeField(auto_now_add=False,blank=True,null=True,verbose_name='结束时间')
    price = models.FloatField(default=0,verbose_name='支付金额')
    is_payed = models.BooleanField(default=False,verbose_name='是否已支付')

    time_end = models.CharField(max_length=20,blank=True,null=True)
    trade_type_choice = (
        ('JSAPI', 'JSAPI支付'),
        ('NATIVE', '扫码支付'),
        ('APP', 'App支付'),
        ('MWEB', 'H5支付'),
    )
    trade_type = models.CharField(max_length=10,verbose_name='交易类型',default='JSAPI')
    VALID = models.BooleanField(default=True)

    @property
    def status(self):
        if self.notice is None:
            return 90
        else:
            return self.notice.status

    class Meta:
        ordering = ['-id', ]
