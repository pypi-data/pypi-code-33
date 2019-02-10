import setuptools

requires = [
    "flake8 > 3.0.0"
]

setuptools.setup(
    name="flake8-rewriter",
    license="MIT",
    version="1.1.0",
    description="Flake8 plugin that rewrites error codes.",
    author="Isaac 'Izzy' Avram",
    author_email="avrisaac555@gmail.com",
    url="https://github.com/ILikePizza555/flake8-rewriter",
    packages=[
        "flake8_rewriter",
    ],
    install_requires=requires,
    entry_points={
        "flake8.report": [
            "rewriter = flake8_rewriter.rewriter:RewriteFormatter",
        ],
    },
    classifiers=[
        "Framework :: Flake8",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ]
)