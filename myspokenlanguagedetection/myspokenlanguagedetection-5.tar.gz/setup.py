from setuptools import setup

long_description="""*** Version-5 release with accuracy improvement *** 
This program may take a minute or so to get results showed on the screen,
please be patient.

Spoken Language Identification is the process of determining and classifying natural language 
from a given content and dataset. Employing an acoustic model and a language model, Data of 
audio files is processed to extract useful features for performing Machine Learning. 
The acoustic features for SPOKEN LANGUAGE IDENTIFICATION are namely standard features such 
as Mel-Frequency Cepstral Coefficients (MFCC), Shifted Delta Cepstral (SDC), while for the 
language features the Gaussian Mixture Model (GMM) and the i-vector based framework are 
used. 

However, the Machine Learning process based on extract features remains a challenge. 
Optimisation needs to be improved in order to capture embedded knowledge on the extracted 
features. CNN (Convolutional Neural Networks), RNN (Recurrent Neural Networks) and ELM (the 
Extreme Learning Machine) are promising as effective learning architectures used to perform 
classification and further complex analysis and are extremely useful to train a single 
hidden layer neural network. However, by now, the learning process of these models is not 
entirely effective due to the selection methods of weights within the input hidden layer.

myspokenlanguagedetection is a preliminary package structured for SPOKEN LANGUAGE 
IDENTIFICATION based on standard feature extraction
and CNN and RNN. An optimisation approach was employed as the benchmark and improved by 
altering the selection phase of the optimisation process. The selection process is performed
incorporating deferent methods. The results are generated based on SPOKEN LANGUAGE 
IDENTIFICATION with the datasets created from eighteen different languages. The results of 
the study indicate the performance of Machine Learning highly correlated with the soundness 
of architecture of Neural Networks and co-existence of acoustic and language models.

THIS version of myspokenlanguagedetection was trained to detect "French", "English", "Spanish", 
"Italian", "Deutsch", "Russian", "Portuguese", "Swedish", and "Japanese" and to some lower 
extent other 40 languages. We will complete the machine training sessions for more languages 
along with increasing the accuracy of the languages identification process.

=============
Installation
=============
myspokenlanguagedetection can be installed like any other Python library, using (a recent version of) the
Python package manager pip, on Linux, macOS, and Windows:

------------------pip install myspokenlanguagedetection
				
or, to update your installed version to the latest release:
------------------- pip install -u myspokenlanguagedetection 	---------------------------------

Recording files must be 25 sec. or longer of audio and in *.wav PCM/LPCM format, recorded at 48 kHz 
sample frame and 24-32 bits of resolution or AIFF, AIFF-C, FLAC: must be native FLAC format; 
OGG-FLAC is not supported.

please check out https://github.com/Shahabks/myspokenlanguageid    

myspokenlanguagedetection was developed by MYOLUTION Lab in Japan. It is part of New Generation of 
Voice Recognition and Acoustic & Language modeling Project in MYSOLUTION Lab. That is planned to 
enrich the functionality of myspokenlanguagedetection by adding more advanced functions."""
	
	
setup(name='myspokenlanguagedetection',
      version='5',
      description='Spoken language identification with CNN and RNN - Improved Version: accuracy up',
	  long_description=long_description,
	  url='https://github.com/Shahabks/myspokenlanguageid',
      author='Shahab Sabahi',
      author_email='sabahi.s@mysol-gc.jp',
      license='MIT',
      classifiers=[
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.7',
		],
	  keywords='speech signal processing , Natural Language Processing and Understanding',
	  install_requires=[
		'numpy>=1.15.2',
		'SpeechRecognition>=3.8.1',
		'langdetect>=1.0.7',
		'pickleshare>=0.7.5',
		'nagisa>=0.2.0',
		],
	  packages=['my_spoken_language_detection'],
      zip_safe=False)
	  
