from django.db import models as models


class ComputationalTool(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    cwl = models.URLField(blank=False, null=False, unique=True)
    author_name = models.CharField(max_length=255, blank=False, null=False)
    author_identifier = models.URLField(blank=False, null=False)
    author_email = models.EmailField(blank=False, null=False)
    codeRepository = models.URLField(blank=True, null=True)
    license = models.URLField(blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('id',)
        indexes = [
            models.Index(fields=['name']),
        ]
        index_together = [
            ["author_name", "author_identifier", "author_email"],
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalToolCWLImport(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    version = models.CharField(max_length=60, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    cwl = models.URLField(blank=False, null=False)

    # Relationship Fields
    computationaltool = models.ForeignKey(
        ComputationalTool,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('computationaltool', 'id',)
        unique_together = ("name", "computationaltool", "cwl")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalToolInputType(models.Model):
    # Fields
    type = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('type',)

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.type


class ComputationalToolInput(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    option = models.CharField(max_length=100, blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    array = models.BooleanField(default=False)
    optional = models.BooleanField(default=False)
    doc = models.TextField(blank=True, null=True)

    # Relationship Fields
    computationaltool = models.ForeignKey(
        ComputationalTool,
        on_delete=models.CASCADE
    )
    computationaltoolinputtype = models.ForeignKey(
        ComputationalToolInputType,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('computationaltool', 'id',)
        unique_together = ("name", "computationaltool", "option")
        index_together = [
            ["name", "option"],
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalWF(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    cwl = models.URLField(blank=False, null=False, unique=True)
    author_name = models.CharField(max_length=255, blank=False, null=False)
    author_identifier = models.URLField(blank=False, null=False)
    author_email = models.EmailField(blank=False, null=False)
    license = models.URLField(blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('id',)
        indexes = [
            models.Index(fields=['name']),
        ]
        index_together = [
            ["author_name", "author_identifier", "author_email"],
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalWFCWLImport(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    cwl = models.URLField(blank=False, null=False)

    # Relationship Fields
    computationalwf = models.ForeignKey(
        ComputationalWF,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('computationalwf', 'id',)
        unique_together = ("name", "computationalwf", "cwl")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalWFStep(models.Model):
    # Fields
    name = models.CharField(max_length=255, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    order = models.IntegerField(blank=False, null=False)
    description = models.TextField(blank=True, null=True)

    # Relationship Fields
    computationaltool = models.ForeignKey(
        ComputationalTool,
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    computationalwfstep = models.ForeignKey(
        ComputationalWF,
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='computationalwfstep'
    )
    computationalwf = models.ForeignKey(
        ComputationalWF,
        on_delete=models.CASCADE,
        related_name='computationalwf'
    )

    class Meta:
        ordering = ('order', 'computationalwf', 'computationaltool')
        unique_together = ("name", "computationalwf", "computationaltool")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.name


class ComputationalWFStepInput(models.Model):
    # Fields
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    value = models.TextField(blank=True, null=True)

    # Relationship Fields
    computationalwfstep = models.ForeignKey(
        ComputationalWFStep,
        on_delete=models.CASCADE
    )
    computationaltoolinput = models.ForeignKey(
        ComputationalToolInput,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('id', 'computationalwfstep', 'computationaltoolinput')
        unique_together = ('id', 'computationalwfstep', 'computationaltoolinput')

    def __unicode__(self):
        return u'%s' % self.id

    def __str__(self):
        return self.value
