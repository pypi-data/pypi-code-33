# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='hand_detection_v6',
    version='0.6.1',
    description=(
        'This is an installation package that detects the hand of the video.'),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='llz',
    author_email='hero1153@sina.com',
    license='MIT License',

    #packages = find_packages(),
    packages = ['hand_detection_v6/', 'hand_detection_v6/models/', 'hand_detection_v6/data/'],
    package_data={  # Optional
        'hand_detection_v6': ['models/frozen_inference_graph.pb']},

    platforms=["all"],
    #url='<null>',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)

