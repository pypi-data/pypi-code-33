from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import time

import logging
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils.text import slugify
import simplejson as json
import hashlib

from bs4 import BeautifulSoup


logger = logging.getLogger("mycms.view_handlers.ViewObject")

from . formatters import CreoleFormatter

class ArticleList(list):
    
    def __init__(self):
        super().__init__(self)
    
        self._next = None
        self._total_articles = None
        self._limit = 10
        self._offset = 0 
        self.has_newer = False
        self.has_older = False
        self.processed = False 
    @property
    def next_offset(self):
        return self.limit + self.offset
        
    @property
    def next(self):
        return self._next
    
    @next.setter
    def next(self, value):
        self._next = value
    
    @property 
    def total_articles(self):
        return self._total_articles
    
    @total_articles.setter
    def total_articles(self, value):
        self._total_articles = value
    
    @property 
    def limit(self):
        return self._limit 
    
    @limit.setter
    def limit(self,value):
        self._limit = value
    
    @property 
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self, value):
        self._offset = value


class ContentTopicsContainer(object):

    def __init__(self, title, anchor_text=None):

        self.title = title
        self._anchor_text = anchor_text

    @property
    def has_children(self):
        pass

    @property
    def children(self):
        """
        Returns a list of ContentTopics that exists below this content
        Topic
        """
        pass

    @property
    def anchor_text(self):

        return slugify(self.title)


