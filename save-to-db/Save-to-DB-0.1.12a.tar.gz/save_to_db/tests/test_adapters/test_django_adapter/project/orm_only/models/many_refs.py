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
    

class ModelManyRefsOne(CommonColumns):
    class Meta:
        db_table = 'model_many_refs_one'
    
    two_x_1_a = models.ForeignKey(
        'ModelManyRefsTwo',
        on_delete=models.CASCADE,
        related_name='one_1_x_a',
        null=True)
    
    two_x_x_a = models.ManyToManyField(
        'ModelManyRefsTwo',
        related_name='one_x_x_a')
    
    two_1_1_a = models.OneToOneField(
        'ModelManyRefsTwo',
        on_delete=models.CASCADE,
        related_name='one_1_1_a',
        null=True)


class ModelManyRefsTwo(CommonColumns):
    class Meta:
        db_table = 'model_many_refs_two'
    
    one_x_1_b = models.ForeignKey(
        'ModelManyRefsOne',
        on_delete=models.CASCADE,
        related_name='two_1_x_b',
        null=True)
    
    one_x_x_b = models.ManyToManyField(
        'ModelManyRefsOne',
        related_name='two_x_x_b')
    
    one_1_1_b = models.OneToOneField(
        'ModelManyRefsOne',
        on_delete=models.CASCADE,
        related_name='two_1_1_b',
        null=True)