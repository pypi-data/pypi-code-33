from django.apps import apps as django_apps


class ListdataTestHelper:

    list_data = None

    def load_list_data(self, label_lower):
        objs = []
        model = django_apps.get_model(*label_lower.split('.'))
        for name in self.list_data.get(label_lower):
            objs.append(model(name=name, short_name=name))
        model.objects.bulk_create(objs)
