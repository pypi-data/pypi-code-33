from distutils.core import setup
from io import open


with open("README",
          "r",
          encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="PyRQA",
    packages=[
        "pyrqa",
        "pyrqa.operators",
        "pyrqa.operators.create_matrix",
        "pyrqa.operators.create_matrix.fixed_radius",
        "pyrqa.operators.detect_diagonal_lines",
        "pyrqa.operators.detect_diagonal_lines.fixed_radius",
        "pyrqa.operators.detect_vertical_lines",
        "pyrqa.operators.detect_vertical_lines.fixed_radius",
        "pyrqa.variants",
        "pyrqa.variants.recurrence_plot",
        "pyrqa.variants.recurrence_plot.fixed_radius",
        "pyrqa.variants.rqa",
        "pyrqa.variants.rqa.fixed_radius",
    ],
    package_data={
        "pyrqa": [
            "config.ini",
            "kernels/clear_buffer/*.cl",
            "kernels/create_matrix/fixed_radius/euclidean_metric/*.cl.mako",
            "kernels/create_matrix/fixed_radius/maximum_metric/*.cl.mako",
            "kernels/create_matrix/fixed_radius/taxicab_metric/*.cl.mako",
            "kernels/detect_diagonal_lines/*.cl.mako",
            "kernels/detect_diagonal_lines/fixed_radius/euclidean_metric/*.cl.mako",
            "kernels/detect_diagonal_lines/fixed_radius/maximum_metric/*.cl.mako",
            "kernels/detect_diagonal_lines/fixed_radius/taxicab_metric/*.cl.mako",
            "kernels/detect_vertical_lines/*.cl.mako",
            "kernels/detect_vertical_lines/fixed_radius/euclidean_metric/*.cl.mako",
            "kernels/detect_vertical_lines/fixed_radius/maximum_metric/*.cl.mako",
            "kernels/detect_vertical_lines/fixed_radius/taxicab_metric/*.cl.mako",
        ],
    },
    version="2.0.1",
    description="A tool to conduct recurrence quantification analysis and to create recurrence plots in a massively parallel manner using the OpenCL framework.",
    long_description=long_description,
    author="Tobias Rawald",
    author_email="pyrqa@gmx.net",
    keywords=[
        "time series analysis", 
        "recurrence quantification analysis", 
        "RQA", 
        "recurrence plot"
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    install_requires=[
        'Mako',
        'numpy', 
        'Pillow', 
        'pyopencl', 
        'scipy'
    ],
)