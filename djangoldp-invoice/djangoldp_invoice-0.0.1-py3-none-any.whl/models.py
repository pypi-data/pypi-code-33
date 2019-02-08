# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from  djangoldp_project.models import Customer
from  djangoldp_project.models import Project
from django.db.models import Sum
import datetime
from decimal import Decimal

class FreelanceInvoice(models.Model):
    # customer = models.ForeignKey(User, on_delete=models.CASCADE)
    # provider = models.ForeignKey(User, on_delete=models.CASCADE)
    STATES = (
      ('pending', 'en attente'),
      ('sent', 'envoyé'),
      ('paid', 'payé')
    )
    TVA_RATES = (
      (0.0, 'exonération de TVA'),
      (20.0, '20%')
    )
    freelanceFullname = models.CharField(max_length=255)
    identifier = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name=u"Titre facture")
    state = models.CharField(max_length=255, choices=STATES, default='pending')
    htAmount = models.DecimalField(max_digits=11, decimal_places=2)
    tvaRate = models.DecimalField(choices=TVA_RATES, max_digits=4, decimal_places=2, default=20.0)
    uploadUrl = models.URLField
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)
    invoicingDate = models.DateField(default = datetime.date.today)

    class Meta:
        permissions = (
            ('view_freelance_invoice', 'Read'),
            ('control_freelance_invoice', 'Control'),
        )

    def __str__(self):
        return '{} ({} / {})'.format(self.freelanceFullname, self.identifier, self.title)



class CustomerInvoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, null=True)
    STATES = (
      ('pending', 'en attente'),
      ('paid', 'réglée')
    )
    identifier = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    state = models.CharField(max_length=255, choices=STATES, default='pending')
    tvaRate = models.DecimalField(max_digits=4, decimal_places=2)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)
    invoicingDate = models.DateField(default = datetime.date.today)

    def htAmount(self):
        return self.batches.aggregate(total=Sum('tasks__htAmount'))['total']

    def tvaAmount(self):
        return Decimal(self.tvaRate * self.htAmount() / Decimal(100))

    def ttcAmount(self):
        return Decimal(self.tvaAmount() + self.htAmount())

    class Meta:
        permissions = (
            ('view_invoice', 'Read'),
            ('control_invoice', 'Control'),
        )

    def __str__(self):
        return '{} - {} ({})'.format(self.identifier, self.title, self.htAmount())

# Lot =========================================================
class Batch(models.Model):
    invoice = models.ForeignKey(CustomerInvoice, on_delete=models.CASCADE, related_name='batches')
    title = models.CharField(max_length=255)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)

    class Meta:
        permissions = (
            ('view_batch', 'Read'),
            ('control_batch', 'Control'),
        )

    def __str__(self):
        return '{} - {} ({} € HT)'.format(self.invoice.title, self.title, self.htAmount())

    def htAmount(self):
        amount = self.tasks.all().aggregate(total=Sum('htAmount'))['total']
        if amount is None:
            amount = Decimal(0.0)
        return amount

Batch._meta.serializer_fields = ['@id', 'invoice', 'title', 'htAmount', 'tasks']

class Task(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    htAmount = models.DecimalField(max_digits=11, decimal_places=2)
    creationDate = models.DateField(auto_now_add=True)
    modificationDate = models.DateField(auto_now=True)

    class Meta:
        permissions = (
            ('view_batch', 'Read'),
            ('control_batch', 'Control'),
        )

    def __str__(self):
        return '{} - {} ({} € HT)'.format(self.batch.title, self.title, self.htAmount)

