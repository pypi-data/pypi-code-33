from django.db import models

from dgenome.models import Transcript


class Region(models.Model):
    # Fields
    name = models.CharField(max_length=45, blank=False, null=False)

    class Meta:
        ordering = ('-pk',)
        indexes = [
            models.Index(fields=['name']),
        ]

    def __unicode__(self):
        return u'%s' % self.pk


class CpG(models.Model):
    # Fields
    ilmnid = models.CharField(max_length=45, blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    addressa_id = models.IntegerField(blank=True, null=True)
    allelea_probeseq = models.TextField(blank=True, null=True)
    addressb_id = models.CharField(max_length=10, blank=True, null=True)
    alleleb_probeseq = models.CharField(max_length=100, blank=True, null=True)
    infinium_design_type = models.CharField(max_length=5, blank=True, null=True)
    next_base = models.CharField(max_length=5, blank=True, null=True)
    color_channel = models.CharField(max_length=5, blank=True, null=True)
    forward_sequence = models.CharField(max_length=255, blank=True, null=True)
    genome_build = models.CharField(max_length=5, blank=True, null=True)
    chr = models.CharField(max_length=5, blank=True, null=True)
    mapinfo = models.IntegerField(blank=True, null=True)
    sourceseq = models.CharField(max_length=100, blank=True, null=True)
    chromosome_36 = models.CharField(max_length=5, blank=True, null=True)
    coordinate_36 = models.CharField(max_length=25, blank=True, null=True)
    strand = models.CharField(max_length=5, blank=True, null=True)
    probe_snps = models.CharField(max_length=45, blank=True, null=True)
    probe_snps_10 = models.CharField(max_length=45, blank=True, null=True)
    random_loci = models.BooleanField(default=False)
    methyl27_loci = models.BooleanField(default=False)
    ucsc_refgene_name = models.TextField(blank=True, null=True)
    ucsc_refgene_accession = models.TextField(blank=True, null=True)
    ucsc_refgene_group = models.TextField(blank=True, null=True)
    ucsc_cpg_islands_name = models.CharField(max_length=45, blank=True, null=True)
    relation_to_ucsc_cpg_island = models.CharField(max_length=15, blank=True, null=True)
    phantom = models.CharField(max_length=45, blank=True, null=True)
    dmr = models.CharField(max_length=5, blank=True, null=True)
    enhancer = models.BooleanField(default=False)
    hmm_island = models.CharField(max_length=45, blank=True, null=True)
    regulatory_feature_name = models.CharField(max_length=45, blank=True, null=True)
    regulatory_feature_group = models.CharField(max_length=45, blank=True, null=True)
    dhs = models.BooleanField(default=False)

    class Meta:
        ordering = ('-pk',)
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['chr']),
        ]

    def __unicode__(self):
        return u'%s' % self.pk


class CpGHasTranscriptRegions(models.Model):
    # Relationship Fields
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE
    )
    cpg = models.ForeignKey(
        CpG, on_delete=models.CASCADE
    )
    transcript = models.ForeignKey(
        Transcript, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-pk',)
        index_together = [
            ["region", "cpg", "transcript"],
        ]

    def __unicode__(self):
        return u'%s' % self.pk
