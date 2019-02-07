from django.apps import apps


def apply_update(data):
    models = apps.get_app_config("glossary").get_models()
    models = sorted(models, key=lambda m: m.get_foreign_key_count())
    for model in models:
        records = data[model._meta.model_name]
        for record in records:
            uuid = record["uuid"]
            obj_data = model.clean_dump_data(record)

            try:
                model.all_objects.get(uuid=uuid)
                model.all_objects.filter(uuid=uuid).update(**obj_data)
            except model.DoesNotExist:
                model.all_objects.create(**obj_data)

