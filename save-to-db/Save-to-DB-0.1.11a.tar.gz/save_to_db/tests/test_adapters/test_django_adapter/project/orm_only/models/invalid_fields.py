from django.db import models


# this model must not get into Django migrations as it contains "__" in it's
# name
class ModelInvalidFieldNames(models.Model):
    class Meta:
        db_table = 'model_invalid_field_names'
        
    f__integer = models.IntegerField(null=True)

