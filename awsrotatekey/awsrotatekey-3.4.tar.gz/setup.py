
from setuptools import setup

setup(
  name = 'awsrotatekey',         # How you named your package folder (MyLib)
  packages = ['awsrotatekey'],   # Chose the same as "name"
  version = '3.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Rotate AWS keys for any user.', # Give a short description about your library
  longdescription = 'As a security best practice, AWS recommends that users periodically regenerate their AWS access keys. This tool simplifies the rotation of access keys for any user. Before running, create text files and list the user names that have to be blacklisted and whitelisted respectively.',
  author = 'Kanishk Saxena',                   # Type in your name
  author_email = 'kanishk.saxena@cred.club',      # Type in your E-Mail
  scripts=['awsrotatekey/awsrotatekeystart'],
  #url = 'https://github.com/saxenakanishk/Intern-Kanishk',   # Provide either the link to your github or to your website
  #download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    # I explain this later on
  keywords = ['AWS', 'Rotate', 'Keys'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'datetime'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',      #Specify which pyhton versions that you want to support
  ],
)