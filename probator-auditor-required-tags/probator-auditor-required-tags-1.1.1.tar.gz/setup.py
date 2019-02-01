import os
from codecs import open

import setuptools


path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(path, 'README.md')) as fd:
    long_desc = fd.read()

setuptools.setup(
    name='probator-auditor-required-tags',
    use_scm_version=True,
    python_requires='~=3.7',

    entry_points={
        'probator.plugins.auditors': [
            'auditor_required_tags = probator_auditor_required_tags:RequiredTagsAuditor'
        ],
        'probator.plugins.types.issues': [
            'aws_required_tags = probator_auditor_required_tags.types:RequiredTagsIssue',
        ],
        'probator_auditor_required_tags.actions': [
            'aws_ec2_instance_stop = probator_auditor_required_tags.actions:aws_ec2_instance_stop',
            'aws_ec2_instance_remove = probator_auditor_required_tags.actions:aws_ec2_instance_remove',
        ]
    },

    packages=setuptools.find_packages(),
    setup_requires=['setuptools_scm'],
    install_requires=[
        'probator~=1.0',
        'more-itertools~=5.0',
        'pytimeparse==1.1.8',
        'pyexcel~=0.5.10',
        'pyexcel-io~=0.5.11',
        'pyexcel-xlsx~=0.5.6',
    ],
    extras_require={
        'dev': [],
        'test': [],
    },

    # Metadata for the project
    description='Required Tags auditor',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    url='https://github.com/bunjiboys/probator-auditor-required-tags/',
    author='Asbjorn Kjaer',
    author_email='bunjiboys+probator@gmail.com',
    license='License :: OSI Approved :: Apache Software License',
    classifiers=[
        # Current project status
        'Development Status :: 4 - Beta',

        # Audience
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',

        # License information
        'License :: OSI Approved :: MIT License',

        # Supported python versions
        'Programming Language :: Python :: 3.7',

        # Frameworks used
        'Framework :: Flask',
        'Framework :: Sphinx',

        # Supported OS's
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',

        # Extra metadata
        'Environment :: Console',
        'Natural Language :: English',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    keywords='cloud security',
)
