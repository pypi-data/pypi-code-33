from setuptools import setup, find_packages

requirements = [
    'elist',
    'edict'
]

setup_requirements = [
    'elist',
    'edict'
]

setup(
      name="rblk",
      version = "0.5",
      description="recursive match nested brackets",
      author="dapeli",
      url="https://github.com/ihgazni2/rblk",
      author_email='terryinzaghi@163.com', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/ihgazni2/rblk",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      py_modules=['rblk'], 
      )


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist

