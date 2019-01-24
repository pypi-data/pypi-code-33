from django.db import models
from django.contrib.auth.models import User
from djangoldp_skill.models import Skill

class JobOffer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True) # WARN : Skill imported
    creationDate = models.DateField(auto_now_add=True)
    closingDate = models.DateField(blank=True, null=True)

    class Meta:
        auto_author = 'author'
        permissions = (
            ('view_joboffer', 'Read'),
            ('control_joboffer', 'Control'),
        )

    def __str__(self):
        return '{} ({})'.format(self.title, self.author.get_full_name())
