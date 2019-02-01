from distutils.core import setup
setup(name='QualiLab_CLI', packages=['QualiLab_CLI'], version='1.0.6',
      description='Command line library suport Telnet and SSH for use with Quali CloudShell field solutions', author='Gregory Sloan',
      author_email='gregory.s@quali.com',
      url='https://github.com/QualiSystemsLab/QualiLab-CLI',
      download_url='https://github.com/QualiSystemsLab/QualiLab-CLI/tarball/1.0.6',
      keywords=['telnet', 'console', 'handler', 'ssh','cli','quali', 'cloudshell', 'exscript'], classifiers=[],
      install_requires=['exscript>=2.6.2,<2.7.0']
      )