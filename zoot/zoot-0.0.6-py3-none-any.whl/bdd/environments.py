from types import ModuleType
import inspect

from zoot.testing.common import Test, Suite
from zoot.bdd.common import Background, Scenario, IterableScenario, Feature, Step, Definition, StepDefinition
from zoot.testing.environments import Environment
from zoot.testing.reporting import ConsoleReporter

from zoot.utils import files, collections

from typing import Dict, List
from enum import Enum

import re

class Scope(Enum):

        BOF = 'bof'
        FEATURE = 'feature'
        BACKGROUND = 'background'
        SCENARIO = 'scenario'

        STEP = 'step'

        STEP_BACKGROUND = 'step-background'
        STEP_SCENARIO = 'step-scenario'

        END_SCENARIO = 'eo-scenario'
        END_BACKGROUND = 'eo-background'

        TAGS = 'tags'

        DATA_STEP = 'data-step'

        DATA_STEP_BACKGROUND = 'data-step-background'
        DATA_STEP_SCENARIO = 'data-step-scenario'

        DATA_ITERATION = 'data-iteration'

        KEYS_STEP = 'keys-step'
        KEYS_ITERATION = 'keys-iteration'
        
        ITERATION = 'iteration'
        EOF = 'eof'


class FeatureEnvironment(Environment):

    def __init__(self, parse_json:bool=True, *required_args:str, **optional_args:str):

        if not optional_args:
            optional_args = {}

        args = None

        if required_args:

            args = list(required_args)

            for arg in ['step_path', 'data_path', 'tags', 'mlo']:
                args.append(arg)

        else:
            args = ['step_path', 'data_path', 'tags', 'mlo']

        Environment.__init__(self, parse_json, self.post_build, *args, **optional_args)

        self.__dataPath = None
        self.__stepPath = None

        self.__mlo = None
        self.__tags = None

    def get_path_to_steps(self) -> str:
        return self.__stepPath

    def get_path_to_features(self)->str:
        return self.__dataPath

    def get_mlo(self) -> List[str]:
        return self.__mlo

    def get_tags(self) -> List[str]:
        return self.__tags

    def post_build(self, args:Dict[str, any]):

        self.__dataPath = args['data_path']
        self.__stepPath = args['step_path']
        self.__tags = []

        if self.parse_json:
            self.__mlo = args['mlo']
            self.__tags = args['tags']
        else:
            self.__tags = args['tags'].split(" ")

    def get_definitions(self, modules:List[ModuleType]) -> List[Definition]:

        definitions = []
        for module in modules:

            found_definitions = [member[1] for member in inspect.getmembers(module) if inspect.isfunction(member[1]) and "template" in member[1].__dict__ ]

            for found_definition in found_definitions:
                definitions.append(StepDefinition(found_definition))
                
        return definitions

    def load_suites(self) -> List[Suite]:
        
        suites = []

        found_suites = files.find_files(self.__dataPath, '.feature', '.component', '.suite')

        for name, path_to_suite in found_suites.items():

            count = sum(1 for line in open(path_to_suite))

            feature = None
            background = None
            iteration = None
            scenario = None
            step = None
            tags = []

            iterations = None

            with open(path_to_suite) as f:

                scope = None

                for index, line in enumerate(f):                    
                
                    line = line.strip(" \t\r\n")
                    if re.match("(Tests|Feature|Suite): (?P<feature>.+)", line):
                        if scope and scope != Scope.TAGS:
                            raise Exception("invalid feature field syntax, line:{}".format(index+1))

                        featureMatch = re.match("(Tests|Feature|Suite): (?P<feature>.+)", line)
                        name = featureMatch.group("feature")
                        feature = Feature(name, f.name)

                        scope = Scope.FEATURE

                    elif re.match("Background:?", line):

                        if scope != Scope.FEATURE:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        scope = Scope.BACKGROUND

                    elif re.match("Scenario: (?P<scenario>.+)", line):
                        
                        if scope != Scope.TAGS and scope != Scope.FEATURE and scope != Scope.STEP and scope != Scope.DATA_STEP and scope != Scope.DATA_ITERATION:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        if scenario and feature:
                            feature.append_tests(scenario)
                            scenario = None

                        scenarioMatch = re.match("Scenario: (?P<scenario>.+)", line)
                        name = scenarioMatch.group("scenario")

                        scenario = Scenario(name)
                        scope = Scope.SCENARIO

                    elif re.match("Scenario Outline: (?P<outline>).+", line):

                        if scope != Scope.TAGS and scope != Scope.FEATURE and scope != Scope.STEP and scope != Scope.DATA_STEP and scope != Scope.DATA_ITERATION:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        outlineMatch = re.match("Scenario Outline: (?P<outline>).+", line)
                        name = outlineMatch.group("outline")

                        scenario = IterableScenario(name)
                        scope = Scope.SCENARIO

                    elif re.match("(?:Given|When|Then|Step) (?P<step>.+)", line):
                        
                        #if scope != Scope.BACKGROUND and scope != Scope.SCENARIO and scope != Scope.STEP and scope != Scope.DATA_STEP:
                        if scope not in [Scope.BACKGROUND, Scope.SCENARIO, Scope.STEP, Scope.DATA_STEP_BACKGROUND, Scope.DATA_STEP_SCENARIO]:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        stepMatch =  re.match("(?:Given|When|Then|Step) (?P<step>.+)", line)
                        name = stepMatch.group("step")
                        step = Step(name, line_number=index+1)

                        if scope in [Scope.BACKGROUND, Scope.STEP_BACKGROUND, Scope.DATA_STEP_BACKGROUND]:
                            scope = Scope.STEP_BACKGROUND
                        elif scope in [Scope.SCENARIO, Scope.STEP_SCENARIO, Scope.DATA_STEP_SCENARIO]:
                            scope = Scope.STEP_SCENARIO

                    elif re.match("Examples:?", line):

                        if scope != Scope.STEP:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        scope = Scope.ITERATION


                    elif re.match(r"^(@\w+)(,@\w+)*$", line):
                        if scope != None and scope != Scope.TAGS and scope != Scope.DATA_STEP and scope != Scope.DATA_ITERATION:
                            raise Exception("invalid feature file syntax, line:{}".format(index+1))

                        foundTags = line.replace("@", "").replace(" ", "").split(",")

                        for tag in foundTags:
                            tags.append(tag)

                        scope = Scope.TAGS

                    elif re.match(r"\|([^|\n\r]+\|)*", line):

                        if scope != Scope.DATA_ITERATION and scope != Scope.ITERATION:
                            raise Exception("invalid feature file syntax: {}, line:{}".format(path_to_suite, index+1))

                        iteration = line.strip('|').split('|')

                        if scope == Scope.ITERATION:
                            scope == Scope.KEYS_ITERATION
                        else:
                            if not iterations or len(iteration) != iterations.get_size():
                                raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))
                            iterations.append_items(*iteration)
                            scope = Scope.DATA_ITERATION

                    elif line != "" and not line.startswith("#"):
                        raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))

                    else:
                        if scope in [Scope.STEP_BACKGROUND, Scope.DATA_STEP_BACKGROUND]:
                            scope = Scope.END_BACKGROUND
                        elif scope in [Scope.STEP_SCENARIO, Scope.DATA_STEP_SCENARIO, Scope.DATA_ITERATION]:
                            scope = Scope.END_SCENARIO


                    if scope == Scope.STEP_SCENARIO:

                        if scenario and step:
                            scenario.append_steps(step)
                            step = None
                        else:
                            raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))
                    elif scope ==  Scope.STEP_BACKGROUND:
                        if background and step:
                            background.append_steps(step)
                            step = None
                        else:
                            raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))
                    elif scope == Scope.BACKGROUND:
                        if feature and tags:
                            if tags: feature.append_tags(*tags)
                        else:
                            raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))

                    elif scope in [Scope.SCENARIO]:
                        if scenario:
                            if tags:
                                scenario.append_tags(*tags)
                                tags = []

                        elif background and feature and not feature.has_before():
                            feature.set_before(background)
                            background = None

                    elif scope in [Scope.END_SCENARIO]:
                        if scenario and feature:
                            feature.add_scenario(scenario)
                            scenario = None


                    elif scope == Scope.KEYS_ITERATION:
                        if (scenario and isinstance(scenario, IterableScenario)) and (iteration and isinstance(iteration, list)):
                            scenario.set_iterations(collections.TupleMap(False, *iteration))
                        else:
                            raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))
                        iteration = None

                    elif scope==Scope.DATA_ITERATION:
                        if (scenario and isinstance(scenario, IterableScenario)) and iteration and len(iteration) == scenario.get_iterations().get_size():
                            scenario.add_iteration(*iteration)
                        else:
                            raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))
                        iteration = None

            if scenario and feature:
                feature.add_scenario(scenario)
                scenario = None

            if background or scenario or tags or iteration:
                raise Exception("invalid feature file syntax {}, line:{}".format(path_to_suite, index+1))


            feature.set_listener(ConsoleReporter())
            suites.append(feature)

        return suites






