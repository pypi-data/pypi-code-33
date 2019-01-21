import setuptools

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="weibo-photos",
    version="0.3.0",
    author="darknoll",
    author_email="darknoll@126.com",
    description="Download Weibo photos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/darknoll/weibo_image_crawler",
    packages=setuptools.find_packages(),
    install_requires=["requests==2.21.0", "click==7.0", "rsa==4.0"],
    entry_points={
        'console_scripts': [
            'weibo-photos=weibo_photos.app:cli'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)