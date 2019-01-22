from django.db import models
from save_to_db.adapters.utils.relation_type import RelationType


class CommonColumns(models.Model):
    class Meta:
        abstract = True
        
    f_binary = models.BinaryField(null=True)
    f_boolean = models.NullBooleanField(null=True)
    f_string = models.CharField(max_length=255, null=True)
    f_text = models.TextField(null=True)
    f_integer = models.IntegerField(null=True)
    f_float = models.FloatField(null=True)
    f_date = models.DateField(null=True)
    f_time = models.TimeField(null=True)
    f_datetime = models.DateTimeField(null=True)
    

class ModelAutoReverseOne(CommonColumns):
    
    class Meta:
        db_table = 'model_auto_reverse_one'
        
    ITEM_RELATIONS = {
        'two_a_1_1': ('modelautoreverseone', RelationType.ONE_TO_ONE),
        'two_b_1_1': (None, RelationType.ONE_TO_ONE),
        'three_a_x_1': ('modelautoreverseone_set', RelationType.MANY_TO_ONE),
        'three_b_x_1': (None, RelationType.MANY_TO_ONE),
        'four_a_x_x': ('modelautoreverseone_set', RelationType.MANY_TO_MANY),
        'four_b_x_x': (None, RelationType.MANY_TO_MANY),
    }
    
    #--- one-to-one ---
    
    # related name auto configured
    two_a_1_1 = models.OneToOneField(
        'ModelAutoReverseTwoA',
        on_delete=models.CASCADE,
        null=True)
    
    # no related_name
    two_b_1_1 = models.OneToOneField(
        'ModelAutoReverseTwoB',
        on_delete=models.CASCADE,
        related_name='+',
        null=True)
    
    #--- one-to-many ---
    
    # related name auto configured
    three_a_x_1 = models.ForeignKey(
        'ModelAutoReverseThreeA',
        on_delete=models.CASCADE,
        null=True)
    
    # no related_name
    three_b_x_1 = models.ForeignKey(
        'ModelAutoReverseThreeB',
        on_delete=models.CASCADE,
        related_name='+',
        null=True)
    
    #--- many-to-many ---
    
    # related name auto configured
    four_a_x_x = models.ManyToManyField(
        'ModelAutoReverseFourA')
    
    # no related_name
    four_b_x_x = models.ManyToManyField(
        'ModelAutoReverseFourB',
        related_name='+')

class ModelAutoReverseTwoA(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_two_a'
    ITEM_RELATIONS = {'modelautoreverseone': ('two_a_1_1',
                                              RelationType.ONE_TO_ONE)}
    
class ModelAutoReverseTwoB(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_two_b'
    ITEM_RELATIONS = {}

class ModelAutoReverseThreeA(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_thee_a'
    ITEM_RELATIONS = {'modelautoreverseone_set': ('three_a_x_1', 
                                                  RelationType.ONE_TO_MANY)}

class ModelAutoReverseThreeB(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_thee_b'
    ITEM_RELATIONS = {}
    
class ModelAutoReverseFourA(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_four_a'
    ITEM_RELATIONS = {'modelautoreverseone_set': ('four_a_x_x',
                                                  RelationType.MANY_TO_MANY)}
    
class ModelAutoReverseFourB(CommonColumns):
    class Meta:
        db_table = 'model_auto_reverse_four_b'
    ITEM_RELATIONS = {}