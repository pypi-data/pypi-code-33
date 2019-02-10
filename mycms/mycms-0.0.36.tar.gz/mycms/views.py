from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import logging
import pathlib
import os
from PIL import Image
import threading
import datetime

from bs4 import BeautifulSoup
import simplejson as json
import threading
import arrow
from pathlib import Path

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.contrib.sitemaps import Sitemap
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django import forms
from django.forms.models import model_to_dict
from django.http import Http404
from django.core.files.uploadedfile import UploadedFile
from django.utils.text import slugify
from django.views.generic.base import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework import permissions
from django.contrib.auth import logout
from django.contrib.auth import login


from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned
from django.template import RequestContext

from django.http import HttpResponseNotFound
# Create your views here.

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound


from rest_framework import authentication, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import status

from rest_framework import filters
from rest_framework import generics

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView


from django_filters.rest_framework import DjangoFilterBackend

from loremipsum import get_paragraphs
from mycms.creole import creole2html

from mycms.serializers import CMSPageTypesSerializer
from mycms.serializers import CMSContentsSerializer
from mycms.serializers import CMSEntrySerializer
from mycms.serializers import CMSMarkUpSerializer
from mycms.serializers import CMSTemplatesSerializer
from mycms.serializers import CMSPathsSerializer
from mycms.serializers import CMSEntryExpandedSerializer
from mycms.serializers import LoremIpsumSerializer


from mycms.models import CMSPageTypes
from mycms.models import CMSContents
from mycms.models import CMSEntries
from mycms.models import CMSMarkUps
from mycms.models import CMSTemplates
from mycms.models import CMSPaths

from mycms.view_handlers import ViewObject



from mycms.api import CMSContentsViewSet
from mycms.api import CMSFormatterContent


logger = logging.getLogger(name="mycms.views")

try:
    import wingdbstub
except:
    pass

def  get_static_files_dir():
    """
    Gets the static files directory.
    """

    for each in settings.STATICFILES_DIRS:
        if each.endswith("static"):
            return each
    else:
        raise Exception("""Static Files Dir Not Found. Please create a 'static' dir within the parent path.""")




