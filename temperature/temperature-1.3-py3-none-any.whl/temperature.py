import st
import os
import shutil


class Temperature:
    @property
    def execution_path(self) -> str:
        main_path = os.path.join(os.path.dirname(__file__), '..')

        # build if SConstruct file exists
        if os.path.exists(os.path.join(main_path, 'SConstruct')):
            if os.system('cd {} && scons'.format(main_path)) != 0:
                raise self.Error("Compile C++ Temperature Error")

        # try to find exe file in different paths
        execution_name = 'temperature.exe'
        execution_path = execution_name
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, execution_name)
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, 'cpp_build', execution_name)
        if not os.path.exists(execution_path):
            execution_path = os.path.join(main_path, '..', '..', execution_name)
        if os.path.exists(execution_path):
            return os.path.abspath(execution_path)

        # try to find temperature.exe in system path when release
        if shutil.which(execution_name):
            return shutil.which(execution_name)

        raise self.Error('Temperature exe Not Found')

    @property
    def p(self) -> st.Process:
        p = getattr(self, 'p_', None)
        if p is not None:
            return p

        p = st.Process(self.execution_path)
        setattr(self, 'p_', p)
        return p

    def communicate(self, command: str, executor: st.Process = None) -> float:
        executor = executor or self.p

        executor.write_line(command)
        lines = executor.read_until('EOF')

        temperature = -1
        exec(lines)
        return temperature

    @property
    def value(self) -> float:
        return self.communicate('get_temp')

    class Error(RuntimeError):
        pass

temp = Temperature()
