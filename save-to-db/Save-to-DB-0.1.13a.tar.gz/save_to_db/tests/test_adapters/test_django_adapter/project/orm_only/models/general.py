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


class ModelGeneralOne(CommonColumns):
    
    class Meta:
        db_table = 'model_general_one'
        
    #--- self relations ---
    
    # self one-to-one
    parent_1_1 = models.OneToOneField(
        'ModelGeneralOne',
        on_delete=models.CASCADE,
        related_name='child_1_1',
        null=True)
    
    # self one-to-many and many-to-one
    parent_x_1 = models.ForeignKey(
        'ModelGeneralOne',
        on_delete=models.CASCADE,
        related_name='child_1_x',
        null=True)
    
    # self many-to-many
    parent_x_x = models.ManyToManyField(
        'ModelGeneralOne',
        related_name='child_x_x')
    
    #--- relations with other ---
    
    # one-to-one auto configured on the other side
    
    # one-to-many auto configured on the other side with many-to-one
    
    # many-to-one
    two_x_1 = models.ForeignKey(
        'ModelGeneralTwo',
        on_delete=models.CASCADE,
        related_name='one_1_x',
        null=True)
    
    # many-to-many
    two_x_x = models.ManyToManyField(
        'ModelGeneralTwo',
        related_name='one_x_x')


class ModelGeneralTwo(CommonColumns):
    
    class Meta:
        db_table = 'model_general_two'
    
    #--- self relations ---
    
    # self one-to-one
    parent_1_1 = models.OneToOneField(
        'ModelGeneralTwo',
        on_delete=models.CASCADE,
        related_name='child_1_1',
        null=True)
    
    # self one-to-many and many-to-one
    parent_x_1 = models.ForeignKey(
        'ModelGeneralTwo',
        on_delete=models.CASCADE,
        related_name='child_1_x',
        null=True)
    
    # self many-to-many
    parent_x_x = models.ManyToManyField(
        'ModelGeneralTwo',
        related_name='child_x_x')
    
    #--- relations with other ---
    
    # one-to-one
    one_1_1 = models.OneToOneField(
        ModelGeneralOne,
        on_delete=models.CASCADE,
        related_name='two_1_1',
        null=True)

    # one-to-many auto configured on the other side with many-to-one
    
    # many-to-one
    one_x_1 = models.ForeignKey(
        ModelGeneralOne,
        on_delete=models.CASCADE,
        related_name='two_1_x',
        null=True)
    
    # many-to-many auto configured on the other side with many-to-many
    
    
    