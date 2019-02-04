from django.db import models
from glossary.models import GlossaryModel
from mptt.models import MPTTModel, TreeForeignKey


class Address(GlossaryModel):
    name = models.TextField('Адрес')
    longitude = models.FloatField('Долгота', blank=True, null=True)
    latitude = models.FloatField('Широта', blank=True, null=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'


class Campus(GlossaryModel):
    name = models.CharField('Наименование', max_length=500)
    address = models.ForeignKey(Address, verbose_name='Адрес', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Здание'
        verbose_name_plural = 'Здания'


class RoomType(GlossaryModel):
    name = models.CharField('Тип', max_length=500)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Тип помещения'
        verbose_name_plural = 'Тип помещений'


class Subdivision(MPTTModel, GlossaryModel):
    name = models.CharField('Наименование', max_length=500)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Room(GlossaryModel):
    FLOORS = [(i, i) for i in range(10)]

    name = models.CharField('Наименование/номер', max_length=500)
    type = models.ForeignKey(RoomType, verbose_name='Тип помещения', blank=True, null=True, on_delete=models.CASCADE)
    description = models.TextField('Описание', blank=True)
    places = models.PositiveSmallIntegerField('Количество посадочных мест', blank=True, null=True)
    size = models.FloatField('Площадь', blank=True, null=True)
    floor = models.PositiveSmallIntegerField('Этаж', choices=FLOORS, blank=True, null=True)
    subdivisions = models.ManyToManyField(Subdivision, verbose_name='Подразделения', blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'
