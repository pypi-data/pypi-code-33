from dcomputationaltool.models import ComputationalTool, ComputationalToolCWLImport
from dcomputationaltool.models import ComputationalToolInput, ComputationalToolInputType
from dcomputationaltool.models import ComputationalWF, ComputationalWFCWLImport
from dcomputationaltool.models import ComputationalWFStep, ComputationalWFStepInput
from django.contrib.auth.models import User


def create_user(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return User.objects.create(**defaults)


def create_computationaltool(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalTool.objects.create(**defaults)


def create_computationaltoolcwlimport(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalToolCWLImport.objects.create(**defaults)


def create_computationaltoolinput(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalToolInput.objects.create(**defaults)


def create_computationaltoolinputtype(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalToolInputType.objects.create(**defaults)


def create_computationalwf(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalWF.objects.create(**defaults)


def create_computationalwfcwlimport(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalWFCWLImport.objects.create(**defaults)


def create_computationalwfstep(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalWFStep.objects.create(**defaults)


def create_computationalwfstepinput(**kwargs):
    defaults = {}
    defaults.update(**kwargs)
    return ComputationalWFStepInput.objects.create(**defaults)
