from setuptools import setup


setup(
    name="masonite-billing.dev",
    version='0.1.5.dev',
    packages=[
        'billing',
        'billing.commands',
        'billing.contracts',
        'billing.controllers',
        'billing.drivers',
        'billing.factories',
        'billing.models',
        'billing.snippets',
    ],
    install_requires=[
        'masonite',
        'cleo',
        'stripe',
    ],
    include_package_data=True,
)
