from zoot.bdd.environments import FeatureEnvironment
from zoot.testing.executors import Executor
from zoot.bdd.common import set_definitions
from zoot.utils.files import find_files, load_modules_ordered, load_modules

from unittest import TestSuite, TextTestRunner
from colorama import init as init_colorama

class FeatureExecutor(Executor):

    def __init__(self, environment:FeatureEnvironment):
        self.__environment = environment

    def execute(self):

        init_colorama()

        testSuite = TestSuite()

        self.__environment.build()

        suites = self.__environment.load_suites()
        pyFiles = find_files(self.__environment.get_path_to_steps(), '.py')
        loadedModules = []

        print("files:")
        print(pyFiles)

        if self.__environment.parse_json:
            print("parse json")
            loadedModules = load_modules_ordered(pyFiles, self.__environment.get_mlo())
        else:
            loadedModules = load_modules(pyFiles)

        print("kbhjjv")
        print(loadedModules)
        print("kbhjjv")

        set_definitions(self.__environment.get_definitions(loadedModules))

        for suite in suites:
            testSuite.addTest(suite)

        runner = TextTestRunner()
        runner.run(testSuite)