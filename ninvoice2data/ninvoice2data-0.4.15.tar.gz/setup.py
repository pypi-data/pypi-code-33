from setuptools import setup, find_packages

setup(
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'ninvoice2data.extract': [
            'templates/com/*.yml',
            'templates/de/*.yml',
            'templates/es/*.yml',
            'templates/fr/*.yml',
            'templates/nl/*.yml',
            'templates/ch/*.yml'],
    },
)
