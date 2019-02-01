# encoding=utf8
# author=spenly
# mail=i@spenly.com

from modelhub.framework import ParentApiModel


class Model(ParentApiModel):
    model_name = "translate_cnen_claim"

    INPUTS_SAMPLE = {
        "type": "human",
        "text": "本实用新型涉及一种煤矿巷道支护装置，特别是一种两端楔形锚固式锚杆。"}
    OUTPUTS_SAMPLE = {
        "text": "The utility model relates to a coal mine roadway support device , in particular to a wedged anchoring bolt with two ends ."}

    def prepare_submodels(self, *args, **kwargs):
        from translate_cnen_claim_chem.api_models import Model as translate_cnen_claim_chem_model
        from translate_cnen_claim_elec.api_models import Model as translate_cnen_claim_elec_model
        from translate_cnen_claim_fite.api_models import Model as translate_cnen_claim_fite_model
        from translate_cnen_claim_huma.api_models import Model as translate_cnen_claim_huma_model
        from translate_cnen_claim_mech.api_models import Model as translate_cnen_claim_mech_model
        from translate_cnen_claim_perf.api_models import Model as translate_cnen_claim_perf_model
        from translate_cnen_claim_phys.api_models import Model as translate_cnen_claim_phys_model
        return {
            "chemistry": translate_cnen_claim_chem_model(*args, **kwargs),
            "electronic": translate_cnen_claim_elec_model(*args, **kwargs),
            "fite": translate_cnen_claim_fite_model(*args, **kwargs),
            "human": translate_cnen_claim_huma_model(*args, **kwargs),
            "mechanic": translate_cnen_claim_mech_model(*args, **kwargs),
            "performance": translate_cnen_claim_perf_model(*args, **kwargs),
            "physical": translate_cnen_claim_phys_model(*args, **kwargs),
        }

    option_key = "type"
    default_option = "human"


if __name__ == "__main__":
    model = Model()
    output = model.run(model.INPUTS_SAMPLE)
    print(output)
