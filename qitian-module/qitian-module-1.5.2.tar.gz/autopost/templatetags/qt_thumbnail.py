from django import template
import random
from django.conf import settings

register = template.Library()
thumb_configure = settings.QINIU_THUMBNAIL['max_limit']


@register.filter
def auto_thumbnail(img_src, alias):
    site, alias = site_image(alias)
    if str(img_src).startswith('http'):
        # TODO 检测这个地址是不是正确,不正确显示随机图片 目前直接显示随机
        return settings.QINIU_RANDOM % random.randint(1, 15) + '?imageView2' + thumb_configure[alias]
    if str(img_src) == '':
        return settings.QINIU_RANDOM % random.randint(1, 15) + '?imageView2' + thumb_configure[alias]
    return qiniu_max_thumbnail(img_src, alias)


def qiniu_max_thumbnail(image_src, alias):
    zoom_name = '?imageView2' + thumb_configure[alias]
    try:
        return get_url_code(image_src.url, zoom_name)
    except Exception as e:
        return get_url_code(settings.MEDIA_URL + str(image_src), zoom_name)


def get_url_code(img_url, alias=''):
    try:
        return img_url + alias
    except Exception:
        return settings.QINIU_RANDOM % random.randint(1, 15) + alias


def site_image(alias):
    site = ''
    if alias.__contains__('__'):
        args = str(alias).split(',')
        site = args[0]
        alias = args[1]
    return site, alias
