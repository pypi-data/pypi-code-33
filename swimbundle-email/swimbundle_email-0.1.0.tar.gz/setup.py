from setuptools import setup


def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()


with open('./README.rst') as f:
    long_description = f.read()

setup(
    name='swimbundle_email',
    packages=['swimbundle_email'],
    version='0.1.0',
    description='Swimlane Email Utility Package',
    author='Swimlane',
    author_email="info@swimlane.com",
    long_description=long_description,
    install_requires=parse_requirements('./requirements.txt'),
    keywords=['utilities', 'email', 'parsing'],
    classifiers=[],
)
