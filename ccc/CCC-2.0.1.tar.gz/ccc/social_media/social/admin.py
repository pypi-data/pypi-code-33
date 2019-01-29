# Register your models here.
from django.contrib import admin

from ccc.social_media.social.models import Post, PostedTo

admin.site.register(Post)
admin.site.register(PostedTo)
