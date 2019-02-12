# -*- coding: utf-8 -*-
# #!/usr/bin/env python
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eeapp.settings")
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


# from seller.models_locations import Area
# from seller.models_seller import Shop,ShopAdmin
import django
if django.VERSION >= (1, 7):
    django.setup()
# s = Shop.objects.get(pk='4')
# print s


#!/usr/bin/env python

# import sys
# import os
#

# # print e
#
# a = float('12.0')
# print a



class ChinaLocCreater:
    def __init__(self, province, city, area):
        self.province = province
        self.city = city
        self.area = area

    def provinces(self):
        from location.models import Province
        if Province.objects.all().count() < 1:
            f = open(self.province)
            for line in f:
                a, b = line.split('@@@@')
                Province.objects.create(
                    province_id=a.strip().lstrip(), province=b)
            f.close()

    def citys(self):
        from location.models import City, Province
        if City.objects.all().count() < 1:
            f = open(self.city)
            for line in f:
                a, b, c = line.split('@@@@')
                try:
                    father = Province.objects.get(
                        province_id=c.strip().lstrip())
                    City.objects.create(
                        city_id=a.strip().lstrip(), city=b, father=father)
                except:
                    print(line)
            f.close()

    def areas(self):
        from location.models import City, Area
        if Area.objects.all().count() < 1:
            f = open(self.area)
            for line in f:
                a, b, c = line.split('@@@@')
                try:
                    father = City.objects.get(city_id=c.strip().lstrip())
                    Area.objects.create(
                        area_id=a.strip().lstrip(), area=b, father=father)
                except:
                    print(line)
            f.close()

    def importData(self):
        self.provinces()
        self.citys()
        self.areas()


file_path = os.path.join(settings.BASE_DIR, 'location/static/location/chinese')
p = file_path + '/province.txt'
c = file_path + '/city.txt'
a = file_path + '/area.txt'

ChinaLocCreater(province=p, city=c, area=a).importData()
