# coding=utf-8
from setuptools import setup, find_packages

setup(
    name='hand_detection_v7',
    version='0.4.1',
    description=(
        'This is an installation package that detects the hand of the video.'),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='llz',
    author_email='hero1153@sina.com',
    license='MIT License',

    #packages = find_packages(),
    packages = ['hand_detection_v7', 'hand_detection_v7/models', 'hand_detection_v7/data'],
    package_data={  # Optional
        'hand_detection_v7': ['models/frozen_inference_graph.pb',
        'data/hand_label_map.pbtxt','data/101968001/101968001_roleid_1_1532946600_out-video-jzccda1caa6f5544519191477b40c3030f_f_1532946591547_t_1532948297067.flv_01703.png']},

    platforms=["all"],
    #url='<null>',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

)

