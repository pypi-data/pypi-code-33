
from uperations.operation import Operation
import shutil
import os

class Dockerfile(Operation):

    @staticmethod
    def name():
        return "Dockerfile"

    @staticmethod
    def description():
        return "Create a docker file at the root of the directory."

    def _parser(self, main_parser):
        main_parser.add_argument('--force', dest='force', help="Overwritte the Dockerfile if exists", action='store_true')
        return

    def _run(self):
        if os.path.isfile(os.path.join(os.getcwd(),"Dockerfile")):
            if not self.args.force:
                print("Dockerfile already exists. Use --force to overwrite: %s" % (os.path.join(os.getcwd(),'Dockerfile')))
                return

        shutil.copy(self.resource_file('Dockerfile'),os.path.join(os.getcwd(),"Dockerfile"))


    def _id_publishable(self):
        return False