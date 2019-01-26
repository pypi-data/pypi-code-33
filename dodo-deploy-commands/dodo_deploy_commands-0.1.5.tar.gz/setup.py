from setuptools import setup

setup(
    name='dodo_deploy_commands',
    version='0.1.5',
    description='Deployment related Dodo Commands',
    url='https://github.com/mnieber/dodo_deploy_commands',
    download_url=
    'https://github.com/mnieber/dodo_deploy_commands/tarball/0.1.5',
    author='Maarten Nieber',
    author_email='hallomaarten@yahoo.com',
    license='MIT',
    packages=[
        'dodo_deploy_commands',
    ],
    package_data={
        'dodo_deploy_commands': [
            'drop-in/*.yaml',
            'drop-in/*.md',
            'drop-in/deploy-tools/docker/Dockerfile',
            'drop-in/ssh-agent/docker/Dockerfile',
        ]
    },
    entry_points={},
    install_requires=[],
    zip_safe=False)
