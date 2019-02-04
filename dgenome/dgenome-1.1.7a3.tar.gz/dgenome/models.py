from django.urls import reverse
from django.db import models


class Genome(models.Model):
    # Fields
    organism = models.CharField(max_length=100)
    chromosomes = models.IntegerField()
    assembly = models.CharField(max_length=100)
    source = models.CharField(max_length=100)

    class Meta:
        ordering = ('-pk',)

    def __str__(self):
        return '%s' % (self.assembly)

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('genome_detail', args=(self.pk,))

    def get_update_url(self):
        return reverse('genome_update', args=(self.pk,))


class Chromosome(models.Model):
    name = models.CharField(max_length=5, unique=True)

    # Relationship Fields
    genome = models.ForeignKey(
        Genome, on_delete=models.CASCADE
    )

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ('-pk',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('chromosome_detail', args=(self.pk,))


class Gene(models.Model):
    name = models.CharField(max_length=45)
    strand = models.CharField(max_length=50)
    description = models.TextField(max_length=3000)
    chromosome = models.ForeignKey(Chromosome, models.CASCADE)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ('-pk',)
        unique_together = ("name", "chromosome")
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('gene_detail', args=(self.pk,))


class GeneLocation(models.Model):
    txstart = models.IntegerField()
    txend = models.IntegerField()
    cdsstart = models.IntegerField()
    cdsend = models.IntegerField()
    gene = models.ForeignKey(Gene, models.CASCADE)

    class Meta:
        ordering = ['txstart']
        unique_together = ("txstart", "txend", "gene")
        index_together = [
            ["txstart", "txend"],
        ]

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('genelocation_detail', args=(self.pk,))


class GeneAlias(models.Model):
    alias = models.CharField(max_length=50)

    # Relationship Fields
    gene = models.ForeignKey(
        Gene, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-pk',)
        indexes = [
            models.Index(fields=['alias']),
        ]

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('genealias_detail', args=(self.pk,))


class Transcript(models.Model):
    name = models.CharField(max_length=45)
    strand = models.CharField(max_length=1)
    tss1500start = models.IntegerField()
    tss200start = models.IntegerField()
    txstart = models.IntegerField()
    txend = models.IntegerField()
    cdsstart = models.IntegerField()
    cdsend = models.IntegerField()
    description = models.TextField(max_length=3000)
    long_name = models.TextField(max_length=1000)
    has_coding = models.BooleanField(default=False)
    gene = models.ForeignKey(
        Gene, on_delete=models.CASCADE
    )

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ['txstart']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['strand']),
            models.Index(fields=['tss1500start']),
            models.Index(fields=['tss200start']),
            models.Index(fields=['txstart']),
            models.Index(fields=['txend']),
            models.Index(fields=['cdsstart']),
            models.Index(fields=['cdsend']),
        ]
        index_together = [
            ["strand", "txstart", "txend", "gene"],
            ["strand", "tss1500start", "tss200start", "gene"],
        ]

    def __unicode__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('transcript_detail', args=(self.pk,))


class Feature(models.Model):
    feat_type = models.CharField(max_length=45)
    start = models.IntegerField()
    end = models.IntegerField()
    transcript = models.ForeignKey('Transcript', models.CASCADE)

    class Meta:
        ordering = ['start']
        unique_together = ("start", "end", "transcript")
        indexes = [
            models.Index(fields=['feat_type']),
        ]
        index_together = [
            ["start", "end"],
        ]
