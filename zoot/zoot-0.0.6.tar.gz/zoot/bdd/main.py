from zoot.bdd.executors import FeatureExecutor
from zoot.bdd.environments import FeatureEnvironment

from zoot.bdd.common import step_definitions

def main():
    features = FeatureEnvironment(parse_json=True)
    executor = FeatureExecutor(features)
    executor.execute()
    return 0