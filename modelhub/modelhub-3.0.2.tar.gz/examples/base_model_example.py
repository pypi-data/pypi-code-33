# encoding=utf8
# author=spenly
# mail=i@spenly.com


from modelhub.framework import ApiModel

from ner_chemical.modify_format import format_to_api
from ner_chemical.pre_process import read_text
from ner_chemical.train_model import CrfModel


class Model(ApiModel):
    model_name = 'ner_chemical'
    INPUTS_SAMPLE = {
        "text": "3,4-methyl acid hahaha !"
    }
    OUTPUTS_SAMPLE = {
        "result": [
            {
                "entity": "3,4-methyl acid",
                "start": 0,
                "end": 15,
                "type": ""
            }
        ]
    }

    def prepare(self):
        self.crf = CrfModel()

    def is_ready(self):
        return self.crf is not None

    def validate_input_data(self, input_item):
        if not (len(input_item) == 1 and "text" in input_item):
            raise self.InvalidValueInput("input need to has key 'text'")

    def preprocess(self, data):
        return read_text(data["text"])

    def run_model(self, data):
        tok, tok_feature, tok_start, tok_end, label_estimate = data
        return self.crf.inference(tok_feature, label_estimate, tok)

    def postprocess(self, result, input_data, preprocessed_data):
        prediction = result
        tok, tok_feature, tok_start, tok_end, label_estimate = preprocessed_data
        return format_to_api(tok, prediction, tok_start, tok_end)
