from setuptools import setup
with open('README.rst') as f:
    readme = f.read()

setup(
    name='pyq-kernel',
    version='1.2',
    py_modules=['pyq.kernel'],
    package_dir={'pyq': '.'},
    data_files=[('q', ['pyq-kernel.p'])],
    description='PyQ kernel for Jupyter',
    long_description=readme,
    url='http://pyq.enlnt.com',
    author='Enlightenment Research, LLC',
    author_email='pyq@enlnt.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Environment :: Web Environment',
    ],
)
