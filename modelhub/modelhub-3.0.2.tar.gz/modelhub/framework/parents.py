# encoding=utf8
# author=spenly
# mail=i@spenly.com
from .base import ApiModel
from abc import abstractproperty, abstractmethod


class ParentApiModel(ApiModel):
    TYPE = "TF"
    INPUTS_SAMPLE = None
    OUTPUTS_SAMPLE = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    @abstractproperty
    def option_key(self):
        raise NotImplementedError

    @property
    def default_option(self):
        return None

    def prepare(self):
        super().prepare()
        self.submodels = self.prepare_submodels(*self.args, **self.kwargs)
        if not isinstance(self.submodels, dict) or not all(isinstance(submodel, ApiModel) for submodel in self.submodels.values()):
            raise InvalidSubModel("prepare_submodels must return a dict with key as input type and value as ApiModel instance")
        if self.default_option and self.default_option not in self.submodels:
            raise InvalidSubModel("default_option %s not exist in prepare_submodels" % self.default_option)

    @abstractmethod
    def prepare_submodels(self):
        """
        return {
            "chemistry": translate_cnen_claim_chem_model(*args, **kwargs),
            "electronic": translate_cnen_claim_elec_model(*args, **kwargs),
            "fite": translate_cnen_claim_fite_model(*args, **kwargs),
            "human": translate_cnen_claim_huma_model(*args, **kwargs),
            "mechanic": translate_cnen_claim_mech_model(*args, **kwargs),
            "performance": translate_cnen_claim_perf_model(*args, **kwargs),
            "physical": translate_cnen_claim_phys_model(*args, **kwargs),
        }
        """
        raise NotImplementedError

    def is_ready(self):
        return all(submodel.is_ready() for submodel in self.submodels.values())

    def validate_input_data(self, raw_input):
        if self.option_key not in raw_input and self.default_option is None:
            raise self.InvalidValueInput("input data need key '%s'" % self.option_key)
        submodel_type = raw_input.get(self.option_key, self.default_option)
        if submodel_type not in self.submodels:
            raise self.InvalidValueInput("%s: %s not support" % (self.option_key, submodel_type))
        if raw_input[self.option_key] not in self.submodels:
            msg = "invalid %s value, should be one of [ %s ]"
            msg = msg % (self.option_key, ",".join(self.submodels.keys()))
            raise self.InvalidValueInput(msg)
        return True

    def run_model(self, preprocessed_data):
        submodel_type = preprocessed_data.get(self.option_key, self.default_option)
        submodel = self.submodels[submodel_type]
        return submodel.run(preprocessed_data)


class InvalidSubModel(Exception):
    pass


ParentBaseModel = ParentApiModel
