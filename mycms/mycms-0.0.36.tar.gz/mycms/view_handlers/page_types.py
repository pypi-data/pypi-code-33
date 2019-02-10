from mycms.models import CMSEntries
from mycms.models import CMSPageTypes
from mycms.view_handlers.mycms_view import ViewObject

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import OperationalError

import logging
logger = logging.getLogger("mycms.page_handlers")

try:

    try:
        singlepageview_pagetype_obj, c = obj = CMSPageTypes.objects.get_or_create(page_type = "SINGLEPAGE",
                                                     text = "Single Page HTML",
                                                     view_class = "SinglePage",
                                                     view_template = "SinglePage.html")

    except ObjectDoesNotExist as e:
        singlepageview_pagetype_obj = CMSPageTypes( page_type = "SINGLEPAGE",
                                                     text = "Single Page HTML",
                                                     view_class = "SinglePage",
                                                     view_template = "SinglePage.html")
        singlepageview_pagetype_obj.save()

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSPageTypes : SINGLEPAGE. Database is inconsistent, Will return the first one. "
        logger.warn(msg)

        singlepageview_pagetype_obj = CMSPageTypes.objects.filter(page_type="SINGLEPAGE")[0]


    try:
        categorypageview_pagetype_obj = CMSPageTypes.objects.get(page_type="CATEGORY")

    except ObjectDoesNotExist as e:

        msg = "Could not load CATEGORY view object. Going to create it."
        logger.debug(msg)
        pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="CATEGORY",
                                                         text = "Category Page",
                                                         view_class = "CategoryPage",
                                                         view_template = "CategoryPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSPageType: CATEGORY. Database is inconsistent. Will return the first one."
        logger.info(msg)

        categorypageview_pagetype_obj = CMSPageTypes.objects.filter(page_type="CATEGORY")[0]

    try:
        multipageview_pagetype_obj = CMSPageTypes.objects.get(page_type="MULTIPAGE")

    except ObjectDoesNotExist as e:

        msg = "Could not load MULTIPAGE view object. Going to create it."
        logger.debug(msg)
        multipageview_pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="MULTIPAGE",
                                                         text = "MultPage Article",
                                                         view_class = "MultiPage",
                                                         view_template = "MultiPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSMultiPageType: MULTIPAGE. Database is inconsistent. Will return the first one."
        logger.info(msg)

        multipageview_pagetype_obj = CMSMultiPageTypes.objects.filter(page_type="MULTIPAGE")[0]


    #MULTIPAGE

    try:
        memberpageview_pagetype_obj = CMSPageTypes.objects.get(page_type="MEMBERPAGE")

    except ObjectDoesNotExist as e:

        msg = "Could not load MULTIPAGE view object. Going to create it."
        logger.debug(msg)
        pagetype_obj, _ = CMSPageTypes.objects.get_or_create(page_type="MEMBERPAGE",
                                                         text = "MemberPage Article",
                                                         view_class = "MemberPage",
                                                         view_template = "MemberPage.html"
                                                         )

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSMultiPageType: MULTIPAGE. Database is inconsistent. Will return the first one."
        logger.info(msg)

        memberpageview_pagetype_obj = CMSMultiPageTypes.objects.filter(page_type="MEMBERPAGE")[0]


        
    try:
        allarticles_pagetype_obj, c = obj = CMSPageTypes.objects.get_or_create(page_type = "ALLARTICLES",
                                                     text = "All Articles ",
                                                     view_class = "AllArticlesPage",
                                                     view_template = "AllArticlesPage.html")

    except ObjectDoesNotExist as e:
        allarticles_pagetype_obj = CMSPageTypes( ppage_type = "ALLARTICLES",
                                                     text = "All Articles ",
                                                     view_class = "AllArticlesPage",
                                                     view_template = "AllArticlesPage.html")
        allarticles_pagetype_obj.save()

    except MultipleObjectsReturned as e:
        msg = "Got more than 1 CMSPageTypes : SINGLEPAGE. Database is inconsistent, Will return the first one. "
        logger.warn(msg)

        allarticles_pagetype_obj = CMSPageTypes.objects.filter(page_type="ALLARTICLES")[0]


except OperationalError as e:
    #This can happen only when the database is not yet initialized.
    pass

