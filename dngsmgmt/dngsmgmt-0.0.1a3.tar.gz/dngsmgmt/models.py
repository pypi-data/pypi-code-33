from django.contrib.auth.models import User
from django.db import models as models


class ProjectRole(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class ProjectPermission(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    # Relationship Fields
    role = models.ManyToManyField(
        'dngsmgmt.ProjectRole',
        related_name="projectpermission_role"
    )

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class Project(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    description = models.TextField()
    status = models.CharField(default='created', max_length=255, blank=False, null=False)
    completed = models.FloatField(default=0, blank=False, null=False)

    # Relationship Fields
    permission = models.ForeignKey(
        'dngsmgmt.ProjectPermission',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_updated_by'
    )

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class ProjectUserRole(models.Model):
    project = models.ForeignKey(
        'dngsmgmt.Project',
        on_delete=models.CASCADE,
        related_name='projectuser'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projectuser'
    )
    role = models.ForeignKey(
        'dngsmgmt.ProjectRole',
        on_delete=models.CASCADE,
        related_name="projectrole"
    )

    class Meta:
        ordering = ('project',)
        unique_together = (("project", "user"),)

    def __str__(self):
        return u'%s' % self.pk

    def __unicode__(self):
        return u'%s' % self.pk


class ProjectMetadata(models.Model):
    # Fields
    key = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.TextField()

    # Relationship Fields
    project = models.ForeignKey(
        'dngsmgmt.Project',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projectmetadata_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projectmetadata_updated_by'
    )

    class Meta:
        ordering = ('key',)
        indexes = [
            models.Index(fields=['key']),
        ]
        unique_together = (("project", "key"),)

    def __str__(self):
        return self.key

    def __unicode__(self):
        return u'%s' % self.pk


class ExperimentType(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class Experiment(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    description = models.TextField()

    # Relationship Fields
    project = models.ForeignKey(
        'dngsmgmt.Project',
        on_delete=models.CASCADE
    )
    permission = models.ForeignKey(
        'dngsmgmt.ProjectPermission',
        on_delete=models.CASCADE
    )
    type = models.ForeignKey(
        'dngsmgmt.ExperimentType',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experiment_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experiment_updated_by'
    )

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class ExperimentMetadata(models.Model):
    # Fields
    key = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.TextField()

    # Relationship Fields
    experiment = models.ForeignKey(
        'dngsmgmt.Experiment',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experimentmetadata_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='experimentmetadata_updated_by'
    )

    class Meta:
        ordering = ('key',)
        indexes = [
            models.Index(fields=['key']),
        ]
        unique_together = (("experiment", "key"),)

    def __str__(self):
        return self.key

    def __unicode__(self):
        return u'%s' % self.pk


class Sample(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    # Relationship Fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sample_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sample_updated_by'
    )
    experiment = models.ForeignKey(
        'dngsmgmt.Experiment',
        on_delete=models.CASCADE
    )
    permission = models.ForeignKey(
        'dngsmgmt.ProjectPermission',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class SampleMetadata(models.Model):
    # Fields
    key = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.TextField()

    # Relationship Fields
    sample = models.ForeignKey(
        'dngsmgmt.Sample',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='samplemetadata_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='samplemetadata_updated_by'
    )

    class Meta:
        ordering = ('key',)
        indexes = [
            models.Index(fields=['key']),
        ]
        unique_together = (("sample", "key"),)

    def __str__(self):
        return self.key

    def __unicode__(self):
        return u'%s' % self.pk


class Condition(models.Model):
    # Fields
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    description = models.TextField()

    # Relationship Fields
    experiment = models.ForeignKey(
        'dngsmgmt.Experiment',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='condition_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='condition_updated_by'
    )
    samples = models.ManyToManyField(
        'dngsmgmt.Sample',
        related_name="conditions"
    )
    permission = models.ForeignKey(
        'dngsmgmt.ProjectPermission',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def __unicode__(self):
        return u'%s' % self.pk


class ConditionMetadata(models.Model):
    # Fields
    key = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.TextField()

    # Relationship Fields
    condition = models.ForeignKey(
        'dngsmgmt.Condition',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conditionmetadata_created_by'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conditionmetedata_updated_by'
    )

    class Meta:
        ordering = ('key',)
        indexes = [
            models.Index(fields=['key']),
        ]
        unique_together = (("condition", "key"),)

    def __str__(self):
        return self.key

    def __unicode__(self):
        return u'%s' % self.pk
