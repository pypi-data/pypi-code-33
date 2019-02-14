import st
import os
import shutil
from .result import Result


class Sampler:
    @property
    def execution_path(self) -> str:
        main_path = os.path.join(os.path.dirname(__file__), '..')

        # build if SConstruct file exists
        if os.path.exists(os.path.join(main_path, 'SConstruct')):
            if os.system('cd {} && scons'.format(main_path)) != 0:
                raise self.Error("Compile C++ Driver Error")

        # try to find exe file in different paths
        execution_name = 'carrier_sample.exe'
        execution_path = execution_name
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, execution_name)
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, 'cpp_build', execution_name)
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, '..', '..', execution_name)
        if os.path.exists(execution_path):
            return os.path.abspath(execution_path)

        # try to find sample.exe in system path when release
        if shutil.which(execution_name):
            return shutil.which(execution_name)

        raise self.Error('Sample Driver Not Found')

    @property
    def p(self) -> st.Process:
        p = getattr(self, 'p_', None)
        if p is not None:
            return p

        p = st.Process(self.execution_path)
        setattr(self, 'p_', p)
        return p

    def communicate(self, command: str, executor: st.Process = None) -> Result:
        executor = executor or self.p

        executor.write_line(command)
        lines = executor.read_until('EOF')

        result = Result()
        exec(lines, result.__dict__)

        if result.error:
            raise self.Error("{}: {}".format(result.message, result.chinese_message))

        return result

    @property
    def is_measuring(self) -> bool:
        return self.communicate('is_measuring').measuring

    def measure(self, number_of_waveforms: int, first_percent: float, second_percent: float) -> None:
        self.communicate("to_measure {} {:.3f} {:.3f}".format(number_of_waveforms, first_percent, second_percent))

    def set_sampler(self, sampler_name: str) -> Result:
        return self.communicate("set_sampler {}".format(sampler_name))

    def get_sampler(self) -> Result:
        return self.communicate("get_sampler")

    def set_sampler_value(self, key: str, value: float) -> Result:
        return self.communicate("set_sampler_value {} {}".format(key, value))

    def get_sampler_value(self, key: str) -> Result:
        return self.communicate("get_sampler_value {}".format(key))

    def query(self) -> Result:
        result = self.communicate("to_query")
        result.process()
        return result

    class Error(RuntimeError):
        pass


sampler = Sampler()
