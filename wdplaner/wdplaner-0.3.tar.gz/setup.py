import setuptools

setuptools.setup(
    name="wdplaner",
    version="0.3",
    author="Enno Lohmeier",
    author_email="elo-pypi@nerdworks.de",
    include_package_data=False,
    package_dir={"":"wdplaner"},
    packages=setuptools.find_packages("wdplaner"),
    package_data={
        "wrd": ["templates/*.html", "templates/**/*.html", "static/**/*.*"],
        "wdplaner": ["static/**/*.*", "static/**/**/*.*"],
    },
    scripts=["wdplaner/manage.py"],
)
