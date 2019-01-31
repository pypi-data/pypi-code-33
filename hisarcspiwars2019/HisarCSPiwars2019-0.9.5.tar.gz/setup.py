from setuptools import setup

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(
      name = "HisarCSPiwars2019",
      version = "0.9.5",
      author = "Yaşar İdikut, Sarp Yoel Kastro",
      author_email = "yasar.idikut@hisarschool.k12.tr, sarp.kastro@hisarschool.k12.tr",
      description = "Library that makes use of sensors, motors, and servos made for the  PiWars competition by HisarCS",
      packages = ["HisarCSPiWars2019"],
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
                   "Development Status :: 4 - Beta",
                   ]


)
