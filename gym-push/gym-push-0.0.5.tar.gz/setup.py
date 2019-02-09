from setuptools import setup, find_packages

setup(name='gym-push',
      packages=find_packages(),
      version='0.0.5',
      install_requires=['gym', 'numpy', 'pandas'],  # And any other dependencies foo needs,
      author='Kieran Fraser',
      author_email='kfraser@tcd.ie',
      download_url='https://github.com/kieranfraser/gym-push/archive/0.0.5.tar.gz'
) 