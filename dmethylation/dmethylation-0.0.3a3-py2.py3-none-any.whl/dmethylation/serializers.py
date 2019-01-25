from . import models

from rest_framework import serializers


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = (
            'pk',
            'name',
        )


class IlluminaMethylation450Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.CpG
        fields = (
            'pk',
            'ilmnid',
            'name',
            'addressa_id',
            'allelea_probeseq',
            'addressb_id',
            'alleleb_probeseq',
            'infinium_design_type',
            'next_base',
            'color_channel',
            'forward_sequence',
            'genome_build',
            'chr',
            'mapinfo',
            'sourceseq',
            'chromosome_36',
            'coordinate_36',
            'strand',
            'probe_snps',
            'probe_snps_10',
            'random_loci',
            'methyl27_loci',
            'ucsc_refgene_name',
            'ucsc_refgene_accession',
            'ucsc_refgene_group',
            'ucsc_cpg_islands_name',
            'relation_to_ucsc_cpg_island',
            'phantom',
            'dmr',
            'enhancer',
            'hmm_island',
            'regulatory_feature_name',
            'regulatory_feature_group',
            'dhs',
        )


class CpGHasTranscriptRegionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CpGHasTranscriptRegions
        fields = (
            'pk',
        )
