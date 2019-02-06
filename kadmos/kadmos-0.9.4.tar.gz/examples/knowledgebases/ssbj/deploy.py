import os

from ssbjkadmos.utils.database import deploy, clean

dir_path = os.path.dirname(os.path.realpath(__file__))

clean(dir_path)

deploy(dir_path)