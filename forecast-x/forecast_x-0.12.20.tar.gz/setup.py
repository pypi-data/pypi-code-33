
import setuptools

with open("C:/Users/DeBarros/Documents/Python Scripts/forecast_x/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="forecast_x",
    version="0.12.20",
    author="Alejandro De Barros",
    author_email="alejandrodbn@gmail.com",
    description="Forecasting Model package based on naive models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alejandrodbn/forecast",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)