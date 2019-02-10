from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from mycms.models import CMSContents
from mycms.models import CMSMarkUps
from mycms.models import CMSTemplates
from mycms.models import CMSPageTypes
from mycms.models import CMSEntries
from mycms.models import CMSPaths

import os

class LoremIpsumSerializer(serializers.Serializer):

    num_paragraphs = serializers.IntegerField()

    class Meta:
        fields = ['num_paragraphs']


class CMSPathsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSPaths
        fields = ('id','path','parent')

class CMSPageTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSPageTypes
        fields = ('id','page_type','text','view_class','view_template')

class CMSContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSContents
        fields = ('id', 'content', 'timestamp', 'markup','title')

class CMSMarkUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSMarkUps
        fields = ('id','markup')

class CMSTemplatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSTemplates
        fields = ('id','name', 'template')

class CMSEntrySerializer(serializers.ModelSerializer):

    path = serializers.StringRelatedField()
    title = serializers.CharField(max_length=1024,
                                  help_text="The title of the page.")
    #content = serializers.CharField(default="[]")
    #template = serializers.IntegerField(default=1,
    #                                    help_text="Index value, pk for template")
    frontpage = serializers.BooleanField(default=False,
                                         help_text="default to False. Set True to display in frontpage")
    published = serializers.BooleanField(default=False,
                                         help_text="Published defaults to False")
    page_number = serializers.IntegerField(default=1,
                                           help_text="page_number")

    #content = serializers.ManyRelatedField(child_relation=CMSContents,
    #                                       help_text="array of PK of content objects.")
    class Meta:
        model = CMSEntries
        fields = ('id','title','path','slug','content','date_created',
                  'page_type','frontpage','published',
                   'page_number')

class CMSEntryExpandedSerializer(serializers.ModelSerializer):

    path = serializers.StringRelatedField()
    template = serializers.IntegerField(default=1,
                                        help_text="Index value, pk for template")
    class Meta:
        model = CMSEntries
        fields = ('id','title','path','slug','content','date_created',
                  'page_type','template','frontpage','published',
                   'page_number', "date_modified")


class EntryData(object):

    def __init__(self, **kwargs):
        for field in ('id', "title", "slug", "parent"):
            setattr(self, field,  kwargs.get(field, None))



class CMSChildEntrySerializer(serializers.ModelSerializer):

    template = serializers.IntegerField(required=False)
    content= CMSContentsSerializer(many=True, required=False)
    
    class Meta:
        model = CMSEntries

        fields = ('id','title','slug','content','date_created',
                  'page_type','template','frontpage','published',
                   'page_number')



    def make_path(self, slug, parent_id):
        """
        Creates a CMSPaths object for the current CMSEntry.
        """

        parent_obj = CMSEntries.objects.get(id = parent_id)
        path_str = os.path.join(parent_obj.path.path, slug)
        path_obj,c  = CMSPaths.objects.get_or_create(path=path_str, parent=parent_obj.path)

        if not c:
            print("Warning. Recreated {}".format(path_str))
            #We need to check if there exists an article with this Path.
            entry = CMSEntries.objects.filter(path=path_obj)
            if entry:
                raise Exception("Article: {} already exists. Refuse to create. ".format(entry.title))
        return path_obj

    def create(self, validated_data, parent_id=None):

        title = validated_data["title"]
        slug = validated_data["slug"]
        try:
            content = validated_data["content"]
        except KeyError as e: 
            #This means no content was provided. Previous versions of
            #DRF would provide content = [] when no content was provided
            #so this is just a hack!
            content = []
            
        template = validated_data.get("template", None)
        published = validated_data["published"]
        frontpage = validated_data["frontpage"]
        page_type = validated_data["page_type"]

        #TODO: Currently even though we accept a path id, we do not use it
        #and instead we insist on getting or creating the CMSPaths object
        #which has the path corresponding to this CMSEntry.


        child = CMSEntries()
        child.title = title
        child.slug = slug
        child.frontpage = frontpage
        child.published = published
        
        #Need to call save before being able to add any reference
        child.save()

        path_obj = self.make_path(slug, parent_id)
        
        child.path = path_obj
        child.template = template

        if len(content) == 0:
            content_entry = CMSContents(content="New Page. Please Edit Me!!!")
            content_entry.save()
            child.content.add(content_entry)
        else:
            #TODO: This has never been tested. Test this and remove.
            child.content = content

        child.page_type=page_type
        child.save()

        #Now call the on_create() of the Child Entry
        
        child.on_create()
        
        
        return child



class CMSPathFullSerializer(serializers.ModelSerializer):

    class Meta:
        model = CMSPaths

        fields = ['path', 'parent']

class CMSPageSerializer(serializers.ModelSerializer):

    path = CMSPathFullSerializer()
    content = CMSContentsSerializer(many=True)
    class Meta:
        model = CMSEntries
        title = serializers.CharField(max_length=1024, default=None)


        fields = ('id','title','slug','content','date_created',
                  'page_type','template','frontpage','published',
                   'page_number', 'path',)
    #path = serializers.Field.ForeignKey(CMSPaths,
    #                         null=True,
    #                         on_delete=models.DO_NOTHING)
    #slug = models.SlugField(max_length=1024, unique=True)

    ##We make the content a many to many to be able to handle multiple
    ##so we can version by published.
    #content = models.ManyToManyField(CMSContents, blank=True)
    #date_created = models.DateTimeField(auto_now_add=True)
    #date_modified = models.DateTimeField(auto_now_add=True)

    #page_type = models.ForeignKey("CMSPageTypes",
                                  #null=True,
                                  #on_delete=models.DO_NOTHING)
    #template = models.ForeignKey(CMSTemplates,
                                 #null=True,
                                 #blank=True,
                                 #on_delete=models.DO_NOTHING)

    #frontpage = models.BooleanField(default=False)
    #published = models.BooleanField(default=False)

    #page_number = models.IntegerField(default=1)
    #created_by = models.ForeignKey(User,
                                   ##default=get_admin_user().pk,
                                   #null=True,
                                   #blank=True,
                                   #on_delete=models.DO_NOTHING)


class CMSAuthTokenSerializer(serializers.Serializer):

    pass
