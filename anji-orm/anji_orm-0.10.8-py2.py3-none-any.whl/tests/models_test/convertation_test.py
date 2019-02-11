from .base_models import BaseModelWithEnum, BaseEnum
from ..base import BaseTestCase


class ModelBaseConvertationTest(BaseTestCase):

    def test_enum_field(self) -> None:
        test_field_text = 'cute panda'
        base_model_record = BaseModelWithEnum(enum_field=BaseEnum.first, test_field=test_field_text)
        base_model_dict = base_model_record.to_dict()
        self.assertEqual(base_model_dict['test_field'], test_field_text)
        self.assertEqual(base_model_dict['enum_field'], BaseEnum.first)
