# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='bslideshow',
    version='0.0.13',
    url='https://github.com/tuaplicacionpropia/bslideshow',
    download_url='https://github.com/tuaplicacionpropia/bslideshow/archive/master.zip',
    author=u'tuaplicacionpropia.com',
    author_email='tuaplicacionpropia@gmail.com',
    description='Python library for generate slideshow from blender.',
    long_description='Python library for generate slideshow from blender.',
    keywords='video, slideshow, blender',
    classifiers=[
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python', 
      'Programming Language :: Python :: 2.7', 
      'Intended Audience :: Developers', 
      'Topic :: Multimedia :: Graphics',
    ],
    scripts=[
      'bin/bs_split.cmd', 'bin/bs_split', 
      'bin/bs_scale.cmd', 'bin/bs_scale', 
      'bin/bs_frames.cmd', 'bin/bs_frames', 
      'bin/bs_banner.cmd', 'bin/bs_banner', 
      'bin/bs_footage.cmd', 'bin/bs_footage', 
      'bin/bs_bgmusic.cmd', 'bin/bs_bgmusic', 
      'bin/bs_transition.cmd', 'bin/bs_transition.cmd'
    ],
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='MIT',
    install_requires=[
        'requests==2.20.0',
        'Pillow==3.4.2',
        'hjson==2.0.2',
        'sbrowser==0.0.18',
    ],
)

