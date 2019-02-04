from enum import Enum
from typing import List, Dict, Callable
from abc import ABC, abstractmethod
import re

from zoot.utils.collections import TupleMap
from zoot.testing.reporting import ConsoleReporter

from zoot.testing.common import Before, Test, TestListenerHandler, TestListener, Suite


class Definition(ABC):

    @abstractmethod
    def matches(self, **data) -> bool:
        pass

    @abstractmethod
    def execute(self, **data)->Exception:
        pass

class StepDefinition(Definition):

    def __init__(self, func:Callable[..., Exception]):

        if "keyword" not in func.__dict__:
            raise Exception('invalid step definition: keyword not found')

        if "template" not in func.__dict__:
            raise Exception('invalid step definition: template not found')

        self.func = func

    def get_template(self)->str:
        return self.func.__dict__['template']

    def matches(self, **data) -> bool:

        template = self.func.__dict__["template"]

        if re.match(template, data["original"]):
            return True
        return False

    def execute(self, **data)->Exception:

        if not self.matches(**data):
            return Exception('does not match step definition')

        try:
            template = self.func.__dict__["template"]
            match = re.match(template, data["original"])
            if match:
                kwargs = match.groupdict()
                return self.func(**kwargs)
            return Exception('does not match step template')
        except Exception as e:
            return e

def step_definition(keyword:str, template:str, func:Callable[..., Exception]) -> StepDefinition:

    func.__dict__["keyword"] = keyword
    func.__dict__["template"] = template

    return StepDefinition(func)

def keyword_definition(template:str, func:Callable[..., Exception]) -> StepDefinition:
    return step_definition("keyword", template, func)

def given_definition(template:str, func:Callable[..., Exception]) -> StepDefinition:
    return step_definition("given", template, func)

def when_definition(template:str, func:Callable[..., Exception]) -> StepDefinition:
    return step_definition("when", template, func)

def then_definition(template:str, func:Callable[..., Exception]) -> StepDefinition:
    return step_definition("then", template, func)

def and_definition(template:str, func:Callable[..., Exception]) -> StepDefinition:
    return step_definition("and", template, func)
            
step_definitions:List[Definition] = None

def set_definitions(definitions:List[Definition]):
    global step_definitions
    step_definitions = definitions

def find_definition(string:str) -> Definition:
    global step_definitions

    if step_definitions is None:
        return None
    
    for definition in step_definitions:
        if definition.matches(original=string):
            return definition

    return None
    
class Step(ABC):

    def __init__(self, string:str, data:TupleMap=None, line_number:int=-1):
        self.__string = string
        self.string = string
        self.data = data
        self.line_number = line_number
    
    def get_original_string(self)->str:
        return self.__string

    def get_string(self)->str:
        return self.string

    def set_string(self, string:str):
        self.string = string

    def execute(self) -> Exception:

        definition = find_definition(self.get_original_string())
        if definition is None:
            return Exception('no matching definition found')
        return definition.execute(original=self.get_original_string())

    def __str__(self):
        return "\tStep: {}".format(self.__string)      



class Background(Before):

    def __init__(self, *steps:Step):
        Before.__init__("Background")
        self.__error = None
        self.__steps = []
        if steps:self.append_steps(*steps)

    def get_steps(self) -> List[Step]:
        return self.__steps

    def append_steps(self, *steps:Step):
        for step in steps:
            self.__steps.append(step)

    def get_error(self) -> Exception:
        return self.__error

    def has_error(self) -> bool:
        if self.__error:
            return True
        return False

    def run(self) -> Exception:

        for index, step in enumerate(self.get_steps()):

            self.__error = step.execute()

            if self.has_error():
                return Exception("step({}): {}\n|{}".format(index, step, self.get_error()))

        return None

class Scenario(Test, TestListenerHandler):

    def __init__(self, name:str, tags:List[str]=[], *steps:List[Step]):

        Test.__init__(self, name)
        TestListenerHandler.__init__(self)

        self.__skip = False
        self.__error = None

        self.__background = None

        self.__time_start = None
        self.__time_stop = None

        self.__tags = []
        self.__steps = []

        if tags:self.append_tags(*tags)
        if steps:self.append_steps(*steps)

    def append_steps(self, *steps:Step):
        for step in steps:
            self.__steps.append(step)

    def append_tags(self, *tags:str):
        for tag in tags:
            self.__tags.append(tag)

    def get_steps(self)->List[Step]:
        return self.__steps

    def run_test(self):
                
        if self.is_skipped():
            if self.has_listener():
                self.get_listener().on_test_skipped(self)
            self.skipTest('')

        if self.has_listener():
            self.get_listener().on_test_started(self)

        if self.__background:
            self.__error = self.__background.run()

        if self.has_error():
            self.get_listener().on_test_failed(self)
            self.fail("background: {}".format(self.get_error()))

        for index, step in enumerate(self.__steps):
            self.__error = step.execute()
            if self.has_error():
                if self.has_listener():
                    self.get_listener().on_test_failed(self)
                self.fail("step: {}".format(self.get_error()))
                
        if self.has_listener():
            self.get_listener().on_test_success(self)

    def get_error(self) -> Exception:
        return self.__error

    def has_error(self) -> bool:
        if self.__error:
            return True
        return False     

    def __str__(self):
         return "Test: {}, Steps: {}".format(self.get_name(), len(self.__steps))

