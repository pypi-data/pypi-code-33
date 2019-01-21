from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy

class Circle(models.Model):
    name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255, default='')
    team = models.ManyToManyField(User, blank=True)
    owner = models.ForeignKey(User, related_name="owned_circles", on_delete=models.DO_NOTHING)
    jabberID = models.CharField(max_length=255, blank=True, null=True)
    jabberRoom = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse_lazy('circle-detail', kwargs={'pk': self.pk})

    class Meta:
        permissions = (
            ('view_circle', 'Read'),
            ('control_circle', 'Control'),
        )

    def __str__(self):
        return self.name
