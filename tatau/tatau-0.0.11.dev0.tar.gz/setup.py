import setuptools
import versioneer

# if versioneer.get_versions()["dirty"]:
#     raise RuntimeError("please commit everything before making tarballs")

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tatau',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Tatau Limited',
    # author_email="author@example.com",
    # description="A small example package",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TatauCloud/tatau',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    # TODO: revert when core will be switched to the horovod 0.15
    # install_requires=[
    #     'numpy==1.14.5',
    #     'torchvision==0.2.1',
    #     'torch==1.0.0',
    #     'keras==2.2.4',
    #     'tensorflow==1.12.0',
    #     'tensorboard==1.12.0'
    # ],
    install_requires=[
        'numpy==1.14.5',
        'h5py==2.8.0',
        'torchvision==0.2.1',
        'torch==0.4.1',
        'keras==2.2.2',
        'tensorflow==1.10.0',
        'tensorboard==1.10.0'
    ]

)