class IterableScenario(Test, TestListenerHandler):

    def __init__(self, name:str, tags:List[str]=[], *steps:Step):
        Test.__init__(self, 'run_test', name)
        TestListenerHandler.__init__(self, None)

        self.__iterations = TupleMap()
        self.__error = None

        self.__skip = False
        self.__tags = []
        self.__steps = []

        self.__background = None
        self.__listener = None
        
        self.__time_start = None
        self.__time_stop = None
    

        if tags:
            self.append_tags(*tags)

        if steps:
            self.append_steps(*steps)

    def set_listener(self, listener):
        self.__listener = listener

    def get_listener(self)->TestListener:
        return self.__listener

    def set_before_all(self, background):
        self.__background = background

    def append_steps(self, *steps:Step):
        for step in steps:
            self.__steps.append(step)

    def append_tags(self, *tags:str):
        for tag in tags:
            self.__tags.append(tag)

    def get_steps(self)->List[Step]:
        return self.__steps

    def add_iteration(self, *iteration:str):
        if iteration is not None:
            self.__iterations.append_items(*iteration)

    def set_iterations(self, iterations:TupleMap):
        self.__iterations = iterations

    def get_iterations(self)->TupleMap:
        return self.__iterations

    def run_test(self):

        if self.is_skipped():
            if self.has_listener():
                self.get_listener().on_test_skipped(self)
            self.skipTest('')

        for i in range(0, self.__iterations.get_tuple_size()):
        
            if self.__background:
                self.__error = self.__background.run()

            with self.subTest(i=i):
                #if self.__reporter: self.reporter.report_test(self)
                if self.has_listener():
                    self.get_listener().on_test_started(self)

                if self.__error:
                    if self.has_listener():
                        self.get_listener().on_test_failed(self)
                    self.fail("background: {}".format(self.__error))

                for index, step in enumerate(self.get_steps()):

                    string = None

                    for k, iteration in enumerate(self.__iterations.get_values_at(i)):
                        string = step.get_original_string().replace("<{}>".format(self.__iterations.get_key(k)), iteration.strip(' \n\r\t'))
                        
                    step.set_string(string)

                    self.__error = step.execute()

                    if self.has_error():
                        self.get_listener().on_test_failed(self)
                        self.fail("iteration: {}, step: {} {}\n|{}".format(i, index, step.get_string(), self.__error))
        
        self.get_listener().on_test_success(self)

    def get_error(self) -> Exception:
        return self.__error

    def has_error(self) -> bool:
        if self.__error:
            return True
        return False  

    def __str__(self):
         return "Test: {}, Steps: {}".format(self.__name, len(self.__steps))


class Feature(Suite):

    def __init__(self, name:str, file_name:str, tags:List[str]=[], *tests:Test):
        Suite.__init__(self, name, *tests)
        self.__tags = tags if tags else []
        self.__file_name = file_name
        self.set_listener(ConsoleReporter())

    def get_file_name(self) -> str:
        return self.__file_name

    def append_tags(self, *tags:str):
        if tags:
            for tag in tags:
                self.__tags.append(tag)

    def get_tags(self) -> List[str]:
        return self.__tags

    def add_scenario(self, *tests:Test):

        for test in tests:
            if test and isinstance(test, (Scenario, IterableScenario)):
                for tag in self.get_tags():
                    if (tag.startswith("~") and tag[1:] in test.get_tags()):
                        test.skip()
                    elif not tag.startswith("~") and (tag not in test.get_tags()):
                        test.skip()
                
                if self.has_listener() and not test.has_listener():
                    test.set_listener(self.get_listener())

                self.add_tests(*tests)

    def __str__(self):
        return "Suite: {}, Count: {}, Tags: {}".format(self.__name, len(self.get_tests()), self.get_tags())
