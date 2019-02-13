from setuptools import setup, find_packages
import celespy

setup(name       = 'celespy',
    packages     = find_packages(),
    include_package_data=True,
    install_requires=['astropy'],
    python_requires='>=3.5',
    scripts      = [],
    version      = celespy.__version__,
    description  = 'Generic astronomy functions',
    url          = 'https://github.com/AlanLoh/celespy.git',
    author       = 'Alan Loh',
    author_email = 'alan.loh@obspm.fr',
    license      = 'MIT',
    zip_safe     = False)

# make the package:
# python3 setup.py sdist bdist_wheel
# upload it:
# python3 -m twine upload dist/*version*

# Release:
# git tag -a v*version* -m "annotation for this release"
# git push origin --tags