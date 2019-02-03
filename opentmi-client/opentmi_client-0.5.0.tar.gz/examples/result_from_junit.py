from os import path
from opentmi_client import Result

dir_path = path.dirname(path.realpath(__file__))
junit_file = path.join(dir_path, "../test/data/junit_simple.xml")
results = Result.from_junit_file(junit_file)

for result in results: print(result)
