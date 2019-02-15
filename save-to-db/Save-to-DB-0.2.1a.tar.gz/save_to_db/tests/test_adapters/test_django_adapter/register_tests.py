import os
import django
from django.core.management import call_command

from save_to_db.adapters.django_adapter import DjangoAdapter
from save_to_db.core.persister import Persister

from . import project
from .project import settings
from .django_test_base import DjangoTestBase

from .. import register_test
from ..test_fields_and_relations import TestFieldsAndRelations
from ..test_constraints import TestConstraints
from ..test_complete_item_metaclass import TestCompleteItemMetaclass
from ..test_item_cls_manager import TestItemClsManager
from ..test_item_fields import TestItemFields
from ..test_item_hooks import TestItemHooks
from ..test_item_persist import TestItemPersist
from ..test_item_dump import TestItemDump
from ..test_bulk_slicing import TestBulkSlicing
from ..test_scope import TestScope
from ..test_select import TestSelect
from ..test_signals import TestSignals


# setting up Django and loading models
settings.INSTALLED_APPS = tuple(
    '{}.{}'.format(project.__name__, app) for app in settings.INSTALLED_APPS)
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    '{}.settings'.format(project.__name__))
django.setup()
call_command('migrate', verbosity=0)
from .project.orm_only import models



AdapterPrefix = 'Django'
persister = Persister(DjangoAdapter,
                      adapter_settings={})

models = {
    'ModelFieldTypes': models.ModelFieldTypes,
    
    'ModelGeneralOne': models.ModelGeneralOne,
    'ModelGeneralTwo': models.ModelGeneralTwo,

    'ModelConstraintsOne': models.ModelConstraintsOne,
    'ModelConstraintsTwo': models.ModelConstraintsTwo,
    'ModelConstraintsThree': models.ModelConstraintsThree,
    'ModelConstraintsFour': models.ModelConstraintsFour,
    'ModelConstraintsFive': models.ModelConstraintsFive,
    'ModelConstraintsSix': models.ModelConstraintsSix,
    'ModelConstraintsSelf': models.ModelConstraintsSelf,
    
    'ModelInvalidFieldNames': models.ModelInvalidFieldNames,

    'ModelManyRefsOne': models.ModelManyRefsOne,
    'ModelManyRefsTwo': models.ModelManyRefsTwo,
    
    'ModelAutoReverseOne': models.ModelAutoReverseOne,
    'ModelAutoReverseTwoA': models.ModelAutoReverseTwoA,
    'ModelAutoReverseTwoB': models.ModelAutoReverseTwoB,
    'ModelAutoReverseThreeA': models.ModelAutoReverseThreeA,
    'ModelAutoReverseThreeB': models.ModelAutoReverseThreeB,
    'ModelAutoReverseFourA': models.ModelAutoReverseFourA,
    'ModelAutoReverseFourB': models.ModelAutoReverseFourB,
}

for test_cls in (TestFieldsAndRelations,
                 TestConstraints,
                 TestItemClsManager,
                 TestCompleteItemMetaclass,
                 TestItemFields,
                 TestItemHooks,
                 TestItemPersist,
                 TestItemDump,
                 TestBulkSlicing,
                 TestScope,
                 TestSelect,
                 TestSignals):
    
    register_test(AdapterPrefix, DjangoTestBase,
                  test_cls, models, persister)