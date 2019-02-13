
from uperation_base.operation_types.command_operation import CommandOperation
import subprocess

class Command(CommandOperation):

    @staticmethod
    def name():
        return "Command"

    @staticmethod
    def description():
        return "Run any command from the terminal"

    def _parser(self, main_parser):
        main_parser.add_argument('command', help="Command to be run")
        return

    def _run(self):
        command = [self.args.command]+ self.unknown_args
        proc = subprocess.Popen([self.args.command]+ self.unknown_args,shell=False)
        proc.communicate()
        proc.kill()
        #subprocess.check_output(command, stderr=subprocess.STDOUT)