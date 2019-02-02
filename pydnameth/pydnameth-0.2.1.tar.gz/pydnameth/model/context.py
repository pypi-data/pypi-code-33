from pydnameth.model.strategy.load import CPGLoadStrategy
from pydnameth.model.strategy.load import AttributesLoadStrategy
from pydnameth.model.strategy.get import CPGGetStrategy
from pydnameth.model.strategy.get import AttributesGetStrategy
from pydnameth.model.strategy.setup import TableSetUpStrategy
from pydnameth.model.strategy.setup import ClockSetUpStrategy
from pydnameth.model.strategy.setup import MethylationSetUpStrategy
from pydnameth.model.strategy.setup import ObservablesSetUpStrategy
from pydnameth.model.strategy.proc import TableProcStrategy
from pydnameth.model.strategy.proc import ClockProcStrategy
from pydnameth.model.strategy.proc import MethylationProcStrategy
from pydnameth.model.strategy.proc import ObservablesProcStrategy
from pydnameth.model.strategy.release import TableReleaseStrategy
from pydnameth.model.strategy.release import ClockReleaseStrategy
from pydnameth.model.strategy.release import MethylationReleaseStrategy
from pydnameth.model.strategy.release import ObservablesReleaseStrategy
from pydnameth.model.strategy.save import TableSaveStrategy
from pydnameth.model.strategy.save import ClockSaveStrategy
from pydnameth.model.strategy.save import MethylationSaveStrategy
from pydnameth.model.strategy.save import ObservablesSaveStrategy
from pydnameth.config.data.types import DataType
from pydnameth.config.setup.types import Task


class Context:

    def __init__(self,
                 config):

        if config.data.type == DataType.cpg:
            self.load_strategy = CPGLoadStrategy()
        elif config.data.type == DataType.attributes:
            self.load_strategy = AttributesLoadStrategy()

        if config.data.type == DataType.cpg:
            self.get_strategy = CPGGetStrategy()
        elif config.data.type == DataType.attributes:
            self.get_strategy = AttributesGetStrategy()

        if config.setup.task == Task.table:
            self.setup_strategy = TableSetUpStrategy(self.get_strategy)
        elif config.setup.task == Task.clock:
            self.setup_strategy = ClockSetUpStrategy(self.get_strategy)
        elif config.setup.task == Task.methylation:
            self.setup_strategy = MethylationSetUpStrategy(self.get_strategy)
        elif config.setup.task == Task.observables:
            self.setup_strategy = ObservablesSetUpStrategy(self.get_strategy)

        if config.setup.task == Task.table:
            self.proc_strategy = TableProcStrategy(self.get_strategy)
        elif config.setup.task == Task.clock:
            self.proc_strategy = ClockProcStrategy(self.get_strategy)
        elif config.setup.task == Task.methylation:
            self.proc_strategy = MethylationProcStrategy(self.get_strategy)
        elif config.setup.task == Task.observables:
            self.proc_strategy = ObservablesProcStrategy(self.get_strategy)

        if config.setup.task == Task.table:
            self.release_strategy = TableReleaseStrategy()
        elif config.setup.task == Task.clock:
            self.release_strategy = ClockReleaseStrategy()
        elif config.setup.task == Task.methylation:
            self.release_strategy = MethylationReleaseStrategy()
        elif config.setup.task == Task.observables:
            self.release_strategy = ObservablesReleaseStrategy()

        if config.setup.task == Task.table:
            self.save_strategy = TableSaveStrategy()
        elif config.setup.task == Task.clock:
            self.save_strategy = ClockSaveStrategy()
        elif config.setup.task == Task.methylation:
            self.save_strategy = MethylationSaveStrategy()
        elif config.setup.task == Task.observables:
            self.save_strategy = ObservablesSaveStrategy()

    def base_pipeline(self, config):
        self.load_strategy.load_base(config)
        self.setup_strategy.setup_base(config)
        self.proc_strategy.proc_base(config)
        self.release_strategy.release_base(config)
        self.save_strategy.save_base(config)

    def advanced_pipeline(self, config, configs_primary):
        self.load_strategy.load_advanced(config, configs_primary)
        self.setup_strategy.setup_advanced(config, configs_primary)
        self.proc_strategy.proc_advanced(config, configs_primary)
        self.release_strategy.release_advanced(config, configs_primary)
        self.save_strategy.save_advanced(config, configs_primary)

    def plot_pipeline(self, config, configs_primary):
        self.load_strategy.load_plot(config, configs_primary)
        self.setup_strategy.setup_plot(config, configs_primary)
        self.proc_strategy.proc_plot(config, configs_primary)
        self.release_strategy.release_plot(config, configs_primary)
        self.save_strategy.save_plot(config, configs_primary)


__all__ = ['Context']
