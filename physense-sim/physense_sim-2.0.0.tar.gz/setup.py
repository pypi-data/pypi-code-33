# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path



here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='physense_sim',  # Required
    version='2.0.0',  # Required
    description='A simulator for itn160',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/primeteacher/physense_sim',  # Optional
    author='Jason Silverstein',  # Optional
    author_email='jsilver5@dtcc.edu',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],

    keywords='itn160',  # Optional

    packages=find_packages(),  # Required

    install_requires=['guizero', 'pygame'],  # Optional

    package_data={  # Optional
        'physense_sim': ['rLedOn.png','rLedOff.png',
					'yLedOn.png','yLedOff.png',
					'gLedOn.png','gLedOff.png',
					'bLedOn.png','bLedOff.png',
					'sun.png', 'moon.png',
					'speaker.png',
					'buzzer.wav'],
    },

  


entry_points={  # Optional
        'console_scripts': [
            'physense_sim=physense_sim:main',
        ],
    },	# Optional

)
