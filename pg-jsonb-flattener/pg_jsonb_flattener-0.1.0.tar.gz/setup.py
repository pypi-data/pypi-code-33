import os

import setuptools


ROOT = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(ROOT, 'README.rst')) as fp:
    readme = fp.read()

with open(os.path.join(ROOT, 'requirements', 'setup.pip')) as fp:
    setup_reqs = fp.read()

with open(os.path.join(ROOT, 'requirements', 'base.pip')) as fp:
    base_reqs = fp.read()

with open(os.path.join(ROOT, 'requirements', 'test.pip')) as fp:
    test_reqs = fp.read()

with open(os.path.join(ROOT, 'requirements', 'dev.pip')) as fp:
    dev_reqs = fp.read()


setuptools.setup(
    name='pg_jsonb_flattener',
    use_scm_version=True,
    author='Anthony SKORSKI',
    author_email='skorski.anthony+pg_jsonb_flattener@gmail.com',
    url='https://gitlab.com/askorski/pg_jsonb_flattener',
    license='MIT',
    description='JSONB data flattener for Postgresl',
    long_description=readme,
    py_modules=(
        'pg_jsonb_flattener',
    ),
    keywords=('postgresql', 'jsonb', 'sqlalchemy', ),
    # TODO: update the dev status
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Database',
    ),
    setup_requires=setup_reqs,
    install_requires=base_reqs,
    extras_require={
        'test': test_reqs,
        'dev': dev_reqs + test_reqs,
    }
)
