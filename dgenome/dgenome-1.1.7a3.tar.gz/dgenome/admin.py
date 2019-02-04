from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.urls import reverse
from dgenome.models import Chromosome, Gene, GeneLocation, GeneAlias
from dgenome.models import Transcript, Feature, Genome


class GenomeAdminForm(forms.ModelForm):
    class Meta:
        model = Genome
        fields = '__all__'


class GenomeAdmin(admin.ModelAdmin):
    form = GenomeAdminForm
    list_display = ['organism', 'chromosomes', 'assembly', 'source']
    readonly_fields = ['organism', 'chromosomes', 'assembly', 'source']


admin.site.register(Genome, GenomeAdmin)


class ChromosomeAdminForm(forms.ModelForm):
    class Meta:
        model = Chromosome
        fields = '__all__'


class ChromosomeAdmin(admin.ModelAdmin):
    form = ChromosomeAdminForm
    list_display = ['name', 'genome']
    readonly_fields = ['name', 'genome']

    def genome(self, obj):
        link = reverse('admin:dgenome_genome_change', args=[obj.genome.pk])
        return format_html('<a href="{}">{}</a>', link, obj.genome) if obj.genome else None


admin.site.register(Chromosome, ChromosomeAdmin)


class GeneAdminForm(forms.ModelForm):
    class Meta:
        model = Gene
        fields = '__all__'


class GeneAdmin(admin.ModelAdmin):
    form = GeneAdminForm
    list_display = ['name', 'description', 'Chr']
    readonly_fields = ['name', 'description', 'Chr']

    def Chr(self, obj):
        link = reverse('admin:dgenome_chromosome_change', args=[obj.chromosome.pk])
        return format_html('<a href="{}">{}</a>', link, obj.chromosome) if obj.chromosome else None


admin.site.register(Gene, GeneAdmin)


class GeneLocationAdminForm(forms.ModelForm):
    class Meta:
        model = GeneLocation
        fields = '__all__'


class GeneLocationAdmin(admin.ModelAdmin):
    form = GeneLocationAdminForm
    list_display = ['txstart', 'txend', 'cdsstart', 'cdsend', 'name']
    readonly_fields = ['txstart', 'txend', 'cdsstart', 'cdsend', 'name']

    def name(self, obj):
        link = reverse('admin:dgenome_gene_change', args=[obj.gene.pk])
        return format_html('<a href="{}">{}</a>', link, obj.gene) if obj.gene else None


admin.site.register(GeneLocation, GeneLocationAdmin)


class GeneAliasAdminForm(forms.ModelForm):
    class Meta:
        model = GeneAlias
        fields = '__all__'


class GeneAliasAdmin(admin.ModelAdmin):
    form = GeneAliasAdminForm
    list_display = ['alias']
    readonly_fields = ['alias']


admin.site.register(GeneAlias, GeneAliasAdmin)


class TranscriptAdminForm(forms.ModelForm):
    class Meta:
        model = Transcript
        fields = '__all__'


class TranscriptAdmin(admin.ModelAdmin):
    form = TranscriptAdminForm
    list_display = ['name', 'tss1500start', 'tss200start', 'txstart', 'txend',
                    'cdsstart', 'cdsend', 'description', 'long_name', 'gene_link']
    readonly_fields = ['name', 'tss1500start', 'tss200start', 'txstart', 'txend',
                       'cdsstart', 'cdsend', 'description', 'long_name', 'gene_link']

    def gene_link(self, obj):
        link = reverse('admin:dgenome_gene_change', args=[obj.gene.pk])
        return format_html('<a href="{}">{}</a>', link, obj.gene) if obj.gene else None


admin.site.register(Transcript, TranscriptAdmin)


class FeatureAdminForm(forms.ModelForm):
    class Meta:
        model = Feature
        fields = '__all__'


class FeatureAdmin(admin.ModelAdmin):
    form = FeatureAdminForm
    list_display = ['feat_type', 'start', 'end', 'trans_link']
    readonly_fields = ['feat_type', 'start', 'end', 'trans_link']

    def trans_link(self, obj):
        link = reverse('admin:dgenome_transcript_change', args=[obj.transcript.pk])
        return format_html('<a href="{}">{}</a>', link, obj.transcript) if obj.transcript else None


admin.site.register(Feature, FeatureAdmin)
