# -*- coding: utf-8 -*-
from modelhub.framework import TFApiModel


class Model(TFApiModel):
    model_name = "image_extraction"


if __name__ == "__main__":
    model = Model()
    model.run({"inputs": open("page1.png", "rb").read()})
