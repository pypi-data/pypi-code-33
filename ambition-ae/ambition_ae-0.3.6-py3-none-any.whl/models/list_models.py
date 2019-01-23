from edc_base.model_mixins import BaseUuidModel
from edc_list_data.model_mixins import ListModelMixin


class AntibioticTreatment(ListModelMixin, BaseUuidModel):

    pass


class MeningitisSymptom(ListModelMixin, BaseUuidModel):

    pass


class Neurological(ListModelMixin, BaseUuidModel):

    pass
