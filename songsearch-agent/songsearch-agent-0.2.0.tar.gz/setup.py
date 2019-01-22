from setuptools import setup


setup(
    name="songsearch-agent",
    version="0.2.0",
    description="Helps SongSearch download",
    long_description="n/a",
    author="Peter Bengtsson",
    author_email="mail@peterbe.com",
    license="MIT",
    py_modules=["agent"],
    entry_points={"console_scripts": ["songsearch-agent = agent:main"]},
    install_requires=["requests"],
)
