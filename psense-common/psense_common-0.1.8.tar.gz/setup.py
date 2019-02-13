import io
from setuptools import find_packages, setup

main_ns = {}
exec(open('psense_common/version.py').read(), main_ns)

setup(
    name="psense_common",
    version=main_ns['__version__'],
    description="PercuSense Common Modules",
    author="Brad Liang",
    author_email='brad.liang@percusense.com',
    url="https://bitbucket.org/psense/psense-common",
    license='MIT',
    packages=find_packages(),
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'boto3',
        'numpy',
        'scipy',
        'pandas',
        'pytz'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
