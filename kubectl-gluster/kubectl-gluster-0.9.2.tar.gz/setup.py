#
# Copyright (c) 2019 Red Hat, Inc.
#
# This file is part of gluster-health-report project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

from setuptools import setup


setup(
    name="kubectl-gluster",
    version="0.9.2",
    packages=["kubectl_gluster"],
    include_package_data=True,
    install_requires=["jinja2", "PyYAML", "requests"],
    entry_points={
        "console_scripts": [
            "kubectl-gluster = kubectl_gluster.main:main"
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Gluster Developers",
    author_email="gluster-devel@gluster.org",
    description="GlusterCS deployment tool",
    license="GPLv2",
    keywords="gluster, container, kubernetes, glustercs",
    url="https://github.com/aravindavk/kubectl-gluster",
    long_description="""
    GlusterCS deployment tool
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only"
    ],
)
