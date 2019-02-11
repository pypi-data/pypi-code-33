import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(name="transformer_keras",
      version="0.1",
      description="transformer_keras encoder implemented with keras",
      author="MrWaterZhou",
      author_email='zhou_wuxialang@qq.com',
      py_modules=['transformer_keras.layers','transformer_keras.model'],
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      )
