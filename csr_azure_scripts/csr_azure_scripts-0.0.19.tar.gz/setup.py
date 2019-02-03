from distutils.core import setup
project_name = 'csr_azure_scripts'
project_ver = '0.0.19'
setup(
    name=project_name,
    packages=[project_name],  # this must be the same as the name above
    version=project_ver,
    description='A library of scripts for Cisco guestshell on Azure',
    author='Christopher Reder',
    author_email='creder@cisco.com',
    scripts=["bin/capture-interface.py", "bin/cli.ps1",
             "bin/get_metadata.py", "bin/load-bin-from-storage.py",
             "bin/save-tech-support-to-storage.py", "bin/get-cli-cmds.py",
             "bin/get-show-cmds.py", "bin/save-config-to-storage.py",
             "bin/get-stat-drop.py"],
    # use the URL to the github repo
    url='https://github4-chn.cisco.com/csr1000v-azure/csr_azure_scripts.git',
    download_url='https://github4-chn.cisco.com/csr1000v-azure/csr_azure_scripts.git',
    keywords=['cisco', 'azure', 'guestshell'],
    classifiers=[],
    license="MIT",
    install_requires=[
        'configparser==3.5.0',
        'csr_azure_utils==0.0.102'
    ],
)
