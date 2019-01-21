from mlpc.runs.training_run import TrainingRun
import mlpc.configuration
from mlpc.entity.parameters import ParameterReader
import mlpc.utils.log

parameters = ParameterReader()

# TODO Type annotations on everything
# TODO Data warnings. e.g. to few instances in a categorical feature?


# noinspection PyProtectedMember
def new_training_run():  # TODO Possibility for a run name
    run = TrainingRun()
    mlpc.utils.log.configure(run)
    run.start()
    return run


def sort_runs_by_measurement(measurement_name):
    raise NotImplementedError("sort_runs_by_measurement is not implemented yet.")
