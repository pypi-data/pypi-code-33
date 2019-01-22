#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 sts=4 tw=78 et:
# -----------------------------------------------------------------------------
import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='markdown_markup_emoji',
    version='0.1.2',
    author='Eloise Severin',
    author_email='Eloise.severin @ gmail.com',
    description='Python markdown extension for markup Emoji',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/EloiseSeverin/markdown_markup_emoji/',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=['Markdown>=3.0.0'],
    test_suite='tests',
    packages=['markdown_markup_emoji'],
    keywords = ['Markdown', 'extension', 'plugin', 'Emoji'],
    entry_points={
        'markdown.extensions': [
            'markup_emoji = markdown_markup_emoji.markdup_emoji:MarkupEmojiExtension']
    },
)
