from setuptools import setup

main_ns = {}
exec(open('dash_core_components/version.py').read(), main_ns)

setup(
    name='dash_core_components_ppeterson',
    version=main_ns['__version__'],
    author='Philip Peterson',
    author_email='philip.peterson@getcruise.com',
    packages=['dash_core_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI core component suite',
    install_requires=['dash']
)
