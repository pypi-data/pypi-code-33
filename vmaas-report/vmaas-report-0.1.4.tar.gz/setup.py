from setuptools import setup

setup(
    name="vmaas-report",
    description="A tool for getting vulnerabilities from VMaaS for given system package profile",
    version="0.1.4",
    license="MIT",
    author="Jan Dobes",
    author_email="jdobes@redhat.com",
    url="https://github.com/jdobes/vmaas-report",
    packages=["vmaas_report"],
    entry_points={  
        "console_scripts": [
            "vmaas-report = vmaas_report.main:main",
        ],
    },
    install_requires=[
        "requests",
    ],
    python_requires=">=2.6",
)
