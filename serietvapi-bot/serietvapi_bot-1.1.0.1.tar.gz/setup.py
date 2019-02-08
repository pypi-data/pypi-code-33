import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="serietvapi_bot",
    version="1.1.0.1",
    author="KingKaitoKid",
    author_email="tvditaly@altervista.org",
    description="Un semplice tool Python che si integra con le API del Bot Telegram @SerieTvItaly_bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KingKaitoKid/serietvapi_bot",
    packages=setuptools.find_packages(),
    install_requires=["youtube-dl", "telethon", "requests"],
    entry_points={
    'console_scripts': [
        'serietvapi_bot=serietvapi_bot.API_main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)