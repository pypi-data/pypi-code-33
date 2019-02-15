from django.db import models



class ModelFieldTypes(models.Model):
    
    class Meta:
        db_table = 'model_field_types'
        
    binary_1 = models.BinaryField(db_column='new_binary_1')
    
    string_1 = models.CharField(db_column='new_string_1', max_length=255)
    
    text_1 = models.TextField(db_column='new_text_1')
    
    integer_1 = models.IntegerField(db_column='new_integer_1')
    integer_2 = models.BigIntegerField(db_column='new_integer_2')
    integer_3 = models.PositiveIntegerField(db_column='new_integer_3')
    integer_4 = models.PositiveSmallIntegerField(db_column='new_integer_4')
    integer_5 = models.SmallIntegerField(db_column='new_integer_5')
    
    boolean_1 = models.BooleanField(db_column='new_boolean_1')
    boolean_2 = models.NullBooleanField(db_column='new_boolean_2')
    
    float_1 = models.FloatField(db_column='new_float_1')
    float_2 = models.DecimalField(db_column='new_float_2',
                                  max_digits=12, decimal_places=3)
    
    date_1 = models.DateField(db_column='new_date_1')
    
    time_1 = models.TimeField(db_column='new_time_1')
    
    datetime_1 = models.DateTimeField(db_column='new_datetime_1')
