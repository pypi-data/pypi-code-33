from pydnameth.model.strategy.load import CPGLoadStrategy
from pydnameth.model.strategy.load import AttributesLoadStrategy
from pydnameth.model.strategy.get import CPGGetStrategy
from pydnameth.model.strategy.get import AttributesGetStrategy
from pydnameth.model.strategy.setup import TableSetUpStrategy
from pydnameth.model.strategy.setup import ClockSetUpStrategy
from pydnameth.model.strategy.setup import MethylationSetUpStrategy
from pydnameth.model.strategy.setup import ObservablesSetUpStrategy
from pydnameth.model.strategy.proc import TableRunStrategy
from pydnameth.model.strategy.proc import ClockRunStrategy
from pydnameth.model.strategy.proc import MethylationRunStrategy
from pydnameth.model.strategy.proc import ObservablesRunStrategy
from pydnameth.model.strategy.release import TableReleaseStrategy
from pydnameth.model.strategy.release import ClockReleaseStrategy
from pydnameth.model.strategy.release import MethylationReleaseStrategy
from pydnameth.model.strategy.release import ObservablesReleaseStrategy
from pydnameth.model.strategy.save import TableSaveStrategy
from pydnameth.model.strategy.save import ClockSaveStrategy
from pydnameth.model.strategy.save import MethylationSaveStrategy
from pydnameth.model.strategy.save import ObservablesSaveStrategy
from pydnameth.config.experiment.types import Task
from pydnameth.config.experiment.types import DataType


class Context:

    def __init__(self, config):

        if config.experiment.type == DataType.cpg:
            self.load_strategy = CPGLoadStrategy()
        elif config.experiment.type == DataType.attributes:
            self.load_strategy = AttributesLoadStrategy()

        if config.experiment.type == DataType.cpg:
            self.get_strategy = CPGGetStrategy()
        elif config.experiment.type == DataType.attributes:
            self.get_strategy = AttributesGetStrategy()

        if config.experiment.task == Task.table:
            self.setup_strategy = TableSetUpStrategy(self.get_strategy)
        elif config.experiment.task == Task.clock:
            self.setup_strategy = ClockSetUpStrategy(self.get_strategy)
        elif config.experiment.task == Task.methylation:
            self.setup_strategy = MethylationSetUpStrategy(self.get_strategy)
        elif config.experiment.task == Task.observables:
            self.setup_strategy = ObservablesSetUpStrategy(self.get_strategy)

        if config.experiment.task == Task.table:
            self.run_strategy = TableRunStrategy(self.get_strategy)
        elif config.experiment.task == Task.clock:
            self.run_strategy = ClockRunStrategy(self.get_strategy)
        elif config.experiment.task == Task.methylation:
            self.run_strategy = MethylationRunStrategy(self.get_strategy)
        elif config.experiment.task == Task.observables:
            self.run_strategy = ObservablesRunStrategy(self.get_strategy)

        if config.experiment.task == Task.table:
            self.release_strategy = TableReleaseStrategy()
        elif config.experiment.task == Task.clock:
            self.release_strategy = ClockReleaseStrategy()
        elif config.experiment.task == Task.methylation:
            self.release_strategy = MethylationReleaseStrategy()
        elif config.experiment.task == Task.observables:
            self.release_strategy = ObservablesReleaseStrategy()

        if config.experiment.task == Task.table:
            self.save_strategy = TableSaveStrategy()
        elif config.experiment.task == Task.clock:
            self.save_strategy = ClockSaveStrategy()
        elif config.experiment.task == Task.methylation:
            self.save_strategy = MethylationSaveStrategy()
        elif config.experiment.task == Task.observables:
            self.save_strategy = ObservablesSaveStrategy()

    def pipeline(self, config, configs_child):

        if config.is_run:

            if not self.save_strategy.is_result_exist(config, configs_child):

                config.initialize()
                for config_child in configs_child:
                    config_child.initialize()

                self.load_strategy.load(config, configs_child)
                self.setup_strategy.setup(config, configs_child)
                self.run_strategy.run(config, configs_child)
                self.release_strategy.release(config, configs_child)
                self.save_strategy.save(config, configs_child)
