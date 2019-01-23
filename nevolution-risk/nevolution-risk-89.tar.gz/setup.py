import setuptools
import subprocess

with open("README.md", "r") as fh:
    long_description = fh.read()

version = subprocess.run(['git', 'rev-list', '--all', '--count'], stdout=subprocess.PIPE)
version = version.stdout.decode('utf-8').replace('\n', '').replace('\r', '')

req = []
with open('requirements.txt', 'r') as file:
    for line in file:
        if line != '' or line != '\n':
            req.append(line)

setuptools.setup(
    name="nevolution-risk",
    version=version,
    author="nevolution.developers",
    author_email="basti.neubert@gmail.com",
    description="Python Gym Environment for the popular Risk game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nevolution.developers/slave/games/risk",
    packages=setuptools.find_packages(),
    package_dir={'nevolution_risk': 'nevolution_risk'},
    package_data={'nevolution_risk': ['res/*']},
    install_requires=req,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
