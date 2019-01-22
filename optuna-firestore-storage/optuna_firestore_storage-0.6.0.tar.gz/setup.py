import os

from setuptools import setup


def get_version():
    version_filepath = os.path.join(os.path.dirname(__file__), 'optuna_firestore_storage', 'version.py')
    with open(version_filepath) as f:
        for line in f:
            if line.startswith('__version__'):
                return line.strip().split()[-1][1:-1]
    assert False


requires = [
    'grpcio',
    'optuna',
    'protobuf'
]

extras_require = {
    'build': [
        'grpcio-tools',
        'mypy-protobuf',
    ],
    'testing': [
        'grpcio-testing',
    ],
}

setup(
    name='optuna_firestore_storage',
    version=get_version(),
    description='It helps optuna to use Firestore as a backend DB.',
    url='https://gitlab.com/optuna-firestore-adapter/optuna-firestore-storage',
    author='Akira Sosa',
    author_email='akirasosa@gmail.com',
    license='MIT',
    packages=[
        "optuna_firestore_proto",
        "optuna_firestore_storage",
    ],
    install_requires=requires,
    tests_require=extras_require['testing'],
    extras_require=extras_require,
)
