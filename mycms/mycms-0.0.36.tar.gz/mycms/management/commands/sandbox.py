from django.core.management.base import BaseCommand, CommandError
from mycms.models import CMSEntries


from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

from mycms.view_handlers.page_types import singlepageview_pagetype_obj
from mycms.view_handlers.page_types import multipageview_pagetype_obj
from mycms.view_handlers.page_types import allarticles_pagetype_obj


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'


    def handle(self, *args, **options):
        
        from django.db.models import Q
        
        c = CMSEntries.objects.get(path__path="/sysadmin/linux")
        
        print(c)
        obj_list = CMSEntries.objects.filter((Q(page_type = singlepageview_pagetype_obj) | 
                                              Q(page_type = multipageview_pagetype_obj)) &
                                             Q(path__path__startswith =  c.path.path))        
        
        
        
        for obj in obj_list:
            print(obj.path)
    
    