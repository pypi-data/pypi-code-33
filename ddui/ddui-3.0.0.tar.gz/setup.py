from setuptools import setup


with open("ci/test_requirements.txt") as f:
    test_reqs = [l for l in f.readlines()]

setup(
    long_description=open("README.md").read(),

    # to make installation easy for developers : pip install .[test]
    extras_require={
        "test": test_reqs
    },

    py_modules = "link_plugin_to_airflow",
    entry_points='''
        [airflow.plugins]
        ddui = ddui.plugin:DataDriverUIPlugin
        [console_scripts]
        ddui=link_plugin_to_airflow:cli
    ''',
)