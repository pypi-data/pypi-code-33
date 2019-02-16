import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="turta_iothat",
    version="1.1.1",
    author="Turta LLC",
    author_email="support@turta.io",
    description="Python Libraries for Turta IoT HAT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.turta.io/iot-hat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Topic :: System :: Hardware",
    ],
    project_urls={
        'Documentation': 'https://docs.turta.io/raspberry-pi-hats/iot-hat',
        'Community': 'https://community.turta.io',
        'GitHub Repository' : 'https://github.com/Turta-io/IoTHAT',
    },
)