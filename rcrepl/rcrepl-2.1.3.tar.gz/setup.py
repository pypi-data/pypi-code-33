from setuptools import setup, find_packages

setup(
    name = "rcrepl",
    description='A python script that wraps a REPLs',
    url='http://github.com/sras/rcrepl',
    author='Sandeep.C.R',
    author_email='sandeepcr2@gmail.com',
    license='MIT',
    version = "2.1.3",
    packages = ['rcrepl'],
    entry_points = {
        "console_scripts":['rcelm18=rcrepl.rcelm:main18','rcelm=rcrepl.rcelm:main','rcghci=rcrepl.rcghci:main', 'rcrepl_nvim=rcrepl.rcrepl_nvim:main', 'rcrepl_vim=rcrepl.rcrepl_vim:main']
    },
    install_requires=[ 'pexpect' ]
)
