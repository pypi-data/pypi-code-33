from setuptools import setup, find_packages
import io
import os
import versioneer

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='tabulatehelper',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Converts tabular data like Pandas dataframe to GitHub Flavored Markdown table (wrapper around tabulate module).',
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/kiwi0fruit/tabulatehelper',

    author='Peter Zagubisalo',
    author_email='peter.zagubisalo@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # keywords='sample setuptools development',
    packages=find_packages(exclude=['docs', 'tests']),
    python_requires='>=3.6',
    install_requires=['pandas', 'tabulate>=0.8.2'],
)
