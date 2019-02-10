from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from django.db.models.signals import post_save
from django.db.utils import OperationalError
import pathlib
from datetime import datetime
from django.core.cache import cache

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


from mycms.creole import creole2html


from rest_framework.authtoken.models import Token

from loremipsum import generate_paragraphs

class CMSPaths(models.Model):

    #class Meta: 
    #    db_table = "yacms_cmspaths" #To remove when we no longer need to actuall db contents. 

    path = models.CharField(max_length=2000, null=True)
    parent = models.ForeignKey("CMSPaths", null=True, blank=True, 
                               on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.path




class CMSTags(models.Model):

    #class Meta:
    #    db_table = "yacms_cmstags"

    name = models.CharField(max_length=256, default="NotSet")

    def __str__(self):
        return self.name

class CMSMarkUps(models.Model):
    #class Meta:
    #    db_table = "yacms_cmsmarkups"

    markup = models.CharField(max_length=128, default="Creole")

    def __str__(self):
        return self.markup
                    
class CMSContents(models.Model):
    
    #class Meta:
    #    db_table = "yacms_cmscontents" 
    
    title = models.CharField(max_length=1024, null=True, blank=True)
    content = models.TextField(max_length=20480, default="Empty")
    timestamp = models.DateTimeField(auto_now=True)
    markup = models.ForeignKey(CMSMarkUps, null=True, on_delete=models.DO_NOTHING)
    meta_description = models.TextField(max_length=20480, default="", blank=True)
    tags = models.ManyToManyField(CMSTags, blank=True )
    page = models.IntegerField(default=1)

    def __str__(self):
        return self.content

    @property
    def html(self):

        #Lazy import is needed because the mycms.view_handlers requires to import
        #mycms.models.CMSEntries, but unfortunately the models will not yet
        #be available during the django startup and causes an exception.
        from mycms.view_handlers.formatters import CreoleFormatter
        return CreoleFormatter(self.content).html()

class CMSTemplates(models.Model):

    #class Meta: 
    #    db_table = "yacms_cmstemplates"

    name = models.CharField(max_length=1024, default="page.html")
    template = models.TextField(max_length=10240, default="empty template")

    def __str__(self):
        return self.name

class CMSPageTypes(models.Model):

    #class Meta:
    #    db_table = "yacms_cmspagetypes"

    page_type = models.CharField(max_length=64, default="DefaultType")
    text = models.CharField(max_length=128, default="default class")
    view_class = models.CharField(max_length=256, default="DefaultView")
    view_template = models.CharField(max_length=32, default=None)


    def save(self, *args, **kwargs):
        #if (self.pk is None) and (self.view_template is None):
        if (self.view_template is None):
            #We only care to put the view template as the name of the view_class
            #during the creation.
            self.view_template = "DefaultView.html"

        super(CMSPageTypes, self).save(*args, **kwargs)




    def __str__(self):
        return self.text


def get_admin_user():

    try:
        admin = User.objects.get(username="admin")
        return admin
    except OperationalError as e:
        return 1



class CMSEntries(models.Model):

    #class Meta: 
    #    db_table = "yacms_cmsentries"

    title = models.CharField(max_length=1024, default=None)
    path = models.ForeignKey(CMSPaths, 
                             null=True, 
                             on_delete=models.DO_NOTHING)
    slug = models.SlugField(max_length=1024, unique=True)

    #We make the content a many to many to be able to handle multiple
    #so we can version by published.
    content = models.ManyToManyField(CMSContents, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    page_type = models.ForeignKey("CMSPageTypes", 
                                  null=True, 
                                  on_delete=models.DO_NOTHING)
    template = models.ForeignKey(CMSTemplates, 
                                 null=True, 
                                 blank=True, 
                                  on_delete=models.DO_NOTHING)

    frontpage = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    lists_include = models.BooleanField(default=True)

    page_number = models.IntegerField(default=1)
    created_by = models.ForeignKey(User, 
                                   #default=get_admin_user().pk, 
                                   null=True, 
                                   blank=True,                                   
                                  on_delete=models.DO_NOTHING)

    logo_url = models.CharField(default="/static/mycms/images/png/default.png", 
                                null=True,blank=True, 
                                max_length=1024)

    def on_create(self):

        view_object = self.view
        

        if hasattr(view_object, "on_create"):
            view_object.on_create()


    def parent(self):

        #Get the cms entry that has a path belonging to the parent of our path.
        parent_entry = CMSEntries.objects.get(path=self.path.parent)
        return parent_entry


    def html_content(self):
        # We are going to index the parsed content of the CMSEntries 
        # so we are going to ask our view to give that to us.
        
        #Fortunately the view for this CMSEntrie should alread
        #implement html_content so we let it handle it. 
        return self.view.html_content


    def __str__(self):
        return self.title

 
    #----------------------------------------------------------------------
    @property
    def  date_created_str(self):
        """"""
        #value = self.date_created.strftime("%Y%m%d %H:%M")
        value = self.date_created
        return value

    @property
    def  date_modified_str(self):
        """"""
        value = self.date_modified.strftime("%Y%m%d %H:%M")
        return value


    @property
    def view(self):
        from mycms.view_handlers import ViewObject
        view_object =  ViewObject(page_object=self)
        return view_object
    
    @property
    def view_object(self):
        return self.view

    def get_absolute_url(self):
        cms_base_path = getattr(settings, "YACMS_BASEPATH", None)

        if not cms_base_path:
            cms_base_path = "/cms"

        if not cms_base_path.endswith("/"):
            cms_base_path = cms_base_path.rstrip("/")

        #we assume here that self.path.path will always start with a /
        return "{}{}".format(cms_base_path, self.path.path)


    def get_parent_paths(self,path_str):

        x = path_str.rfind("/")

        if x == 0 :
            #we are at the root
            return [path_str]

        else:
            return  self.get_parent_paths(path_str[:x]) + [path_str]


    def parents_list(self):

        path_str = self.path.path

        p = self.get_parent_paths(path_str)

        pl = []
        for path_str in p:

            pl.append(CMSEntries.objects.get(path__path=path_str))

        return pl

    def categories(self):
        c = CMSEntries.objects.filter(path__parent=self.path, 
                                      page_type__page_type="CATEGORY",
                                      published=True)
        return c




    def save(self, *args, **kwargs):
        if self.pk is None:
            super(CMSEntries, self).save(*args, **kwargs)
            
            #Commenting out self.on_create() because we still do not have 
            #a path yet and as a result we can not call self.on_create()
            #self.on_create()
            
        else:
            super(CMSEntries, self).save(*args, **kwargs)
            

    #def save(self, *args, **kwargs):

        #if self.pk is None:
            #tell parent to save ourselves so we get a pk.
            #super(CMSEntries, self).save(*args, **kwargs)

            #print("WE HAVE A PK: {} ".format(self.pk))
            ##This is a new cms entry
            ##create a new content and
            #paragraphs = generate_paragraphs(5, start_with_lorem=False)
            #p = ""
            #for paragraph in paragraphs:
                #p =  unicode(paragraph[2]) + "\n\n" + p
            #h =  creole2html(p)

            #obj = CMSContents()
            #obj.content = "This is a new content."
            #obj.save()

            #cms_obj = CMSEntries.objects.get(id=self.pk)
            #cms_obj.content.add(obj)


        #else:
            #super(CMSEntries, self).save(*args, **kwargs)

            

## method for updating
#def create_default_content(sender, instance, created, **kwargs):

    #if created:
        #obj = CMSContents()
        #obj.content = "This is the latest content1"
        #obj.save()

        #c = CMSContents.objects.get(id=obj.id)
        #instance.content.add(c)
        #print(type(instance))

## register the signal
#post_save.connect(create_default_content, sender=CMSEntries, dispatch_uid="CREATE_CONTENT")

class CMSArchivesIndex(models.Model):
    
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=1975)
    entries = models.ManyToManyField(CMSEntries, blank=True)
    

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


    #
 
 
 