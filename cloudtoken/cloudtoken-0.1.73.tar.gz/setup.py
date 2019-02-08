from setuptools import setup
import os

VERSION = os.environ['VERSION']

PACKAGE_DATA = [
    'configs/config.yaml',
    'configs/proxy.yaml',
    'shell_additions/bashrc_additions',
    'shell_additions/fishconfig_additions',
]

extras_require = {
    'awscli': ['cloudtoken-plugin.awscli_exporter'],
}

all_extras = [item for sub in extras_require.values() for item in sub]

extras_require['all'] = all_extras

setup(
    name='cloudtoken',
    version=VERSION,
    description='Command line utility for authenticating with public clouds.',
    url='https://bitbucket.org/atlassian/cloudtoken/',
    author='Atlassian Cloud Engineering',
    author_email='cloud-team@atlassian.com',
    license='Apache',
    scripts=['bin/cloudtoken', 'bin/cloudtoken.cmd', 'bin/cloudtoken_proxy.sh', 'bin/awstoken'],
    zip_safe=False,
    install_requires=[
        "Flask>=0.12",
        "schedule>=0.4.2",
        "keyring>=8.7",
        "keyrings.alt>=2.2",
        "cloudtoken-plugin.shell-exporter",
        "cloudtoken-plugin.json-exporter",
        "cloudtoken-plugin.saml",
        "pyyaml",
        "requests>=2.9.1",
    ],
    extras_require=extras_require,
    packages=['cloudtoken'],
    include_package_data=True,
    python_requires='>=3.5',
    package_data={
        'cloudtoken': PACKAGE_DATA,
    },
)
