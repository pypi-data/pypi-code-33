from save_to_db.adapters.sqlalchemy_adapter import SqlachemyAdapter
from save_to_db.core.persister import Persister

from . import config
from .sqlalchemy_test_base import SqlalchemyTestBase

from .models.fields import ModelFieldTypes
from .models.constraints import (ModelConstraintsOne,
                                 ModelConstraintsTwo,
                                 ModelConstraintsThree,
                                 ModelConstraintsFour,
                                 ModelConstraintsFive,
                                 ModelConstraintsSix,
                                 ModelConstraintsSelf)
from .models.general import (ModelGeneralOne,
                             ModelGeneralTwo)
from .models.invalid_fields import ModelInvalidFieldNames
from .models.many_refs import ModelManyRefsOne, ModelManyRefsTwo
from .models.auto_reverse import (ModelAutoReverseOne,
                                  ModelAutoReverseTwoA,
                                  ModelAutoReverseTwoB,
                                  ModelAutoReverseThreeA,
                                  ModelAutoReverseThreeB,
                                  ModelAutoReverseFourA,
                                  ModelAutoReverseFourB)

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

AdapterPrefix = 'Sqlalchemy'
persister = Persister(SqlachemyAdapter,
                      adapter_settings={'session': config.session,
                                        'ModelBase': config.Base},
                      autocommit=True)
models = {
    'ModelFieldTypes': ModelFieldTypes,
    
    'ModelGeneralOne': ModelGeneralOne,
    'ModelGeneralTwo': ModelGeneralTwo,
    
    'ModelConstraintsOne': ModelConstraintsOne,
    'ModelConstraintsTwo': ModelConstraintsTwo,
    'ModelConstraintsThree': ModelConstraintsThree,
    'ModelConstraintsFour': ModelConstraintsFour,
    'ModelConstraintsFive': ModelConstraintsFive,
    'ModelConstraintsSix': ModelConstraintsSix,
    'ModelConstraintsSelf': ModelConstraintsSelf,
    
    'ModelInvalidFieldNames': ModelInvalidFieldNames,
    
    'ModelManyRefsOne': ModelManyRefsOne,
    'ModelManyRefsTwo': ModelManyRefsTwo,
        
    'ModelAutoReverseOne': ModelAutoReverseOne,
    'ModelAutoReverseTwoA': ModelAutoReverseTwoA,
    'ModelAutoReverseTwoB': ModelAutoReverseTwoB,
    'ModelAutoReverseThreeA': ModelAutoReverseThreeA,
    'ModelAutoReverseThreeB': ModelAutoReverseThreeB,
    'ModelAutoReverseFourA': ModelAutoReverseFourA,
    'ModelAutoReverseFourB': ModelAutoReverseFourB,
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

    register_test(AdapterPrefix, SqlalchemyTestBase,
                  test_cls, models, persister)

