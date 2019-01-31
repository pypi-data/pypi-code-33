from setuptools import setup
 
with open('README.md') as f:
    readme = f.read()
 
setup(
    name="ryakugo-pkg",
    version="0.0.8",
    packages=['tensorflow'],
    description='ExactTarget CLI Tool',
    long_description=readme,
    url='https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.10.0-py3-none-any.whl',
    author='Mikuni Motoi',
    author_email='n2i.motoi@gmail.com',
    license='MIT',
    # scripts=['bin/et', 'bin/et.cmd'],
    install_requires=[
        'tensorflow', "numpy", "mojimoji", "jaconv", "ipython", "keras", "pykakasi"
    ],
)



# from setuptools import setup

# packages = []
# install_requires = [
# "numpy", "mojimoji", "jaconv", "keras", "pykakasi","ipython",
# ]
# # 以下もライブラリの検索対象に加える
# dependency_links = [
#     'https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.10.0-py3-none-any.whl',
# ]
# # インストール対象にも加えておく
# dev_extras = [
#     'Mercurial',
#     'flake8',
#     'tensorflow',
# ]

# setup(
#     name='ryakugo_pkg',
#     version='0.0.5',
#     packages=packages,
#     install_requires=install_requires,
#     dependency_links=dependency_links,
#     extras_require=dict(
#         dev=dev_extras,
#     ),
# )



# import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

# setuptools.setup(
#     name="ryakugo_pkg",
#     version="0.0.2",
#     author="Mikuni Motoi",
#     author_email="mtotoimikuni@egmail.com",
#     description="A small example package",
#     long_description=long_description,
#     long_description_content_type="text/markdown",
#     # packages=setuptools.find_packages(),pip 
#     install_requires=["numpy", "mojimoji", "jaconv", "ipython", "keras", "pykakasi"],
#     dependency_links = ["https://storage.googleapis.com/tensorflow/mac/cpu/tensorflow-1.10.0-py3-none-any.whl"],
#     classifiers=[
#         "Programming Language :: Python :: 3",
#         "License :: OSI Approved :: MIT License",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python :: 3.6"
#     ],
# )
# numpy==1.15.4
# tensorflow==1.12.0
# Keras==2.2.4
# jaconv==0.2.3
# import pickle -> ipython
# mojimoji==0.0.8
# pykakasi