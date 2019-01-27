from setuptools import setup

setup(
    name="zhixuewang",
    version="0.1.4",
    keywords=("test", "xxx"),
    description="关于智学网的api",
    license="GPLv3",

    author="anwenhu",
    author_email="anemailpocket@163.com",

    packages=["zhixuewang"],
    include_package_data=True,
    platforms="any",
    install_requires=["requests"],

    scripts=[],
    entry_points={
        'console_scripts': [
            'test = test.help:main'
        ]
    }
)
