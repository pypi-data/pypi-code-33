# encoding=utf8
# author=spenly
# mail=i@spenly.com
from .base import BaseCommand, option, register
import base64
from modelhub.utils import json


class ColorPrint:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def show(msg, style):
        print(style + msg + ColorPrint.ENDC)


class GeneralChecker(object):

    def __init__(self, model_name):
        self.model_name = model_name
        self._weights = [100000000, 10000, 1, 0.0001]

    def _get_token_wight(self):
        from modelhub.core.models import Model
        from collections import Counter
        model_names = [model.name for model in Model.all()]
        counter = Counter()
        for mname in model_names:
            for item in zip(mname.split("_")[::-1], self._weights[::-1]):
                counter.update({item[0]: item[1]})
        return counter

    def _generate_new_name(self):
        weights = self._get_token_wight()
        ss = self.model_name.split("_")
        iws = {}
        for item in ss:
            iws[item] = weights.get(item) or 0
        sorted_values = sorted(iws.items(), key=lambda x: x[1], reverse=True)
        return "_".join([item[0] for item in sorted_values])

    def regular_name_check(self):
        new_name = self._generate_new_name()
        if new_name != self.model_name:
            msg = "The model name suggestion: rename [ %s ] to [ %s ]" % (self.model_name, new_name)
            ColorPrint.show(msg, ColorPrint.YELLOW)
        else:
            ColorPrint.show("The model name check passed!", ColorPrint.GREEN)


# file (base64 encoding)tag
FILE_TAG = "__file__:"
PATH_END = "#"


def _generate_path(data):
    """
    generate a path tree for bytes items
    :param data: dict or list
    :return: path tree, dict object
    """
    path = {}
    idxs = []
    if isinstance(data, dict):
        idxs = data.keys()
    elif isinstance(data, list):
        idxs = range(len(data))
    elif isinstance(data, bytes):
        return PATH_END
    for k in idxs:
        sub_path = _generate_path(data[k])
        if sub_path:
            path[k] = sub_path
    return path


def base64_convert(data, decoding={}, encoding={}):
    path = decoding or encoding
    if not path:
        return data
    if path == PATH_END:
        if encoding:
            # for API response
            # encoding: convert bytes to base64
            assert isinstance(data, bytes)
            data = base64.b64encode(data)
            data = data.decode("utf8")
            data = FILE_TAG + data
        else:
            # for API request
            # decoding: convert base64(str) to bytes
            assert isinstance(data, str)
            data = data.startswith(FILE_TAG) and data[len(FILE_TAG):] or data
            data = data.encode("utf8")
            data = base64.b64decode(data)
        return data
    for p in path:
        subd, sube = decoding and (path[p], {}) or ({}, path[p])
        data[p] = base64_convert(data[p], subd, sube)
    return data


def benchmark(func, *args, **kwargs):
    import time
    times = 10
    print("Preheating ...")
    items = list(range(times))
    for _ in range(3):
        func(*args, **kwargs)
    print("10 tasks running ...")
    total_time_start = time.time()
    for _ in items:
        func(*args, **kwargs)
    avg_time = (time.time() - total_time_start) / times
    print("tasks running over!")
    ColorPrint.show("REAL Time Per Task: %f" % avg_time, ColorPrint.BLUE)


