try:
    from setuptools import setup,  find_packages
except ImportError:
    from distutils.core import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='gynx',
    version='0.0.1',
    description='Google Drive sync client for Linux',
    license="GPL",
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Matthew Levy',
    author_email='matt@webkolektiv.com',
    url="https://gitlab.com/ml394/gynx.git",
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'dictdiffer==0.7.1',
        'google-api-python-client==1.7.4',
        'google-auth==1.6.1',
        'google-auth-httplib2==0.0.3',
        'httplib2==0.12.0',
        'oauth2client==4.1.3',
        'pyasn1==0.4.4',
        'pytz==2018.7',
    ],
    scripts=['bin/gynx', 'bin/run.py'],
)
