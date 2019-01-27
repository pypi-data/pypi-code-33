from setuptools import setup


setup(
        author='Rohan Banerjee',
        author_email='banerjee.rohan98@gmail.com',
        name='solveerror',
        description='Python package for a cli tool for seamless debugging on the go.',
        url='https://github.com/rohanbanerjee/solverror',
        license='MIT',
        packages=['solveerror'],
        install_requires=[
            'bs4', 'requests',
            ],
        entry_points={
            'console_scripts': [
                'solveerror=solveerror:main',
                ]
            },
)