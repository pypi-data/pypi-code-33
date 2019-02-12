from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [l for l in f.readlines() if l.strip()]

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pycashaccount',
    version='0.3.2',
    author='emergent-reasons',
    author_email='emergentreasons@gmail.com',
    description='helper for creating cash accounts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/emergent-reasons/pycashaccount',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        cashaccount=cashaccount.cli:run
    ''',
)
