"""Setup file for seedflow project."""


# [ Imports:Third Party ]
import setuptools  # type: ignore


setuptools.setup(
    name='seedflow',
    version='0.3.0',
    packages=setuptools.find_packages(),
    py_modules=['seedflow'],
    # a license
    license='MIT',
    # "classifiers", for reasons.  Below is adapted from the official docs at https://packaging.python.org/en/latest/distributing.html#classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    # keywords.  because classifiers are for serious metadata only?
    keywords="coroutines async side-effects data side-effects-as-data",
    install_requires=[
        'din',
        'rototiller',
        'pipe',
    ],
    extras_require={
        'test': [
            'bandit',  # installed for bin
            'better_exceptions',
            'blessed',
            'click',
            'coverage',
            'din',
            'flake8-assertive',  # imported by flake8
            'flake8-author',  # imported by flake8
            'flake8-blind-except',  # imported by flake8
            'flake8-bugbear',  # imported by flake8
            'flake8-builtins-unleashed',  # imported by flake8
            'flake8-commas',  # imported by flake8
            'flake8-comprehensions',  # imported by flake8
            'flake8-copyright',  # imported by flake8
            'flake8-debugger',  # imported by flake8
            'flake8-docstrings',  # imported by flake8
            'flake8-double-quotes',  # imported by flake8
            'flake8-expandtab',  # imported by flake8
            'flake8-imports',  # imported by flake8
            'flake8-logging-bymat',  # imported by flake8
            'flake8-mutable',  # imported by flake8
            'flake8-pep257',  # imported by flake8
            'flake8-self',  # imported by flake8
            'flake8-single-quotes',  # imported by flake8
            'flake8-super-call',  # imported by flake8
            'flake8-tidy-imports',  # imported by flake8
            'flake8-todo',  # imported by flake8
            'flake8',  # installed for bin
            'mypy',  # installed for bin
            'pylint',  # installed for bin
            'pipe',
            'vulture',  # installed for bin
        ],
        'dev': [
            'ptpython',  # installed for bin
        ],
    },
)
