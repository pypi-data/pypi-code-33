from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=255, default='')
    users = models.ManyToManyField(User, blank=True, related_name="skills")

    class Meta:
        permissions = (
            ('view_skill', 'Read'),
            ('control_skill', 'Control'),
        )

    def __str__(self):
        return self.name
