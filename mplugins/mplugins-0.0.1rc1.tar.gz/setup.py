import setuptools


setuptools.setup(
    name="mplugins",
    version="0.0.1c1",
    author="Taaku18",
    description="A utility tool for Discord Modmail plugins",
    url="https://github.com/Taaku18/Modmail-Plugins",
    packages=[
        'mplugins'
    ],
    install_requires=[
        'discord.py'
    ],
    dependency_links=[
        'git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        'Topic :: Utilities',
    ],
)