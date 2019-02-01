import io
from setuptools import setup
import sys
import re

with io.open("README.rst") as readme_file:
    readme_text = readme_file.read()

VERSIONFILE = "autoqube_kubernetes/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in {0}.".format(VERSIONFILE))

if sys.version_info[:1] not in [(3, )]:
    sys.stderr.write("Sorry, only Python 3.x are supported at this time.\n")
    exit(1)

setup(name='autoqube_kubernetes',
      version=verstr,
      description='Kubernetes Handler module for AUTOQUBE load testing',
      license='BSD 3',
      keywords="kubernetes jmeter",
      author='Gautam Swaroop',
      author_email='gswaroop@cloudfxlabs.io',
      maintainer='Gautam Swarooop',
      maintainer_email='gswaroop@cloudfxlabs.io',
      url='https://gitlab.com/autoqube/aq-kubernetes',
      long_description=readme_text,
      packages=['autoqube_kubernetes'],
      package_dir={"autoqube_kubernetes": "autoqube_kubernetes"},
      install_requires=[
          'kubernetes',
          'pymongo',
          'pyyaml'
      ],
      zip_safe=False)
