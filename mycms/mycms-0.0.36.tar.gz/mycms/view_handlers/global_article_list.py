from mycms.models import CMSEntries
from mycms.models import CMSPageTypes
from mycms.view_handlers.mycms_view import ViewObject
from mycms.view_handlers.mycms_view import ArticleList

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import OperationalError

import logging
logger = logging.getLogger("mycms.page_handlers")


# #####################
# We ensure that the base page types are already created.
# #####################


from . page_types import singlepageview_pagetype_obj
from . page_types import multipageview_pagetype_obj
from . page_types import allarticles_pagetype_obj

class AllArticlesPage(object):

    def __init__(self, page_object, request=None):
        self.page_object = page_object
        self.request = request
        self._article_list = None


    def articles(self):

        """Here we load all pages that says we are their parent."""

        from django.db.models import Q

        
        # ######################################################################
        # This loads up all the articles that are 
        # of type single_page or multipage and has the provided parent. 
       
        if self.request: 
            try: 
                limit = int(self.request.GET.get("limit",10))
            except Exception as e: 
                #this can only happen if we got a bad limit value such as a non 
                #integer value.Set limit to a sane value.
                limit = 10
            
            try: 
                offset = int(self.request.GET.get("offset", 0))
            except Exception as e: 
                #same reason as above
                offset = 0
                
        else:
            limit = 10
            offset = 0
        
        #We only recalculate if the limit and offset has changed. 
        
        
        # prepare the article list. 
        
        if  ((self._article_list is None) or 
             (limit != self._article_list.limit) or
             (offset != self._article_list.offset)):
        
            # the above "if" works because the first boolean tests if 
            #self._article_list is None and the rest are not evaluated further. 
            
            #This is a lame attempt at ensuring that multple calls to article 
            #is avoided by caching the results so that when processing the 
            #template we do not need to execute this code any further. 
            
            self._article_list = ArticleList()
            self._article_list.limit = limit
            self._article_list.offset = offset
            
            obj_list = CMSEntries.objects.filter(
                                                 (Q(page_type = singlepageview_pagetype_obj ) | 
                                                  Q(page_type = multipageview_pagetype_obj)
                                                  ) &
                                                  Q( lists_include = True)
                                                 )[offset:offset+limit + 1]
            
            num_results = obj_list.count()
            if num_results > limit: 
                #this mean we have more. 
                self._article_list.has_older = True
            else:
                self._article_list.has_older = False
                
            if offset == 0 : 
                self._article_list.has_newer = False
            else:
                self._article_list.has_newer = True
            
            for obj in obj_list:
                self._article_list.append(ViewObject(page_object=obj))

        
        return self._article_list

    def get_categories(self):
        """Returns a list of all child categories of type: CATEGORY"""

        obj_list = CMSEntries.objects.filter(path__path__parent__id = self.page_object.id,
                                             page_type=page_obj.page_type)

        return obj_list



    def page_types(self):

        """
        Refactor me into a parent class.
        returns a list fo page_types
        """


        pagetype_objs = CMSPageTypes.objects.all()

        return pagetype_objs


    def on_create(self):
        pass
