from uperations.operation import Operation
import subprocess
from abc import abstractmethod

class CommandOperation(Operation):

    def _parser(self, main_parser):
        main_parser.add_argument('-c','--command', dest='command', help="Overwrite the command to be run")
        return main_parser

    def _before_start(self):
        super(CommandOperation, self)._before_start()
        return True

    def _on_running(self):
        super(CommandOperation, self)._on_running()
        return True

    def _on_error(self, exception):
        super(CommandOperation, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(CommandOperation, self)._on_completed()
        return True

    @abstractmethod
    def _command(self):
        raise NotImplementedError

    def _run(self):
        base_command = self.args.command if not self.args.command == None else self._command()
        command = [base_command]+ self.unknown_args
        proc = subprocess.Popen(command, shell=False)
        proc.communicate()
