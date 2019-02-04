from rest_framework import serializers

from dgenome.models import Genome, Chromosome, Gene, GeneLocation, GeneAlias, Transcript, Feature


class GenomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genome
        fields = (
            'pk',
            'organism',
            'chromosomes',
            'assembly',
            'source',
        )


class ChromosomeSerializer(serializers.ModelSerializer):
    genome = GenomeSerializer()

    class Meta:
        model = Chromosome
        fields = '__all__'


class GeneLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneLocation
        fields = '__all__'


class GeneAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneAlias
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'


class TranscriptSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(source="feature_set", many=True, read_only=True)

    class Meta:
        model = Transcript
        fields = '__all__'


class GeneSerializer(serializers.ModelSerializer):
    genelocations = GeneLocationSerializer(source="genelocation_set",
                                           many=True, read_only=True)
    genealias = GeneLocationSerializer(source="genealias_set",
                                       many=True, read_only=True)
    transcripts = TranscriptSerializer(source="transcript_set",
                                       many=True, read_only=True)
    chromosome = ChromosomeSerializer()

    class Meta:
        model = Gene
        fields = '__all__'
