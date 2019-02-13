from uperations.operation import Operation
from abc import abstractmethod
import subprocess

class Dockeroperation(Operation):

    def _parser(self, main_parser):
        main_parser.add_argument('-d','--docker-container', dest='docker_container', help="URL of the docker container.")
        main_parser.add_argument('-n','--no-pull', dest='no_pull', help="Don't pull the docker container before running.")
        return main_parser

    def _before_start(self):
        super(Dockeroperation, self)._before_start()

        if not self.args.no_pull:
            print(self._docker_container())

            subprocess.check_output(['docker','pull',self._docker_container()])
        return True

    def _on_running(self):
        super(Dockeroperation, self)._on_running()
        return True

    def _on_error(self, exception):
        super(Dockeroperation, self)._on_error(exception)
        return True

    def _on_completed(self):
        super(Dockeroperation, self)._on_completed()
        return True

    def _run(self):
        subprocess.check_output(['docker','run',self._docker_container()] + self.unknown_args)

    @abstractmethod
    def _docker_container(self):
        raise NotImplementedError