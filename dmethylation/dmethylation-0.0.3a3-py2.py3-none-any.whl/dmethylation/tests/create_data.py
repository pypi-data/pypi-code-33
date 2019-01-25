from django.contrib.auth.models import User

from dmethylation.models import Region, CpG, CpGHasTranscriptRegions


def create_superuser(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return User.objects.create_superuser(**defaults)


def create_region(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Region.objects.create(**defaults)


def create_cpg(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return CpG.objects.create(**defaults)


def create_cpghastranscriptregions(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return CpGHasTranscriptRegions.objects.create(**defaults)
