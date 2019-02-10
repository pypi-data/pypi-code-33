"""
The module mycms.api is a DRF based api which allows REST calls into the CMS contents stored
in the mycms database. The REST API documentation and interface can be reached at /cms/api/v2/docs/ of a mycms instance.

The web interface to the api exposes all the possible operations that we can do to the MyCMS database and is the
best way for understanding and testing the various api calls.

The API exposes the following endpoints:

* cmsauthtoken

* cmscontents

* cmsentries

* cmspages

* cmspaths



Tutorials
**********

Create a new CMSEntry using javascript
---------------------------------------

Introduction and Some Background:

Every mycms page defines a view_json object which contains information about the page. This can be seen in the html page
for example:

.. code-block:: javascript

    var view_json = {"id": 1, "title": "Yet Another CMS.", "path": 1, "slug": "yet-another-cms", "page_type": 5, "template": null, "frontpage": false, "published": true, "lists_include": false, "page_number": 1, "created_by": 1, "logo_url": "/static/mycms/images/png/default.png", "path_str": "/", "content": [], "date_created_epoch": 1460237699000, "date_modified_epoch": 1460237699000}


In order to create a CMSEntry we use the endpoint /cms/api/v2/cmsentries/id/create_child/ where id is the parent of the page we want to create.

"""


from django.core.exceptions import ObjectDoesNotExist

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework import serializers

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import views as drf_views
from rest_framework import status
from rest_framework.views import APIView

from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route

from rest_framework.authtoken.models import Token

from mycms.serializers import CMSPageTypesSerializer
from mycms.serializers import CMSContentsSerializer
from mycms.serializers import CMSEntrySerializer
from mycms.serializers import CMSMarkUpSerializer
from mycms.serializers import CMSTemplatesSerializer
from mycms.serializers import CMSPathsSerializer
from mycms.serializers import CMSEntryExpandedSerializer
from mycms.serializers import LoremIpsumSerializer
from mycms.serializers import CMSChildEntrySerializer

import mycms.serializers as mycmsserializers

from mycms.models import CMSContents
from mycms.models import CMSMarkUps
from mycms.models import CMSTemplates
from mycms.models import CMSPageTypes
from mycms.models import CMSEntries
from mycms.models import CMSPaths

from rest_framework.schemas import AutoSchema, ManualSchema
import coreapi
import coreschema


from django_filters.rest_framework import DjangoFilterBackend
__all__ = [ "CMSContentsViewSet",
            "CMSFormatterContent",
            "CMSEntriesViewSet"]



class CMSContentsViewSet(viewsets.ModelViewSet):
    """
    A viewset that allows
    """
    permission_classes = (IsAuthenticated,)

    queryset = CMSContents.objects.all()
    serializer_class =  CMSContentsSerializer

    @detail_route(methods=["get"])
    def html(self, request, pk=None):

        content_obj =CMSContents.objects.get(id=pk)
        data = { "html": content_obj.html}
        return Response( data, status=status.HTTP_200_OK)


class CMSFormatterContent(APIView):

    def get(self, request, **kwargs):

        content_id = kwargs.get("content_id")

        content_obj =CMSContents.objects.get(id=content_id)
        data = { "html": content_obj.html}
        data = { "html": "Use the new html action of CMSContents."}
        return Response( data, status=status.HTTP_200_OK)

class CMSEntriesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)


    serializer_class =  CMSEntrySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('page_type',"frontpage","published")

    def get_queryset(self):

        queryset = CMSEntries.objects.all()

        parent_path_id = self.request.query_params.get('parent_path_id', None)

        if parent_path_id is not None:
            queryset = queryset.filter(path__parent=parent_path_id)
        return queryset

    @detail_route(methods=["get"])
    def get_categories(self, request, pk=None):
        parent_obj = CMSEntries.objects.get(id=pk)
        print(parent_obj)
        c = CMSEntries.objects.filter(path__parent=parent_obj.path, page_type__page_type="CATEGORY")
        serializer =  CMSEntrySerializer(c, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=["post"])
    def create_child(self, request, pk=None):
        """
        A utility function to create an article including path information.
        """

        serializer = CMSChildEntrySerializer(data=request.data)

        if serializer.is_valid():
            print(serializer.data)
            vd = serializer.validated_data


            #The CMSChildEntrySerializer expects to get the pk of
            #the parent.
            child_obj = serializer.create(vd, pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CMSPathsViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    queryset = CMSPaths.objects.all()
    serializer_class =  CMSPathsSerializer



class CMSPagesViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated,)
    queryset = CMSEntries.objects.all()
    serializer_class =  mycmsserializers.CMSPageSerializer


class CMSContentPreview(viewsets.GenericViewSet):
    """Implements API endpoint to preview a page."""

    #from rest_framework.schemas.inspectors import AuthoSchema
    schema = ManualSchema(fields=[
           coreapi.Field(
               "content",
               required=True,
               location="form",
               schema=coreschema.String(description= "The raw content that needs to be formatted."),

           )
           
       ], description="Retrieves the Creole formatted content of what is posted.")


    #def get(self, request):

        #if request.user.is_authenticated:

            #token =


    def retrieve(self, request, **kwargs):

        content = request.data.get("content", None)
       
        if content:
            from mycms.view_handlers.formatters import CreoleFormatter
            content =  CreoleFormatter(content).html()
            return Response(data={"content" : content},\
                            status=status.HTTP_200_OK)

        else:
            return Response(data={"error": "No Content"}, status=status.HTTP_400_BAD_REQUEST)



    

class CMSAuthToken(viewsets.GenericViewSet):
    """Implements retrieving of Token."""

    #permission_classes = (IsAuthenticated,)

    #from rest_framework.schemas.inspectors import AuthoSchema
    schema = ManualSchema(fields=[
           coreapi.Field(
               "username",
               required=True,
               location="form",
               schema=coreschema.String(description= "username required to create or retrieve token"),

           ),
           coreapi.Field(
               "password",
               required=True,
               location="form",
               schema=coreschema.String(description="password required to create or retrieve token"),
           ),
           coreapi.Field(
               "renew",
               required=False,
               location="query",
               schema=coreschema.Boolean(description= "set to true to retrieve a new token invalidating old one if it exists."),
               description="password required to create or retrieve token"

           )
       ], description="Gets or Creates a Token for the given user.")


    #def get(self, request):

        #if request.user.is_authenticated:

            #token =


    def retrieve(self, request, **kwargs):

        username = request.data.get("username", None)
        password = request.data.get("password", None)
        renew = request.data.get("renew", False)
        """Returns token for logged in user."""


        if request.user.is_authenticated:
            if renew:
                try:
                    token = Token.objects.get(user=request.user)
                    token.delete()
                except ObjectDoesNotExist as e:
                    #Nothing to renew
                    pass

            token, created = Token.objects.get_or_create(user=request.user)
            return Response(data={"token" : token.key},\
                            status=status.HTTP_200_OK)

        else:
            return Response(data={"error": "Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)
