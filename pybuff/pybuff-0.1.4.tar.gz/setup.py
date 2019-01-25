from setuptools import setup

with open("README.md") as file:
        long_desc = file.read()

setup(
        name="pybuff",
        author="BigHeadGeorge",
        url="https://github.com/BigHeadGeorge/overbuff.py",
        version="0.1.4",
        packages=['pybuff'],
        zip_safe=True,
        description="A scraper for grabbing info from Overbuff.",
        long_description=long_desc,
        long_description_content_type="text/markdown",
        classifiers=[
                "Development Status :: 2 - Pre-Alpha",
                "License :: OSI Approved :: MIT License",
                "Programming Language :: Python :: 3",
                "Operating System :: OS Independent",
                "Intended Audience :: Developers",
                "Natural Language :: English",
                "Topic :: Internet",
                "Topic :: Software Development :: Libraries",
                "Topic :: Software Development :: Libraries :: Python Modules"
        ],
)