class CMSFileUpload(View):


    def get(self, request, **kwargs):

        format = request.GET.get("format", None)

        if format == "json":
            #Get a list of the image names.
            pass

        from django.conf import settings
        
        try:
            assets_dir = settings.YACMS_SETTINGS.get("ARTICLE_IMAGES_DIR")
        except AttributeError as e: 
            print("ARTICLE_IMAGES_DIR IS NOT CONFIGURED! Falling back to default.")
            assets_dir = os.path.join(settings.BASE_DIR, "static/assets")
        
        path = kwargs.get("path", None).lstrip("/")
        fullpath = pathlib.Path(pathlib.Path(assets_dir), path)
        print(path)

        data = []

        if fullpath.exists():

            for each in fullpath.iterdir():
                if each.suffix in [".jpeg", ".jpg", ".gif", ".png", ".bmp"]:
                    data.append("/images/{}/{}".format(path, each.name))

        return JsonResponse(data,safe=False)
        #template = "mycms/FileUpload.html"
        #return render_to_response(template, {})

    def _mkdir(self,newdir):
        """Copied from http://code.activestate.com/recipes/82465-a-friendly-mkdir/ """
        """works the way a good mkdir should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                self._mkdir(head)
            #print "_mkdir %s" % repr(newdir)
            if tail:
                if not os.path.exists(newdir):
                    os.mkdir(newdir)

    def fileupload(self,request, **kwargs):

        mylock = threading.Lock()

        with mylock:
            from django.conf import settings

            """
            The files are uploaded to the assets directory. A directory is 
            created with the same path as the article that the asset is 
            uploaded to. For example an article at 
            /foo/bar/baz will hvae all images uploaded to 
            Path(settings.ASSETS_DIR, "foo/bar/baz/image)
            """

            try:
                #A sanity check to make sure the assets dir exists.
                #TODO: Decide if this code should really be here. IMHO the 
                #test to make sure it exists should be elsewhere. 
                assets_dir = settings.ASSETS_DIR
                
            except AttributeError as e: 
                print("ASSETS_DIR IS NOT CONFIGURED! Falling back to default.")
                #TODO: Danger!! We assuming here that PARENT_DIR is defined. 
                #What if the end user does not define it????
                assets_dir = os.path.join(settings.PARENT_DIR, "assets/")
                        
            path = kwargs.get("path", None).lstrip("/")

            fullpath = pathlib.Path(pathlib.Path(assets_dir), path)

            if not fullpath.exists():
                self._mkdir(fullpath.as_posix())
            elif not fullpath.is_dir():
                #Fix this to return a proper json response.
                return HttpResponse("Error. Not full dir")

            thumbnailpath = pathlib.Path(fullpath, "thumbnails")

            if not thumbnailpath.exists():
                try:
                    os.makedirs(thumbnailpath.as_posix())
                except FileExistsError as e:
                    #If we hit here then it means, some other thread
                    #created it.
                    pass
            elif not thumbnailpath.is_dir():
                #Fix this to return a proper json response.
                return HttpResponse("Error. Not full dir")

            if request.method == "POST":
    
                
                uploaded_file = request.FILES.get("files[]")

                filename = uploaded_file.name

                p_filename = pathlib.Path(fullpath, filename)

                with open(p_filename.as_posix(), 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                #Now do the thumbail.
                try:
                    size = 256, 256
                    outfile =  pathlib.Path(thumbnailpath, filename)
                    im = Image.open(p_filename.as_posix())
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(outfile.as_posix(), "JPEG")
                except IOError as e:
                    return JsonResponse( { "error" : "cannot create thumbnail for {}".format(outfile)})

                except Exception as e:
                    return JsonResponse( { "error": "Unhandled exception: {}".format(outfile) })


    def post(self,request, **kwargs):

        self.fileupload(request, **kwargs)
        return HttpResponse("Completed")

    def delete(self, request, **kwargs):
        pass



def index(request, **kwargs):
    return HttpResponse("Index page")



def fileupload(request, **kwargs):

    template = "mycms/fileupload.html"
    return render_to_response(template, {})



from django.contrib.sitemaps import Sitemap
#from blog.models import Entry

class CMSSitemap(Sitemap):
    #changefreq = "never"
    priority = 0.9

    def items(self):
        return CMSEntries.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.date_modified

#Django 

 
class CMSLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Username")
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)

class CMSLoginView(View):

    def get(self, request, **kwargs):
        template_name = "mycms/Login.html"

        context = {"form": CMSLoginForm()}
        return render(request, template_name, context)


    def post(self, request, **kwargs):

        username = request.POST.get("username", None)
        password = request.POST.get("password", None)
        
        #Set the next page to a default if not given. 
        next_page = request.GET.get("next", "/cms/user/articles")

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        error_msg = ""
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                if next_page is not None:
                    return HttpResponseRedirect(next_page)
                else:
                    #Go to the user's account page. 
                    return HttpResponse(content=b'You are now logged in.')
            else:
                print("The password is valid, but the account has been disabled!")
                error_msg = "Account is disabled."
        else:
            # the authentication system was unable to verify the username and password
            error_msg = "The system was unable to verify the username and password."

        template_name = "mycms/Login.html"
        return render(request, template_name,{ "error_msg": error_msg})



class CMSUserAdminPagesView(View):
    
    def get(self, request, **kwargs):
        pass



class CMSLogoutView(View):

    def get(self, request, **kwargs):
        logout(request)
        #template_name = "mycms/Login.html"
        #return render_to_response(template_name,context_instance=RequestContext(request))
        return HttpResponseRedirect("/login/")

class CMSFrontPage(View):

    def get(self, request, **kwargs):

        #template_name = "mycms/Index.html"
        template_name = "mycms/index.html"
        #return render(template_name,context_instance=RequestContext(request) )
        
        #TODO: Fix this hack. We create a fake view_object for the frontpage
        #so that we can pass a few template data. 
        
        class View_Object():
            pass
        
        view_object = View_Object()
        
        if settings.FORCE_SHOW_ADVERTS or (settings.DEBUG == False):
            view_object.SHOW_ADVERTS = True
        else:
            print("SHOW_ADDS_IS FALSE") 
            view_object.SHOW_ADVERTS = False
       	 
        print("FORCE_SHOW_ADVERTS={},DEBUG={},SHOW_ADDS={}".format(settings.FORCE_SHOW_ADVERTS, settings.DEBUG, view_object.SHOW_ADVERTS) )
        return render(request, template_name, { "view_object": view_object})


class LoremIpsumAPIView(APIView):

    """Returns loremipsum paragraphs"""
    authentication_classes = (authentication.SessionAuthentication,
                      authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):

        data = { "message": "You need to send a post."}
        return Response(data, status=status.HTTP_200_OK)


    def post(self, request, **kwargs):
        """Get X number of paragraphs"""
        serializer = LoremIpsumSerializer(data=request.data)
        if serializer.is_valid():
            num_paragraphs = request.data.get("num_paragraphs")

            paragraphs_list  = get_paragraphs(int(num_paragraphs))

            html = ""
            for paragraph in paragraphs_list:
                html += "{}\n\n".format(paragraph)

            data = {"content" : html }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CMSPathsAPIView(APIView):
    """
    View to list PageTypes handled by the system
    """

    authentication_classes = (authentication.SessionAuthentication,
                              authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Get a list of all paths or info about a path
        """

        format = kwargs.get("format", None)
        resource_id = kwargs.get("resource_id", None)

        if resource_id:
        #We are asking for a single entry
            try:
                cmspath = CMSPaths.objects.get(pk=resource_id)
            except ObjectDoesNotExist as e:
                msg_dict = { "error": "Resource with id {} does not exist".format(resource_id) }
                return Response(data=msg_dict, exception=True, status=200)

            serializer = CMSPathsSerializer(cmspath, many=False)
            return Response(serializer.data)

        paths = CMSPaths.objects.all()
        serializer = CMSPathsSerializer(paths, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):

        #Fix the path if it does not start with a / by appending
        #it to the parent path.


        path_str = request.data.get("path")
        parent_str = request.data.get("parent")

        #parent_obj = CMSPaths.objects.get(parent__path=parent_str)

        data_dict = request.data.dict()

        #if path_str and (not path_str.startswith("/")):

            #if int(parent_obj.id) != 1: #1 is always / so we need to get only what is not 1
                #parent_cmspath = CMSPaths.objects.get(pk=parent_id)
                #data_dict["path"] = "{}/{}".format(parent_cmspath.path, path_str)
            #else:
                #data_dict["path"] = "/{}".format(path_str)

        if (parent_str == "") or (parent_str == "/"):
            data_dict["path"]  = data_dict["path"] = "/{}".format(path_str)
        else:
            data_dict["path"] = "{}/{}".format(parent_str, path_str)

        parent = CMSPaths.objects.get(path=parent_str)
        data_dict["parent"] = parent.id
        serializer = CMSPathsSerializer(data=data_dict)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CMSPageTypesAPIView(APIView):
    """
    View to list PageTypes handled by the system

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    #authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Get a list of all available PageTypes
        """

        format = kwargs.get("format", None)

        pagetypes = CMSPageTypes.objects.all()
        serializer = CMSPageTypesSerializer(pagetypes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CMSPageTypesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CMSMarkUpsAPIView(APIView):
    """
    View to list PageTypes handled by the system

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    authentication_classes = (authentication.SessionAuthentication,
                              authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Get a list of all available PageTypes
        """

        format = kwargs.get("format", None)
        pagetypes = CMSMarkUps.objects.all()
        serializer = CMSMarkUpSerializer(pagetypes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CMSMarkUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CMSTemplatesAPIView(APIView):
    """
    View to list PageTypes handled by the system

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    #authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Get a list of all available PageTypes
        """

        format = kwargs.get("format", None)
        pagetypes = CMSTemplates.objects.all()
        serializer = CMSTemplatesSerializer(pagetypes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CMSTemplatesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import django_filters
class CMSEntriesFilter(django_filters.FilterSet):

    class Meta:
        model = CMSEntries
        fields = ['id','page_type', 'slug', 'date_created','published', 'frontpage', 'date_created']


class CMSEntriesROAPIView(generics.ListAPIView):

    queryset = CMSEntries.objects.all()
    serializer_class = CMSEntrySerializer
    filter_class = CMSEntriesFilter
    permission_classes = (IsAuthenticated,)


from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated



class CMSEntriesAPIView(APIView):
    """
    View to list PageTypes handled by the system

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,)

    def get(self, request, **kwargs):
        """
        Get a list of all available PageTypes
        """
        format = kwargs.get("format", None)
        resource_id = kwargs.get("resource_id")

        parent_id  = self.request.query_params.get('parent', None)
        page_id = self.request.query_params.get('id', None)
        page_type_id = self.request.query_params.get('page_type', None)
        expand=self.request.query_params.get('expand', None)

        if resource_id:
            #We are asking for a single entry

            try:
                cmsentry = CMSEntries.objects.get(pk=resource_id)
            except ObjectDoesNotExist as e:
                msg_dict = { "error": "Resource with id {} does not exist".format(resource_id) }
                return Response(data=msg_dict, exception=True, status=200)

            serializer = CMSEntrySerializer(cmsentry, many=False)
            return Response(serializer.data)

        cmsentries = CMSEntries.objects.all()


        if parent_id is not None:

            #We are receiving the id of the parent. We want to return all
            #the cms entries whose path is the children of the path
            #of the parent.


            parent_cmsentry = CMSEntries.objects.get(id=parent_id)
            parent_path = CMSPaths.objects.get(id=parent_id)


            cmsentries = cmsentries.filter(path__parent=parent_cmsentry.path)

        if page_type_id:
            cmsentries = cmsentries.filter(page_type=page_type_id)

        if page_id is not None:
            cmsentries = cmsentries.filter(id=page_id)

        if expand:
            serializer = CMSEntryExpandedSerializer(cmsentries, many=True)
        else:
            serializer = CMSEntrySerializer(cmsentries, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):


        #Because the serializer is so fucking picky, we don't use it
        #to serialize the form

        title = request.data.get("title", None)
        path_id = request.data.get("path", None)
        slug = request.data.get("slug", None)
        page_type_id = request.data.get("page_type", None)

        if slug is None:
            slug = slugify(title)

        if None in (title, path_id, slug, page_type_id):
            return Response({"error": "title,path, slug and page_type are not optional"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cmspath_obj = CMSPaths.objects.get(id=path_id)
        except ObjectDoesNotExist as e:
            return Response({"error": "CMSPath: {} does not exist".format(path_id)},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            cmspagetype_obj  = CMSPageTypes.objects.get(id=page_type_id)
        except ObjectDoesNotExist as e:
            return Response({"error": "CMSPageType: {} does not exist".format(page_type_id)},
                            status=status.HTTP_400_BAD_REQUEST)


        #Now create the cms_obj.
        new_cmsentry = CMSEntries()
        new_cmsentry.title = title
        new_cmsentry.path = cmspath_obj
        new_cmsentry.slug = slug
        new_cmsentry.page_type = cmspagetype_obj
        new_cmsentry.save()

        content = CMSContents()
        content.content = "No content. Edit me."
        content.save()

        new_cmsentry.content.add(content)
        new_cmsentry.on_create()

        return Response(model_to_dict(new_cmsentry, exclude="content"), status=status.HTTP_200_OK)



    def put(self, request, **kwargs):
        serializer = CMSEntrySerializer(data=request.data)



        format = kwargs.get("format", None)
        expand = self.request.query_params.get('expand', None)

        id = request.data.get("id", None)
        if id:
            id = int(id)

        if not id:
            res = {"code": 400, "message": "PUT request requires an id parameter"}
            return Response(data=json.dumps(res), status=status.HTTP_400_BAD_REQUEST)

        cmsentry_object = CMSEntries.objects.get(id=id)


        #Now update the cmsentry_object with the attributes from
        #the request.data

        for key in request.data:

            if key == "date_created_epoch":
                print("Recieved a date_created_epoch")
                value = request.data.get("date_created_epoch")
                created_datetime = datetime.datetime.utcfromtimestamp(int(value)/1000)

                cmsentry_object.date_created = created_datetime

            elif key == "date_created_str":
                #WE re
                x1 = request.data.get("date_created_str")
                x2 = arrow.get(x1, 'YYYY/MM/DD HH:mm')
                setattr(cmsentry_object, "date_created", str(x2))

            elif key == "date_modified_str":
                y1 = request.data.get("date_modified_str")
                y2 = arrow.get(y1, 'YYYY/MM/DD HH:mm')
                setattr(cmsentry_object, "date_modified", str(y2))

            elif hasattr(cmsentry_object, key) and (key != "id"):

                value = request.data.get(key)
                if value == "true":
                    value = True
                if value == "false":
                    value = False
                setattr(cmsentry_object, key, value)

        cmsentry_object.save()

        print(cmsentry_object.frontpage)

            #if expand:

        #We return only the values that we have set.


        return Response(request.data, status=status.HTTP_200_OK)

        #else:
        #    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CMSContentsAPIView(APIView):
    """
    View to list PageTypes handled by the system

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    #authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Get a list of all available PageTypes
        """


        format = kwargs.get("format", None)
        pagetypes = CMSContents.objects.all()
        content_id = self.request.query_params.get('resource_id', None)

        contents = CMSContents.objects.all()

        if content_id is not None:
            contents = contents.filter(id=content_id);

        serializer = CMSContentsSerializer(contents, many=True)
        return Response(serializer.data)



    def post(self, request, format=None):
        serializer = CMSContentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            print(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):


        serializer = CMSContentsSerializer(data=request.data)

        resource_id = request.data.get("id", None)

        if not resource_id:
            res = {"code": 400, "message": "PUT request requires a resource id parameter"}
            return Response(data=res, status=status.HTTP_200_OK)

        if serializer.is_valid():
            cmscontent_object = CMSContents.objects.get(id=resource_id)
            cmscontent_object.content = request.data.get("content")
            cmscontent_object.save()

            include_html = request.GET.get("include_html", None)

            if include_html:
                #Custom pack results:
                cmscontent_dict = model_to_dict(cmscontent_object)


                #We need to get the html. So We need the freaking ViewObject.



                cmscontent_dict["html"] = cmscontent_object.html

                return Response(cmscontent_dict, status=status.HTTP_202_ACCEPTED)
            else:
                serializer = CMSContentsSerializer(cmscontent_object)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CMSIndexView(APIView):
    """
    The index view of a YACMS website.

    url: /cms.

    This is a special page since it needs to exist before any other
    categories or pages can be created.

    To create a new page , we need at minimum to post

    title:
    page_type:

    """

    def get(self, request, **kwargs):
        pass


class CMSArticleListsView(View):
    """
    Implements a paginated list view of all published articles. 
    """
    from django.db.models import Q
    
    def get(self,request, **kwargs):
        
        obj_list = CMSEntries.objects.filter((Q(page_type = singlepageview_pagetype_obj) | Q(page_type = multipageview_pagetype_obj)) &
                                             Q(path__parent__id = self.page_object.path.id))[start: start+page_size]
        #wrap the entries of the obj_list into their view_handler representations
        view_list = []
        
        
        for obj in obj_list:
            view_list.append(ViewObject(page_object=obj))

        return view_list
    
    

class CMSPageView(View):
    """
    The main interface to the website. This view serves all of the web pages
    except pages served by:
    
        CMSArticleListsView.    
        CMSIndexView
        CMSFrontPage
        
        
    """

    def get_object(self,request, **kwargs):
        """
        returns a ViewObject
        """
        path = kwargs.get("path", None)
        page_id = kwargs.get("page_id", None)

        try: 
            if path:
                obj = ViewObject(path=path, request=request)
            
            elif page_id:
                obj = ViewObject(page_id=page_id, request=request)
            else:
                #Lets make path = "/" as default.
                obj = ViewObject(path=u"/", request=request)
                
            return obj

        except ObjectDoesNotExist as e:

            if (path is None) or (path == u"/"):
                #we are in /cms and it does not exist. We create it!!


                path_obj,_ = CMSPaths.objects.get_or_create(path="/")

                try:
                    pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="CATEGORY",
                                                                      text = "Category Page",
                                                                      view_class = "CategoryPage",
                                                                      view_template = "CategoryPage.html"
                                                                      )
                except MultipleObjectsReturned as e:

                    logger.warn("Multiple PageType: CATEGORY found. Database is inconsistent. Returning the first one found.")
                    pagetype_obj = CMSPageTypes.objects.filter(page_type="CATEGORY")[0]


                try:
                    entry_obj, c= CMSEntries.objects.get_or_create(page_type=pagetype_obj,
                                                                 path=path_obj,
                                                                 title="Yet Another CMS.")
                except MultipleObjectsReturned as e:
                    msg = "Multiple CMSEntries for /cms found. Database is inconsistent. Using the first one found. "
                    logger.warn(msg)

                    entry_obj = CMSEntries.objects.filter(path=path_obj)[0]



                obj = ViewObject(path=u"/")
                return obj
            else:
                
                #TODO: Make sure to log this too 
                raise Http404("Page Does Not Exist.")



    def get(self,request, **kwargs):
        """
        The main entry point to the frontend of the CMS. 
        All website user pages are obtained through this method."""
    
        get = request.GET
        
        toolbar = request.GET.get("toolbar", None)
        if toolbar and toolbar.upper() == "TRUE":
            request.session["show_toolbar"] = True
        elif toolbar and toolbar.upper() == "FALSE":
            request.session["show_toolbar"] = False
        
        #get object will load return an instance of mycms.view_handlers.ViewObject
        #which encapsulates the CMSEntry and all other operations on it. 
        obj = self.get_object(request, **kwargs)
        obj.request = request
        obj.show_toolbar = request.session.get("show_toolbar", False) 
        
        
        
        template = obj.template
        try:
            return render_to_response(template, {"view_object": obj})
        except Exception as e:
            # TODO: Make sure to log this
            
            msg = "Application Error {}".format(e)            
            return HttpResponse(content=bytes(msg, 'utf-8'), status=500)
    def post(self, request, **kwargs):
        print(request, kwargs)
        return HttpResponse("Not implemented")

    def put(self, request, **kwargs):
        print(request, kwargs)
        return HttpResponse("Not Implemented")




########################################################################
class  AssetsUploaderView(View):
    """Handles the uploading and deleting of images. Uses multiuploader AJAX plugin.
    made from api on: https://github.com/blueimp/jQuery-File-Upload
    """

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(AssetsUploaderView, self).dispatch(*args, **kwargs)

    def _mkdir(self,newdir):
        """Copied from http://code.activestate.com/recipes/82465-a-friendly-mkdir/ """
        """works the way a good mkdir should :)
            - already exists, silently complete
            - regular file in the way, raise an exception
            - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("a file with the same name as the desired " \
                          "dir, '%s', already exists." % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head):
                self._mkdir(head)
            #print "_mkdir %s" % repr(newdir)
            if tail:
                os.mkdir(newdir)

    #----------------------------------------------------------------------
    def  get(self, request, **kwargs):

        """
        We assume we have a GET
        According to https://github.com/blueimp/jQuery-File-Upload/wiki/Setup
        we have to return a list of the images in the dir as follows:



        {"files": [
          {
            "name": "picture1.jpg",
            "size": 902604,
            "url": "http:\/\/example.org\/files\/picture1.jpg",
            "thumbnailUrl": "http:\/\/example.org\/files\/thumbnail\/picture1.jpg",
            "deleteUrl": "http:\/\/example.org\/files\/picture1.jpg",
            "deleteType": "DELETE"
          },
          {
            "name": "picture2.jpg",
            "size": 841946,
            "url": "http:\/\/example.org\/files\/picture2.jpg",
            "thumbnailUrl": "http:\/\/example.org\/files\/thumbnail\/picture2.jpg",
            "deleteUrl": "http:\/\/example.org\/files\/picture2.jpg",
            "deleteType": "DELETE"
          }
        ]}
        """

        try:
            assets_dir = settings.YACMS_SETTINGS.get("ARTICLE_IMAGES_DIR")
        except AttributeError as e: 
            print("ARTICLE_IMAGES_DIR IS NOT CONFIGURED! Falling back to default.")
            assets_dir = os.path.join(settings.BASE_DIR, "static/assets")
    
        
        path = kwargs.get("path", None).lstrip("/")
        fullpath = pathlib.Path(pathlib.Path(assets_dir), path)

        files = []

        print(fullpath.as_posix())
        try:
            filenames = os.listdir(fullpath.as_posix())
        except OSError as e:
            return  JsonResponse({'files': []})

        for filename in filenames:

            p_filename = pathlib.Path(fullpath, filename)

            if not p_filename.is_dir():

                stat = os.stat(p_filename.as_posix())
                image_url =  url = "/static/assets/{}/{}".format(path, filename)
                thumbnail_url = "/static/assets/{}/thumbnails/{}".format(path, filename)
                delete_url = "/cms/{}/assets_manager/{}".format(path, filename)


                file_dict = { "name": filename ,
                              "size": stat.st_size,
                              "url": image_url,
                              "thumbnailUrl": thumbnail_url,
                              "deleteUrl": delete_url,
                              "deleteType": "DELETE" }

                files.append(file_dict)

        return JsonResponse({'files': files})


    #----------------------------------------------------------------------
    def  post(self, request, **kwargs):
        """"""
        return self.fileupload(request, **kwargs)


    def fileupload(self,request, **kwargs):

        mylock = threading.Lock()

        with mylock:
            from django.conf import settings
            assets_dir = settings.ASSETS_DIR
            path = kwargs.get("path", None).lstrip("/")

            fullpath = pathlib.Path(pathlib.Path(assets_dir), path)

            if not fullpath.exists():
                self._mkdir(fullpath.as_posix())
            elif not fullpath.is_dir():
                #Fix this to return a proper json response.
                return HttpResponse("Error. Not full dir")

            thumbnailpath = pathlib.Path(fullpath, "thumbnails")

            if not thumbnailpath.exists():
                os.makedirs(thumbnailpath.as_posix())
            elif not thumbnailpath.is_dir():
                #Fix this to return a proper json response.
                return HttpResponse("Error. Not full dir")

            if request.method == "POST":
                uploaded_file = request.FILES.get("files[]")

                filename = uploaded_file.name

                p_filename = pathlib.Path(fullpath, filename)

                with open(p_filename.as_posix(), 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                #Now do the thumbail.
                try:
                    size = 256, 256
                    outfile =  pathlib.Path(thumbnailpath, filename)
                    im = Image.open(p_filename.as_posix())
                    im.thumbnail(size, Image.ANTIALIAS)
                    im.save(outfile.as_posix())
                except IOError as e:
                    print(e)
                    return JsonResponse( { "error" : "cannot create thumbnail for {}".format(outfile)})

                except Exception as e:
                    return JsonResponse( { "error": "Unhandled exception: {}".format(outfile) })



                stat = os.stat(p_filename.as_posix())
                image_url =  url = "/static/assets/{}/{}".format(path, filename)
                thumbnail_url = "/static/assets/{}/thumbnails/{}".format(path, filename)
                delete_url = "/cms/{}/assets_manager/{}".format(path, filename)

                files = []
                file_dict = { "name": filename ,
                                  "size": stat.st_size,
                                  "url": image_url,
                                  "thumbnailUrl": thumbnail_url,
                                  "deleteUrl": delete_url,
                                  "deleteType": "DELETE" }

                files.append(file_dict)
                
                return JsonResponse({'files': files})

    #----------------------------------------------------------------------
    def  delete(self,request, **kwargs):
        """"""
        path = kwargs.get("path", None).lstrip("/")
        filename=kwargs.get("filename",None).lstrip("/")
        fullpath = pathlib.Path(pathlib.Path(ASSETS_DIR), path)


        p_filename = pathlib.Path(fullpath, filename)

        logger.debug("Going to delete, {}".format(p_filename.as_posix()))

        """We need to return a format as below:
            {"files": [
              {
                "picture1.jpg": true
              },
              {
                "picture2.jpg": true
              }
            ]}
            """

        try:

            os.remove(p_filename.as_posix())

            files = [ { filename: True }]

            return JsonResponse({ 'files': files} )

        except Exception as e:


            return HttpResponse("Deleted")

#class PictureCreateView(CreateView):
    #model = Picture
    #fields = "__all__"

    #def form_valid(self, form):
        #self.object = form.save()
        #files = [serialize(self.object)]
        #data = {'files': files}
        #response = JSONResponse(data, mimetype=response_mimetype(self.request))
        #response['Content-Disposition'] = 'inline; filename=files.json'
        #return response

    #def form_invalid(self, form):
        #data = json.dumps(form.errors)
        #return HttpResponse(content=data, status=400, content_type='application/json')

#class BasicVersionCreateView(PictureCreateView):
    #template_name_suffix = '_basic_form'


#class BasicPlusVersionCreateView(PictureCreateView):
    #template_name_suffix = '_basicplus_form'


#class AngularVersionCreateView(PictureCreateView):
    #template_name_suffix = '_angular_form'


#class jQueryVersionCreateView(PictureCreateView):
    #template_name_suffix = '_jquery_form'


#class PictureDeleteView(DeleteView):
    #model = Picture

    #def delete(self, request, *args, **kwargs):
        #self.object = self.get_object()
        #self.object.delete()
        #response = JSONResponse(True, mimetype=response_mimetype(request))
        #response['Content-Disposition'] = 'inline; filename=files.json'
        #return response


#class PictureListView(ListView):
    #model = Picture

    #def render_to_response(self, context, **response_kwargs):
        #files = [ serialize(p) for p in self.get_queryset() ]
        #data = {'files': files}
        #response = JSONResponse(data, mimetype=response_mimetype(self.request))
        #response['Content-Disposition'] = 'inline; filename=files.json'
        #return response


from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import os


class TemplateSampleLoader(View):

    def get(self, request, **kwargs):

        template_name = kwargs.get("template", None)

        if template_name:
            return render(request, "{}".format(template_name))
        else:
            #Return a list of html files in bootstrap_templates

            bootstrap_examples_dir = os.path.join(settings.BASE_DIR, "templates/")

            files = []
            for filename in os.listdir(path=bootstrap_examples_dir):
                if filename.endswith(".html"):
                    files.append(filename)

            return render(request, "bootstrap_templates.html", { "files": files})



class LogoViewer(View):

    
    pass



class CMSPreviewAPIView(View):
    
    def get(self, request):
        raise NotImplementedError("This method is not supported")
        
    def post(self, request):
        #We expect to recieve unformatted text and we shall 
        #return it formatted.
        
        #For now it is assumed this is Creole 
        pass
        
    
    
class CMSEntriesContentAreaFilter(forms.Form):
    pass
    
    
class CMSUserContentArea(View):
    """This is a list view with filter."""
    
    
    def get(self, request):
        
    
    
        return render(request, "mycms/CMSUserContentArea.html")
    
    
