import pytz


def get_field_names(cls, *fields_cls):
    attr_list = {
        field_class.creation_counter: name
        for name, field_class in cls.fields().items()
    }
    return [attr_list[field_cls.creation_counter] for field_cls in fields_cls]


def change_field_class(ad_hoc_model, field_name, new_field_class):
    model_cls = ad_hoc_model.__class__
    # Set new field class to fields dicts
    if field_name in ad_hoc_model._fields:
        model_cls._fields[field_name] = new_field_class
        if field_name in ad_hoc_model._writable_fields:
            model_cls._writable_fields[field_name] = new_field_class
        # Update default value
        model_cls._defaults[field_name] = new_field_class.to_python(new_field_class.default, pytz.UTC)
        # Set new field class to model class
        setattr(model_cls, field_name, new_field_class)
        # Set attr value to attr for triggering field conversion/validation
        setattr(ad_hoc_model, field_name, getattr(ad_hoc_model, field_name))