#!/usr/bin/env python
'''
setup
Created by Seria at 04/11/2018 10:50 AM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nebulae",
    version="0.1.11",
    author="Seria",
    author_email="zzqsummerai@yeah.net",
    description="A novel and simple framework based on prevalent DL framework and other image processing libs."
                + " v0.0.11: rename LayoutSheet as BluePrint;"
                + " change the initial parts of Space Craft and Navigator;"
                + " merge log function in Aerolog as an interface exposed by Navigator.",
                # + " v0.1.10: make it simpler to use Dash Board module alone.",
                # + " v0.1.9: be able to remove EXIF without modifying raw images.",
                # + " v0.1.7: users can generate hdf5 as several files since generating large dataset at once is risky;"
                # + " In addition, mergeFuel function is provided for merging multiple hdf5 files;"
                # + " users can remove EXIF in images while generating data file by setting keep_exif as False.",
                # + " v0.1.6: add SE Resnets to Garage;"
                # + " read image in RGB mode of which number of channel is 3.",
                # + " v0.1.5: fix a bug would return wrong device id when looking for available gpu.",
                # + " v0.1.1: change the way to register stage;"
                # + " fix a bug in DashBoard may draw points in wrong places.",
                # + " v0.1.0: A roughly complete version. New parts, Engine, Time Machine, Dashboard and Navigator are added.",
                # + " v0.0.18: fix a bug would repeatedly append variable scope.",
                # + " v0.0.17: network layout will be saved as image instead of pdf;"
                # + " add components: RESHAPE, SLICE, CLIP;"
                # + " implement Time Machine.",
                # + " v0.0.15: fix a bug would lead to wrong implementation of ** symbol."
                # + " v0.0.14: unable to assemble DUPLICATE component without name but passing existent name is allowed."
                # + " v0.0.13: allow users to assemble DUPLICATE component without passing name;"
                # + " add RESIZE component;"
                # + " shorten automatically generated component names."
                # + " v0.0.12: fix wrong implementation on data augmentation;"
                # + " FuelGenerator will keep original image size if width or height is not given.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=setuptools.find_packages(),
    install_requires=
    ['graphviz',
     'h5py',
     'pillow',
     'piexif'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)