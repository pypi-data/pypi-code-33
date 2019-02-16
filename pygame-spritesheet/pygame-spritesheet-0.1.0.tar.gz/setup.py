from setuptools import setup



setup(
    name="pygame-spritesheet",
    packages=["spritesheet"],
    version="0.1.0",
    license="MIT",
    description="Python pygame extension that provides SpriteSheet class.",
    author="Purple Ice",
    author_email="purpleice.git@gmail.com",
    url="https://github.com/purple-ice/pygame-spritesheet",
    download_url="https://github.com/purple-ice/pygame-spritesheet/archive/v0.1.0.tar.gz",
    keywords=["pygame", "sprites", "sheet", "spritesheet", "lightweight", "simple"],
    install_requires=["pygame"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
