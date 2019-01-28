from django.db import models


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
    
    
    
class ModelConstraintsOne(CommonColumns):
    class Meta:
        db_table = 'model_constraints_one'
        
    f_text = models.TextField(null=False)
    f_integer = models.IntegerField(null=True, unique=True)
    f_string = models.CharField(max_length=255, null=False, unique=True)
    
    # `two_1_x`, `three_1_x` and `five_1_1` configured on the other side
        


class ModelConstraintsTwo(CommonColumns):
    class Meta:
        db_table = 'model_constraints_two'
        
    one_x_1 = models.ForeignKey(
        'ModelConstraintsOne',
        on_delete=models.CASCADE,
        related_name='two_1_x',
        null=True)
    
    # Django does not support composite primary key
    four_x_1 = models.ForeignKey(
        'ModelConstraintsFour',
        on_delete=models.CASCADE,
        related_name='two_1_x',
        null=False)
    
    # `three_x_x` configured on the other side
    
    

class ModelConstraintsThree(CommonColumns):
    class Meta:
        db_table = 'model_constraints_three'
        
    one_x_1 = models.ForeignKey(
        'ModelConstraintsOne',
        on_delete=models.CASCADE,
        related_name='three_1_x',
        null=False)
    
    two_x_x = models.ManyToManyField(
        'ModelConstraintsTwo',
        related_name='three_x_x')
    
    four_x_1 = models.ForeignKey(
        'ModelConstraintsFour',
        on_delete=models.CASCADE,
        related_name='three_1_x',
        null=True)
    


class ModelConstraintsFour(CommonColumns):
    class Meta:
        db_table = 'model_constraints_four'
        unique_together = (('f_integer', 'f_string'),)
        
    # Django does not support composite primary key, it uses `id` by default

    # `two_1_x`, `three_1_x`, `five_1_1` configured on the other side



class ModelConstraintsFive(CommonColumns):
    class Meta:
        db_table = 'model_constraints_five'
    
    one_1_1 = models.OneToOneField(
        'ModelConstraintsOne',
        on_delete=models.CASCADE,
        related_name='five_1_1',
        null=True)
    
    four_1_1 = models.OneToOneField(
        'ModelConstraintsFour',
        on_delete=models.CASCADE,
        related_name='five_1_1',
        null=True)
    
    # `six_1_1` configured on the other side



class ModelConstraintsSix(CommonColumns):
    class Meta:
        db_table = 'model_constraints_six'
        unique_together = (('five_1_1', 'f_integer'),)
        
    five_1_1 = models.OneToOneField(
        'ModelConstraintsFive',
        on_delete=models.CASCADE,
        related_name='six_1_1',
        null=False)
        
        
        
class ModelConstraintsSelf(CommonColumns):
    class Meta:
        db_table = 'model_constraints_self'
    
    # using non-standard primary key
    code = models.CharField(max_length=255, primary_key=True)
        
    # many-to-one, not_null
    parent_x_1 = models.ForeignKey(
        'ModelConstraintsSelf',
        on_delete=models.CASCADE,
        related_name='child_1_x',
        null=False)
    
    # self one-to-one, unique
    first_parent_1_1 = models.OneToOneField(
        'ModelConstraintsSelf',
        on_delete=models.CASCADE,
        related_name='first_child_1_1',
        null=True)
    
    # self one-to-one, unique, not_null
    second_parent_1_1 = models.OneToOneField(
        'ModelConstraintsSelf',
        on_delete=models.CASCADE,
        related_name='second_child_1_1',
        null=False)
    
    # self many-to-many
    parent_x_x = models.ManyToManyField(
        'ModelConstraintsSelf',
        related_name='child_x_x')



    
    