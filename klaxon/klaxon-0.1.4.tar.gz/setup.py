# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['klaxon']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['klaxon = klaxon:main']}

setup_kwargs = {
    'name': 'klaxon',
    'version': '0.1.4',
    'description': 'Use osascript to send notifications.',
    'long_description': '# klaxon\n\nSend Mac OS notifications from the terminal or Python programs.\n\nThis is useful for when you want a push notification \nfor some long-running background task.\n\nThis is similar to the [terminal-notifier ruby gem][terminal-notifier],\nbut posix-compliant and with fewer features (PR\'s welcome).\n\n## Security Notice\n\n\n**DO NOT** send untrusted input to through klaxon. \n\nSomeone could use a shell escape sequence to execute arbitrary code\non your machine as klaxon functions by invoking [osascript]\nvia a subprocess call.\n\nYou have been warned.\n\n## Usage\n\n### terminal\n\n```bash\n# blank notification\nklaxon\n# with custom message\nklaxon --message "this is the message body"\n# pipe message from other program\necho "this is the message body" | klaxon --\n```\n\n### python\n\n```python\nfrom klaxon import klaxon, klaxonify\n\n# send a blank notification\n\nklaxon()\n\n# we can decorate our functions to have\n# them send notifications at termination\n\n@klaxonify\ndef hello(name=\'world\'):\n    return f\'hello, {name}\'\n\n@klaxonify(title=\'oh hai\', output_as_message=True)\ndef foo():\n    return "This will be the message body."\n\n```\n\n## Installation\nFor command-line use, the recommended method of installation is through [pipx].\n```bash\npipx install klaxon\n```\nNaturally, klaxon can also be pip-installed.\n```bash\npip install klaxon\n```\n\n[terminal-notifier]: https://github.com/julienXX/terminal-notifier\n[pipx]: https://github.com/pipxproject/pipx\n[osascript]: https://apple.stackexchange.com/questions/57412/how-can-i-trigger-a-notification-center-notification-from-an-applescript-or-shel/115373#115373\n',
    'author': 'Stephan Fitzpatrick',
    'author_email': 'knowsuchagency@gmail.com',
    'url': 'https://pypi.org/project/klaxon/',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
