from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from djangoldp_account.models import ChatConfig


class Customer(models.Model):
    name = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    logo = models.URLField()
    companyRegister = models.CharField(default='', max_length=255)
    contactFirstName = models.CharField(default='', max_length=255)
    contactLastName = models.CharField(default='', max_length=255)
    contactMail = models.EmailField(default='')
    contactPhone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        permissions = (
            ('view_client', 'Read'),
            ('control_client', 'Control'),
        )

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255, default='')
    number = models.PositiveIntegerField(default='0', blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)  # WARN add import
    team = models.ManyToManyField(User, through='Job', blank=True)
    businessProvider = models.CharField(max_length=255, blank=True, null=True)
    businessProviderFee = models.PositiveIntegerField(default='0', blank=True)
    chatConfig = models.ForeignKey(ChatConfig, related_name="projects", on_delete=models.DO_NOTHING, null=True)


    def get_absolute_url(self):
        return reverse_lazy('project-detail', kwargs={'pk': self.pk})

    class Meta:
        permissions = (
            ('view_project', 'Read'),
            ('control_project', 'Control'),
        )
        rdf_type = 'doap:project'

    def __str__(self):
        return self.name

class Job(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
