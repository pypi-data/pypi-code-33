import setuptools
import setuptools as s
try:
    import ready
except Exception:
    pass
with open("README.md", "r") as fh:
    long_description = fh.read()

long_description = long_description.replace('evry', 'every')
setuptools.setup(
    name="os_sys",
    version="0.3.3",
    author="Matthijs labots",
    
    author_email="libs.python@gmail.com",
    description="a big plus lib for more functions to use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://python-libs-com.webnode.nl/",
    python_requires='>=3',
    include_package_data=True,
    packages=['pack', 'pack.test', 'pack.programs', 'pack.data_files',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    project_urls={
        'all files': 'https://github.com/Matthijs990/os_sys',
        'Downloads': 'https://python-libs-com.webnode.nl/downloads/',
        'become a member': 'https://python-libs-com.webnode.nl/user-registration/',
        'download all files': 'https://github.com/Matthijs990/os_sys.git',
        'want to help': 'https://github.com/Matthijs990/os_sys/tree/master/do%20you%20want%20to%20help',
        'startpage': 'https://pypi.org/project/os-sys/',
    },
)
