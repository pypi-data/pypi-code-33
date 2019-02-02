from setuptools import setup

setup(name='pytwig',
      version='0.1.6',
      description='Library for modifying and creating Bitwig files. (Not affiliated with Bitwig at all. Something something trademark of Bitwig GmbH etc.)',
      url='',
      author='jaxter184',
      author_email='jaxter184@gmail.com',
      license='GPL3',
      packages=['pytwig', 'pytwig.src', 'pytwig.src.lib', 'pytwig.src.lib.luts'],
      zip_safe=False)

# python setup.py sdist upload
