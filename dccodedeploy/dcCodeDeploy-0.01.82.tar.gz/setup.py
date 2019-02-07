from distutils.core import setup
setup(
    name='dcCodeDeploy',
    packages=['dcCodeDeploy'],  # this must be the same as the name above

    version='0.01.82',

    description='Deploys code to various tagets (AWS, internal VMs, etc) based on tags',
    author='Josh devops.center, Bob devops.center, Gregg devops.center',
    author_email='josh@devops.center, bob@devops.center, gjensen@devops.center',
    # use the URL to the github repo
    url='https://github.com/devopscenter/dcCodeDeploy',
    # I'll explain this in a second
    download_url='https://github.com/devopscenter/dcCodeDeploy/tarball/',
    keywords=['testing', 'logging', 'example'],  # arbitrary keywords
    classifiers=[],
)
