import setuptools

with open("README.md", "r") as fh:
    for line in fh.readlines():
        if "Version" in line:
            version = line.split(":")[1].strip().rstrip('\n')

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [
    'requests',
    'urllib3',
    'cython',
    'pyyaml',
    'boto3',
    'pymysql',
    'docker',
    'GPUtil',
    'psycopg2-binary'
]

print("Build: ddlworker")
print(". Version: {}".format(version))
print(". Requirements: {}".format(requirements))

setuptools.setup(
    name="ddlworker",
    version=version,
    author="YL & SW",
    author_email = 'nedlitex0053@gmail.com',
    description="cli for distributed deep learning worker",
    url="https://githublu.github.io/DeepLearningCluster/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=['*.test', '*.test.*', 'test.*', 'test', 'data_container', ]),
    entry_points={
        'console_scripts': [
            'ddlworker=main.worker_main:main',
        ],
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)