class CodeChecker(object):
    def __init__(self, model_name):
        self.model_name = model_name
        self.model_class = None
        self.break_check = False
        self._interrupted_msg = "checker is interrupted for existed errors or warnings..."

    def prepare_model(self):
        try:
            self.model_class = self._check_import()
            ColorPrint.show("Model instance has been created", ColorPrint.BLUE)
        except Exception as ex:
            ColorPrint.show("Create model instance failed:", ColorPrint.YELLOW)
            ColorPrint.show(str(ex), ColorPrint.RED)
            return False
        return True

    def _check_import(self):
        from importlib import import_module
        ColorPrint.show("trying to import module ...", ColorPrint.BLUE)
        module_fn = "{name}.api_model".format(name=self.model_name)
        app_module = import_module(module_fn)
        return app_module.Model

    def check_properties(self):
        if self.break_check:
            ColorPrint.show(self._interrupted_msg, ColorPrint.YELLOW)
            return
        ColorPrint.show("trying to check properties ...", ColorPrint.BLUE)
        ColorPrint.show("trying to import ...", ColorPrint.BLUE)
        attrs = ["model_name", "INPUTS_SAMPLE", "OUTPUTS_SAMPLE"]
        msg = "The class [%s.api_model.Model] dose not have the property [%s] \n" \
              "For more info about Base model or TFBase model: \n" \
              "[ https://confluence.zhihuiya.com/display/PR/modelhub.framework ]"
        for attr in attrs:
            if not getattr(self.model_class, attr):
                ColorPrint.show(msg % (self.model_name, attr), ColorPrint.RED)
                self.break_check = True
        if not self.break_check:
            ColorPrint.show("properties check passed!", ColorPrint.GREEN)

    def check_sample_running(self):
        from genson import SchemaBuilder
        from jsonschema import validate
        import os
        if self.break_check:
            ColorPrint.show(self._interrupted_msg, ColorPrint.YELLOW)
            return
        ColorPrint.show("trying to check sample ...", ColorPrint.BLUE)
        run_mode = os.getenv("RUN_MODE", "local")
        hostport = os.getenv("HOSTPORT", "")
        if self.model_class.TYPE == "NTF":
            model = self.model_class()
        elif self.model_class.TYPE == "TF":
            model = self.model_class(run_mode=run_mode, hostport=hostport)
        else:
            raise Exception("Invalid model type [%s]" % self.model_class.TYPE)
        inputs_sample = self.model_class.INPUTS_SAMPLE
        outputs_sample = self.model_class.OUTPUTS_SAMPLE
        output_encoding_path = _generate_path(outputs_sample)
        outputs_sample = base64_convert(outputs_sample, encoding=output_encoding_path)
        outputs = model.run(inputs_sample)
        outputs = base64_convert(outputs, encoding=output_encoding_path)
        outputs = json.loads(json.dumps(outputs))
        builder = SchemaBuilder()
        builder.add_object(outputs_sample)
        outputs_schema = builder.to_schema()
        try:
            validate(outputs, schema=outputs_schema)
            ColorPrint.show("outsputs schema check passed!", ColorPrint.GREEN)
        except Exception as ex:
            ColorPrint.show("=== schema check warning ===", ColorPrint.YELLOW)
            print(ex)
            print("=== schema check over ====")
        benchmark(model.run, inputs_sample)

    def check_requirements(self):
        import os
        req_file = "requirements.txt"
        if os.path.exists(req_file):
            cmd = "pipreqs --diff %s --print %s" % (req_file, self.model_name)
        else:
            cmd = "pipreqs --print %s" % self.model_name
        ColorPrint.show("Checking requirements ...", ColorPrint.BLUE)
        os.system(cmd)


@register("inspect")
class Command(BaseCommand):
    arguments = [
        option("-m", "--model_name", default=""),
    ]

    def run(self, model_name=None):
        """Inspect api_model module before submission, must run at root dir of project (same dir where setup.py locate)"""
        import os
        if not model_name:
            model_name = os.getcwd().split("/")[-1]
            if not os.path.exists(model_name):
                print("Could not determine the model name, please run with option -m")
                return
            ColorPrint.show("Determined model name => %s " % model_name, ColorPrint.YELLOW)
        # model code check
        code_checker = CodeChecker(model_name)
        if code_checker.prepare_model():
            # model name check
            # name_checker = GeneralChecker(model_name)
            # name_checker.regular_name_check()
            code_checker.check_properties()
            code_checker.check_sample_running()
            code_checker.check_requirements()
