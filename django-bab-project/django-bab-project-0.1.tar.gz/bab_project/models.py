from django.db import models
from django.urls import reverse
from django.contrib.auth.models import Group

from filebrowser.fields import FileBrowseField


class Category(models.Model):
    title = models.CharField(max_length=64)
    excerpt = models.TextField(blank=True)
    slug = models.SlugField(verbose_name='slug', unique=True)
    image = FileBrowseField("Image", max_length=200, extensions=['.jpg', '.png'], blank=True)
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        verbose_name = 'catégorie'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project-category-detail', args=[self.slug, ])


class Project(models.Model):
    categories = models.ManyToManyField('Category', related_name="projects", verbose_name='catégories')
    customer = models.ForeignKey('Customer', related_name='projects', on_delete=models.CASCADE, verbose_name='partenaire', null=True, blank=True)
    title = models.CharField(max_length=64)
    slug = models.SlugField(verbose_name='slug', unique=True)
    image = FileBrowseField("Image", max_length=200, extensions=['.jpg', '.png'], blank=True)
    excerpt = models.CharField(max_length=128, blank=True)
    content = models.TextField()
    date = models.DateField(null=True, blank=True)
    prepopulated_fields = {"slug": ("title",)}

    class Meta:
        verbose_name = 'bidule'
        ordering = ['date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project-project-detail', args=[self.slug, ])


class Feature(models.Model):
    project = models.ForeignKey('Project', related_name='features', on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.TextField()

    class Meta:
        verbose_name = 'fonctionnalité'

    def __str__(self):
        return self.title


class Customer(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    image = FileBrowseField("Image", max_length=200, extensions=['.jpg', '.png'], blank=True)

    class Meta:
        verbose_name = 'partenaire'

    def __str__(self):
        return self.name
