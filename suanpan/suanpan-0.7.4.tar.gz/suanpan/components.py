# coding=utf-8
from __future__ import print_function

import argparse
import contextlib
import copy
import itertools
import os
import re
import sys
import traceback
from collections import defaultdict

from suanpan import g, objects
from suanpan.arguments import Bool
from suanpan.log import logger


class Arguments(objects.Context):
    pass


class Result(objects.Context):
    def __init__(self, value):
        super(Result, self).__init__(value=value)


class Component(object):

    ENVIRONMENT_ARGUMENTS_KEYWORD = "SP_PARAM"

    devArguments = [Bool(key="debug", default=False)]
    defaultArguments = []

    def __init__(self, funcOrComponent):
        if isinstance(funcOrComponent, Component):
            self.runFunc = funcOrComponent.runFunc
            self.arguments = funcOrComponent.arguments
        else:
            self.runFunc = funcOrComponent
            self.arguments = defaultdict(list)

    def __call__(self, *arg, **kwargs):
        try:
            logger.setLogger(self.name)
            self.run(*arg, **kwargs)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise e

    @property
    def name(self):
        return self.runFunc.__name__

    def run(self, *arg, **kwargs):
        logger.info("Starting...")
        context = self.init()
        results = self.runFunc(context)
        self.save(context, results)
        logger.info("Done.")

    def init(self):
        restArgs = self.getArgList()
        devArgs, restArgs = self.parseDevArguments(restArgs)
        g.update(vars(devArgs))
        defaultArgs, restArgs = self.parseDefaultArguments(restArgs)
        context = self.getContext(defaultArgs)
        args, restArgs = self.parseArguments(self.getArguments(), restArgs)
        args = self.transformArguments(context, args)
        setattr(context, "args", args)
        return context

    def save(self, context, results):
        outputs = self.saveOutputs(context, results)
        self.closeContext()
        return outputs

    @contextlib.contextmanager
    def context(self, args=None):
        yield objects.Context()

    def getContext(self, *args, **kwargs):
        self.contextManager = self.context(*args, **kwargs)
        return next(self.contextManager.gen)  # pylint: disable-msg=e1101

    def closeContext(self):
        try:
            next(self.contextManager.gen)  # pylint: disable-msg=e1101
        except StopIteration:
            pass

    def parseDevArguments(self, argList=None):
        return self.parseArguments(
            self.devArguments, argList=argList, description="Dev arguments"
        )

    def parseDefaultArguments(self, argList=None):
        return self.parseArguments(
            self.defaultArguments, argList=argList, description="Default arguments"
        )

    def getArgList(self):
        return self.getArgListFromEnv() or self.getArgListFromCli()

    def getArgListFromCli(self):
        return sys.argv[1:]

    def getArgListFromEnv(self):
        argString = os.environ.get(self.ENVIRONMENT_ARGUMENTS_KEYWORD, "")
        regex = r"(--[\w-]+)\s+(?:(?P<quote>[\"\'])(.*?)(?P=quote)|([^\'\"\s]+))"
        groups = re.findall(regex, argString)
        argv = list(
            itertools.chain(*[(group[0], group[-2] or group[-1]) for group in groups])
        )
        return argv

    def parseArguments(self, arguments, argList=None, **kwargs):
        parser = argparse.ArgumentParser(**kwargs)
        for arg in arguments:
            arg.addParserArguments(parser)
        return parser.parse_known_args(argList)

    def transformArguments(self, context, args):
        self.loadArguments(args, self.getArguments())
        self.formatArguments(context, self.getArguments(exclude="outputs"))
        self.cleanArguments(context, self.getArguments(include="outputs"))
        arguments = {
            k: {arg.key: arg.value for arg in v if arg.isSet}
            for k, v in self.arguments.items()
        }
        arguments.update(
            {arg.key: arg.value for arg in itertools.chain(*self.arguments.values())}
        )
        return Arguments(**arguments)

    def loadArguments(self, args, arguments):
        return {arg.key: arg.load(args) for arg in arguments}

    def _safe_list(self, params=None):
        return [params] if isinstance(params, str) else list(params)

    def getArguments(self, include=None, exclude=None):
        includes = set(
            self.arguments.keys() if not include else self._safe_list(include)
        )
        excludes = set([] if not exclude else self._safe_list(exclude))
        includes = includes - excludes
        argumentsLists = [self.arguments[c] for c in includes]
        return itertools.chain(*argumentsLists)

    def formatArguments(self, context, arguments):
        return {arg.key: arg.format(context) for arg in arguments}

    def cleanArguments(self, context, arguments):
        return {arg.key: arg.clean(context) for arg in arguments}

    def saveMutipleOutputs(self, context, outputs, results):
        if isinstance(results, tuple) or isinstance(results, list):
            return {
                argument.key: argument.save(context, Result(result))
                for argument, result in zip(outputs, results)
            }
        elif isinstance(results, dict):
            return {
                argument.key: argument.save(context, Result(results.get(argument.key)))
                for argument in outputs
                if results.get(argument.key) is not None
            }
        else:
            raise Exception("Incorrect results: {}".format(results))

    def saveOneOutput(self, context, output, results):
        result = (
            Result(results[output.key])
            if isinstance(results, dict) and output.key in results
            else Result(results)
        )
        return {output.key: output.save(context, result)}

    def saveOutputs(self, context, results):
        logger.info("Saving...")
        outputs = list(self.getArguments("outputs"))
        if len(outputs) > 1:
            return self.saveMutipleOutputs(context, outputs, results)
        elif len(outputs) == 1:
            return self.saveOneOutput(context, outputs[0], results)

    def addArgument(self, arg, argtype="args", reverse=True):
        if reverse:
            self.arguments[argtype].insert(0, arg)
        else:
            self.arguments[argtype].append(arg)

    @classmethod
    def arg(cls, argument, argtype="args", reverse=True):
        def _dec(funcOrComponent):
            funcOrComponent = (
                funcOrComponent
                if isinstance(funcOrComponent, cls)
                else cls(funcOrComponent)
            )
            funcOrComponent.addArgument(argument, argtype=argtype, reverse=reverse)
            return funcOrComponent

        return _dec

    @classmethod
    def input(cls, *args, **kwargs):
        kwargs.update(argtype="inputs")
        return cls.arg(*args, **kwargs)

    @classmethod
    def output(cls, *args, **kwargs):
        kwargs.update(argtype="outputs")
        return cls.arg(*args, **kwargs)

    @classmethod
    def param(cls, *args, **kwargs):
        kwargs.update(argtype="params")
        return cls.arg(*args, **kwargs)

    @classmethod
    def column(cls, *args, **kwargs):
        kwargs.update(argtype="columns")
        return cls.arg(*args, **kwargs)
