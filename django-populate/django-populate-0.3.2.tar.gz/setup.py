import os

from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return 'No README found.'


def get_dependencies_array(dev=False):
    fpath = dev and "requirements.dev.txt" or "requirements.txt"
    with open(fpath, "r") as f:
        arr = [s for s in f.readlines() if not s.startswith("-i")]
        if dev:
            arr = get_dependencies_array() + arr
        return arr


setup(
    name='django-populate',
    version=__import__('django_populate').__version__,
    author='SolarLiner',
    author_email='solarliner@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://gitlab.com/solarliner/django-populate',
    license='MIT',
    description=u' '.join(__import__('django_populate').__doc__.splitlines()).strip(),
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django'
    ],
    keywords='faker populate database fixtures data test django',
    long_description=read_file('README.rst'),
    install_requires=get_dependencies_array(),
    tests_require=get_dependencies_array(dev=True),
    test_suite="runtests.run_tests",
    zip_safe=False,
)
