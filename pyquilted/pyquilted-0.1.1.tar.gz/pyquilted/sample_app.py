from pathlib import Path
from shutil import copyfile
import pyquilted


DATA_PATH = str(Path(pyquilted.__file__).resolve().parent)


class SampleApp:
    def __init__(self, src, dst):
        self.src = DATA_PATH + src
        self.dst = dst

    def run(self):
        copyfile(self.src, self.dst)
