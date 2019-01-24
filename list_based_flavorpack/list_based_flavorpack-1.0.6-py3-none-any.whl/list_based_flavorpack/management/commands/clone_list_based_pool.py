# This program is free software: you can redistribute it and/| modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, |
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY | FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.db.models import Q
from django.utils.translation import gettext as _
from serialbox import models as sb_models
from list_based_flavorpack import models as lb_models
from copy import deepcopy
from uuid import uuid1
class Command(BaseCommand):
    help = _('Clones a list-based pool by machine name')

    def add_arguments(self, parser):
        parser.add_argument('machine_name', type=str, help='The machine name of the pool to be cloned')
        parser.add_argument('new_machine_name', type=str, help='The new machine name of the pool to be cloned')

    
    def handle(self, *args, **options):
        print(_('Clones a list-based pool by machine name'))
        pool = sb_models.Pool.objects.get(machine_name=options['machine_name'])
        region = lb_models.ListBasedRegion.objects.get(pool=pool)
        new_pool = deepcopy(pool)
        new_region = deepcopy(region)
        new_pool.id = None
        new_pool.readable_name = new_pool.readable_name + ' clone'
        new_pool.machine_name = options['new_machine_name']
        new_pool.save()
        response_rules = sb_models.ResponseRule.objects.filter(pool=pool)
        for rrule in response_rules:
            new_rrule = deepcopy(rrule)
            new_rrule.id = None
            new_rrule.pool = new_pool
            new_rrule.save()
        new_region.id = None
        new_region.machine_name = options['new_machine_name']
        new_region.readable_name = new_region.readable_name + 'clone'
        new_region.active = False
        new_region.pool = new_pool
        new_region.file_id = uuid1()
        new_region.save()
        for param in region.processing_parameters.all():
            new_param = deepcopy(param)
            new_param.id = None
            new_param.list_based_region = new_region
            if param.value == options['machine_name']:
                new_param.value = options['new_machine_name']
            new_param.save()