class ViewObject(object):

    """
    A ViewObject represents a full page object. It takes care of
    coupling together the different pieces of a page such that it can
    be serialized.  The ViewObject handles the management of the
    attributes of the CMSEntry model.
    """
    
    def __init__(self, path=None, page_id=None, page_object=None, request=None):

        self.request = request
        
        if  page_object:
            # A page_object is a models.CMSEntries instance. 
            # 
            self.path = page_object.path.path
            self._page_id = page_object.id
            self._obj = page_object

        else:
            self.path = path
            self._page_id = page_id
            self._obj = None

        x = __import__("mycms.view_handlers")
        y = getattr(x, "view_handlers")
        
        #the view class take care of providing extra implementation that is 
        #needed in the page. vie_class is defined as an attribute inside the 
        #the database.
        # 
        # we provide it the page_object and 
        
        ViewClass  = getattr(y, self.page_object.page_type.view_class)
        instance =  ViewClass(self.page_object, request=self.request)
        self.view_handler = instance

    @property
    def DEBUG(self):
        return settings.DEBUG
    
    @property
    def FORCE_SHOW_ADVERTS(self):    
        return getattr(settings, "FORCE_SHOW_ADVERTS", False)
    
    @property
    def SHOW_ADVERTS(self):
        
        #We follow the settings on DEBUG unless a flag for 
        #FORCE_SHOW_ADVERTS has been set. 
        
        if self.FORCE_SHOW_ADVERTS :
            print("FORCE_SHOW_ADVERTS ")
            return True
        elif self.DEBUG == False:
            return True
        else:
            return False
    
    def __getattr__(self, name):
        """Maps values to attributes.
        Only called if there *isn't* an attribute with this name
        """
        obj = self.view_handler

        try:
            value = getattr(obj, name)
            return value

        except AttributeError as e:
            return None

    @property
    def page_object(self, reload=False):
        """
        Loads the database entry object. Raises PageDoesNotExist
        """

        if (self._obj is None) or (reload):
            from mycms.models import CMSEntries
            
            if self.path:
                if not self.path.startswith("/"):
                    self.path =   "/" + self.path

                try:
                    obj = CMSEntries.objects.get(path__path=self.path)
                except CMSEntries.MultipleObjectsReturned:
                    #Something is wrong with the database. It is inconsistent 
                    #and this is usually caused by having two pages with the same
                    #path. To resolve this, we take the newest one. 
                    
                    #TODO: Fix logging here too
                    
                    objs =  CMSEntries.objects.filter(path__path=self.path)
                    obj = objs[1]
                    
            
            elif self.page_id:
                obj = CMSEntries.objects.get(pk=self.page_id)
            else:
                raise RuntimeError("ViewObject did not get a path or page_id.")

            self._obj = obj
            return obj

        else:
            return self._obj



    @property
    def page_id(self):
        if self._page_id is None:
            self._page_id = self.page_object.id
        return self._page_id

    @page_id.setter
    def page_id(self, value):
        self._page_id = value

    @property
    def title(self):
        """The page title"""
        return self.page_object.title

    @property
    def created_timestamp(self):
        return self.page_object.date_created

    @property
    def path_id(self):
        return self.page_object.path.id

    @property
    def path_str(self):
        p = self.page_object.path.path
        return p

    @property
    def html_content(self):
        """The html content of the page. This formats the page
        using the CreoleFormatter"""

        logger.debug("html_content entered")

        #TODO: Fix me: This loads only the first content entry.
        #      This should be updated to load by date.

        try:
            content_obj = self.page_object.content.all()[0]
        except IndexError as e:

            if settings.DEBUG:
                msg = """We did not find a content_obj so returning a fake content since DEBUG is swithed on."""
                logger.debug(msg)
                return CreoleFormatter().html(fake_content=True)
            else:
                return "Error: There is no content for this page."

        #TODO: Fix me: right now hardcoded to creole.

        #We pass the view into our custom CreoleFormatter so that the
        #custom creole markup can have access.
        _html_content =  CreoleFormatter(content_obj.content,view=self).html()

        logger.debug("Call to YACMSObject.html_content returns: \n {}".format(_html_content))
        
        
        return _html_content
    
    
    @property
    def meta_keywords(self):
        """Returns a string list of keywords."""
        pass

    @property
    def meta_author(self):
        """Returns the author of the page."""
        pass


    @property
    def date_modified(self):
        """Date the page was modified"""
        pass

    @property
    def introduction(self):
        #We use beautifulsoup to extract the first paragraph
        html_content = self.html_content
        soup = BeautifulSoup(html_content)
        intro = soup.find("p")
        return str(intro.text)

    @property
    def template(self):

        #If self.page_object.template is empty, then we're fucked because
        #this will raise an AttributeError
        try:
            tmpl  = self.page_object.template.name
        except AttributeError as e:
            #no specific template defined so we just use the default template
            tmpl = self.page_object.page_type.view_template


        """
        TODO: Fix this so that it is not forcing to
        get templates from mycms and instead set another
        directory.
        """
        if not tmpl.startswith("mycms"):
            tmpl = "mycms/"+tmpl

        return tmpl


    @property
    def data(self):
        d =  model_to_dict(self.page_object, exclude="content")
        path_str = self.page_object.path.path
        d["path_str"] = path_str
        d["content"] = [x.id for x in self.page_object.content.all()]
        page_object = self.page_object
        
        #django model_to_dict ignores the datetime field.
        date_created = self.page_object.date_created
        date_created_epoch = int(time.mktime(date_created.timetuple())*1000)


        #django model_to_dict ignores the datetime field.
        date_modified = self.page_object.date_created
        date_modified_epoch = int(time.mktime(date_modified.timetuple())*1000)

        d["date_created_epoch"] = date_created_epoch
        d["date_modified_epoch"] = date_modified_epoch
        
        return d


    @property
    def json_data(self):
        
        try:
            value =  json.dumps(self.data)
            return value
        except Exception as e:
            print("fuck", e)
            return ""

    @property
    def get_absolute_url(self):
        cms_base_path = getattr(settings, "YACMS_BASEPATH", None)

        if not cms_base_path:
            cms_base_path = "/cms"

        if not cms_base_path.endswith("/"):
            cms_base_path = cms_base_path.rstrip("/")

        #we assume here that self.path.path will always start with a /
        abs_url =  "{}{}".format(cms_base_path, self.page_object.path.path)
        return abs_url

        
    @property
    def title_sha1sum(self):
        #TODO: fix this so that it is cached.
        hash_object = hashlib.md5(self.title.encode('utf-8'))
        return hash_object.hexdigest()
        

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value):
        self._request = value

    @property
    #----------------------------------------------------------------------
    def  slug(self):
        """"""
        return self.page_object.slug


    #----------------------------------------------------------------------
    def  timestamp(self):
        """"""
        pass

    #----------------------------------------------------------------------
    def created_timestamp_str(self):
        """"""
        return self.page_object.date_created.strftime("%Y/%m/%d %H:%M")


    #----------------------------------------------------------------------
    def modified_timestamp_str(self):
        """"""
        return self.page_object.date_modified.strftime("%Y/%m/%d %H:%M")

    #----------------------------------------------------------------------
    def  id(self):
        """
        Returns the id of the curren cms_entry
        """
        _id = self.page_object.id
        return _id


    def parent_entries_list(self):

        return self.page_object.parents_list()

    def content_topics(self):
        #Get all H1 entries from the page.
        soup = BeautifulSoup(self.html_content)
        x = soup.findAll("h1", class_ = "multipage-submenu-h1" )

        y = []
        for z in x:
            y.append(ContentTopicsContainer(z.text))
        return y

    #def on_create(self):
    #    pass

class MenuEntry(object):

    def __init__(self, cmspath):
        self.path = cmspath


    def entries(self):
        pass



    def expand(self):
        pass


