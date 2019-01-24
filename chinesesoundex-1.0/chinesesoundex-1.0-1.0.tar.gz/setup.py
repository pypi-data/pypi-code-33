from setuptools import setup

setup(name="chinesesoundex-1.0",
	version="1.0",
	description="Chinese soundex: a phonetic similarity algorithm for Chinese. (Python version)",
	long_description="Chinese soundex: a phonetic similarity algorithm for Chinese. (Python version)",
	author="Kun Qian",
	author_email="qian.kun@ibm.com",
	packages=['dimsim'],
	package_data={"":['pinyin_to_simplified.pickle','pinyin_to_traditional.pickle']},
	include_package_data=True,
	classifiers=[
		'License :: OSI Approved :: Apache Software License'
	]
)

