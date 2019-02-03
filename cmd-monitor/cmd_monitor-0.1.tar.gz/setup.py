from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='cmd_monitor',
      version='0.1',
      description='python plugin for vim debugger',
      long_description=readme(),
      url='https://github.com/esquires/cmd_monitor',
      author='Eric Squires',
      author_email='eric.g.squires@gmail.com',
      license='GPL',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Unix',
          'Operating System :: POSIX :: Linux'
          ],
      entry_points={
          'console_scripts': ['cmd_monitor=cmd_monitor.cmd_monitor:main'],
      },
      packages=['cmd_monitor'])
