from setuptools import setup, find_packages

REQUIREMENTS = [
    'setuptools',
    'pyserial',
    'progressbar2',
]

setup(
    name='py-asa-loader',
    version='0.3.3',
    description = 'The program to load binary into ASA series board.',
    long_description='',
    author = 'mickey9910326',
    author_email = 'mickey9910326@gmail.com',
    url='https://github.com/mickey9910326/py-asa-loader',
    license = 'MIT',
    packages=find_packages(),
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'asaloader = asaprog.loader:run',
            'asadevsim = asaprog.simulator:run',
        ],
    },
    install_requires=REQUIREMENTS
)
