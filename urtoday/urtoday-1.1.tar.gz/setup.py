import setuptools
import urtoday as urt

with open("README.md") as f:
    long_desc = f.read()


setuptools.setup(
        name="urtoday",
        version=urt.version,
        description="URtoday",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        url="https://github.com/poyynt/urtoday/",
        author="Parsa Torbati",
        author_email="parsa@programmer.net",
        packages=setuptools.find_packages(),
        python_requires=">=3.2",
        entry_points={
            "console_scripts": [
                "urtoday=urtoday.main:run",
                "urtoday-overview=urtoday.overview:run",
                ],
            },
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apple Public Source License",
            "Operating System :: OS Independent",
            "Development Status :: 5 - Production/Stable",
            "Natural Language :: English",
            "Topic :: Utilities",
            ],
        )
