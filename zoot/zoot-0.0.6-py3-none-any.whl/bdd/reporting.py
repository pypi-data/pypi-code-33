from zoot.testing.reporting import Reporting
from zoot.testing.common import Suite
from zoot.bdd.common import Scenario, IterableScenario, Background

import re, time, json, os

class BDDReporter():

    def json(self, *suites:Suite)->str:

        all_json = []

        for suite in suites:

            suite_json = {}

            suite_json = {}
            suite_json['name'] = suite.get_name().strip(' \n\t\t')
            suite_json['description'] = ''
            suite_json['id'] = re.sub(r'\s+', '-', suite_json['name'])
            suite_json['uri'] = suite.get_file_name()
            suite_json['keyword'] = 'Feature'
            suite_json['line'] = 0
            suite_json['elements'] = []

            for test in suite.get_tests():

                if test.is_skipped():
                    continue

                test_json = {}

                test_json['name'] = test.get_name()
                test_json['id'] = re.sub(r'\s+', '-', '{}:{}'.format(suite_json['id'], test_json['name']))
                test_json['description'] = ''

                if isinstance(test, Scenario):
                    test_json['keyword'] = 'Scenario'
                    test_json['type'] = 'scenario'

                if isinstance(test, IterableScenario):
                    test_json['keyword'] = 'Scenario Outline'
                    test_json['type'] = 'scenario'

                if isinstance(test, Background):
                    test_json['keyword'] = 'Background'
                    test_json['type'] = 'background'

                test_json['steps'] = []

                if isinstance(test, (Scenario, IterableScenario, Background)):
                    for step in test.get_steps():

                        step_json = {}

                        step_json['name'] = step.get_string().strip(' \n\r\t')
                        step_json['keyword'] = 'Step'
                        step_json['line'] = step.get_line_number()
                        step_json['match'] = {'location':'{}:{}'.format(suite_json['uri'], step.get_line_number())}
                        step_json['result'] = {'status':'failed' if step.is_failed() else 'passed', 'duration':0}
                        step_json['embeddings'] = []

                        if step.is_failed():
                            step_json['result']['error_message'] = test.get_error()

                        test_json['steps'].append(step_json)

                    suite_json['elements'].append(test_json)

                all_json.append(suite_json)

            if not os.path.exists("json"):
                os.makedirs("json")
            
            with open("json/{}.json".format(str(time.time()).replace(".", "")), "a") as f:
                f.write(json.dumps(all_json))

    def xml(self, *suites:Suite)->str:
        return None