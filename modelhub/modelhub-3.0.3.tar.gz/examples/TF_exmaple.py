# -*- coding: utf-8 -*-
from modelhub.framework import TFApiModel
from string import digits, punctuation
from nltk.tokenize.treebank import TreebankWordTokenizer
from html.parser import HTMLParser


class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    @classmethod
    def strip_tags(cls, html):
        s = cls()
        s.feed(html)
        return s.get_data()


STR_REMOVAL = str.maketrans('', '', digits + punctuation)


class Model(TFApiModel):
    model_name = "language_detection"
    model_version = 5
    # do not need to write docstring function anymore.
    # instead, just paste your model inputs/outputs samples like following lines

    INPUTS_SAMPLE = {
        "text": "To compile, you need to set up some prerequisites."
    }
    OUTPUTS_SAMPLE = {
        "lang": "en",
        "score": 1
    }

    def api_schema(self):
        return {
            self.default_schema_name: {
                "desc": "default schema, return predict lang and its score",
                "inputs": {
                    "text": [str, (), "string to detect"]
                },
                "outputs": {
                    "lang": [str, (), "language result"],
                    "score": [float, (), "score for detected language"]
                }
            },
            "with_all_scores": {
                "desc": "return default schema plus scores of all languages",
                "inputs": {
                    "text": [str, (), "string to detect"]
                },
                "outputs": {
                    "lang": [str, (), "language result"],
                    "score": [float, (), "score for detected language"],
                    "scores": [float, (6,), "score for each language"],
                    "langs": [str, (6,), "name of each language"],
                }
            }
        }

    def prepare(self):
        super().prepare()
        self.tokenize = TreebankWordTokenizer().tokenize
        self.strip_tags = MLStripper.strip_tags

    def validate_input_data(self, input_item):
        """
        Arguments:
            input_item->{"text":"asd is good"}
        Raises:
            self.InvalidValueInput
        Returns:
            None
        """
        super().validate_input_data(input_item)
        if not ("text" in input_item):
            raise self.InvalidValueInput("input need to has key 'text'")

    def preprocess(self, input_item):
        """
        Arguments:
            input_item->{"text":"asd is good"}
        Returns:
            {
                "chars":[["a","s","d", " ", "i","s"," ","g","o","o","d"]],
                "words":[["asd","is","good"]]
            }
        """
        text = self.strip_tags(input_item["text"]) \
            .rstrip() \
            .translate(STR_REMOVAL) \
            .lower()
        words = self.tokenize(text)
        text = " ".join(words)

        # return {"chars": [list("\r" + text)], "words": [["\r"] + words]}
        # or
        return super().preprocess({"chars": list("\r" + text), "words": ["\r"] + words, "schema": input_item.get("schema")})

    outputs_not_unpack = {"langs"}

    def postprocess(self, result, input_item, preprocessed_item):
        """
        Arguments:
            result -> {"lang":["en"], "scores":[[0.1,0.0,0.0,0.0,0.0,0.9]]}
            input_item -> {"text":"asd is good"}
            preprocessed_item -> {
                "chars":[["a","s","d", " ", "i","s"," ","g","o","o","d"]],
                "words":[["asd","is","good"]]
            }
        Returns:
            {
                "lang":"en",
                "score":0.9,
                "scores":[0.1,0.0,0.0,0.0,0.0,0.9]
            }
        """
        unpacked_result = super().postprocess(result, input_item, preprocessed_item)
        # unpacked_result -> {"lang":"en", "scores":[0.1,0.0,0.0,0.0,0.0,0.9]}
        if "score" not in unpacked_result:
            unpacked_result["score"] = max(unpacked_result["sores"])
        if "scores" in unpacked_result and "langs" in unpacked_result:
            unpacked_result["scores"] = dict(zip(unpacked_result["langs"], unpacked_result["scores"]))
            del unpacked_result["langs"]
        return unpacked_result


if __name__ == "__main__":
    # model = Model("bbig:8500", verbose=False)
    model = Model(local_debug=True)  # Local execute mode
    print("1", model.run({"text": "To compile, you need to set up some prerequisites.", "schema": "with_all_scores"}))
    print("2", model.run_batch(
        [
            {"text": "To compile, you need to set up some prerequisites.", "schema": "with_all_scores"},
        ] * 40,
        # signature_name="with_all_scores"
    ))
