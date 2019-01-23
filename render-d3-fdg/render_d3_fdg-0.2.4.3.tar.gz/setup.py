from distutils.core import setup

# Read the version number
with open("render_d3_fdg/_version.py") as f:
    exec(f.read())

setup(
    name='render_d3_fdg',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['render_d3_fdg'],
    scripts=[],
    url='http://pypi.python.org/pypi/render_d3_fdg/',
    license='LICENSE.txt',
    description='Render d3 force directed graphs from python',
    long_description=open('README.md').read(),
    install_requires=[
                      
                     ],
    data_files=[('render_d3_fdg', [
            'fdg_base_no_search.html.template',
            'fdg_base_orig.html.template',
            'fdg_base_simplest.html.template',
            'fdg_base.html.template',
            'graph_setup.js.template',
            'helper_functions.js.template',
            'search_setup.js.template',
            'slider_setup.js.template',
        ]
    )]
)
