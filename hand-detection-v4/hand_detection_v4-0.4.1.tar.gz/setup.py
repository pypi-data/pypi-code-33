# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='hand_detection_v4',
    version='0.4.1',
    description=(
        'This is an installation package that detects the hand of the video.'),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='llz',
    author_email='hero1153@sina.com',
    license='MIT License',

    #packages = find_packages(),
     packages = ['hand_detection_v4', 'hand_detection_v4/models', 'hand_detection_v4/data'],
        package_data={  # Optional
        'hand_detection_v4': ['models/hand.our6_rfcnmv_320_50000']},

    platforms=["all"],
    #url='<null>',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)

