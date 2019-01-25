from django.contrib.auth.models import User

from ..models import ProjectRole, ProjectPermission, Project
from ..models import ProjectMetadata, ProjectUserRole
from ..models import Experiment, ExperimentType, ExperimentMetadata
from ..models import Sample, SampleMetadata
from ..models import Condition, ConditionMetadata


def create_user(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_projectrole(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ProjectRole.objects.create(**defaults)


def create_projectpermission(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ProjectPermission.objects.create(**defaults)


def create_project(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Project.objects.create(**defaults)


def create_projectmetadata(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ProjectMetadata.objects.create(**defaults)


def create_projectuserrole(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ProjectUserRole.objects.create(**defaults)


def create_experimenttype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ExperimentType.objects.create(**defaults)


def create_experiment(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Experiment.objects.create(**defaults)


def create_experimentmetadata(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ExperimentMetadata.objects.create(**defaults)


def create_sample(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Sample.objects.create(**defaults)


def create_samplemetadata(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return SampleMetadata.objects.create(**defaults)


def create_condition(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return Condition.objects.create(**defaults)


def create_conditionmetadata(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ConditionMetadata.objects.create(**defaults)
