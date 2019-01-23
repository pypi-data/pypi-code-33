from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def get_version():
    with open('VERSION') as f:
        return f.read()


def get_requirements():
    with open('requirements.txt') as f:
        return f.readlines()


setup(name='cone',
      version=get_version(),
      description='A tool to sync projects to Roblox Studio',
      long_description=readme(),
      long_description_content_type='text/markdown',
      url='https://gitlab.com/rbx-cone/cone',
      author='Olivier Trepanier',
      author_email='olitrepanier@hotmail.com',
      keywords='roblox',
      packages=find_packages(),
      install_requires=get_requirements(),
      test_suite='tests',
      entry_points={'console_scripts': ['cone = console_cone:main']},
      zip_safe=False)
