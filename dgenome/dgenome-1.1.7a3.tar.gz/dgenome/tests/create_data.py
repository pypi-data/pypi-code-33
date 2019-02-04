from django.contrib.auth.models import User

from dgenome.models import Genome, Chromosome, Gene, GeneLocation, GeneAlias
from dgenome.models import Transcript, Feature


def create_superuser(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return User.objects.create_superuser(**defaults)


def create_genome(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Genome.objects.create(**defaults)


def create_chromosome(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Chromosome.objects.create(**defaults)


def create_gene(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Gene.objects.create(**defaults)


def create_genelocation(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return GeneLocation.objects.create(**defaults)


def create_genealias(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return GeneAlias.objects.create(**defaults)


def create_transcript(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Transcript.objects.create(**defaults)


def create_feature(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Feature.objects.create(**defaults)
