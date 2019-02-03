# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['silverbullet']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.16,<2.0', 'pybullet>=2.4,<3.0']

setup_kwargs = {
    'name': 'silverbullet',
    'version': '0.3.0',
    'description': 'shallow but powerful wrapper around pybullet',
    'long_description': '# silverbullet\n\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c9b3d97530be4717bd5dc3c4409bc545)](https://app.codacy.com/app/coord-e/silverbullet?utm_source=github.com&utm_medium=referral&utm_content=MonoMotion/silverbullet&utm_campaign=Badge_Grade_Dashboard)\n[![Travis CI](https://img.shields.io/travis/MonoMotion/silverbullet.svg?style=flat-square)](https://travis-ci.org/MonoMotion/silverbullet)\n[![pypi](https://img.shields.io/pypi/v/silverbullet.svg)](https://pypi.org/project/silverbullet/)\n[![Reviewed by Hound](https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg?style=flat-square)](https://houndci.com)\n[![license](https://img.shields.io/github/license/MonoMotion/silverbullet.svg?style=flat-square)](LICENSE)\n[![GitHub release](https://img.shields.io/github/release/MonoMotion/silverbullet.svg?style=flat-square)](https://github.com/MonoMotion/silverbullet/releases)\n\nshallow but powerful wrapper around pybullet\n\n## Installation\n\n```shell\npip install silverbullet\n```\n\n## Usage\n\n```python\nfrom silverbullet import Scene, Robot\n\n# GUI mode\n# from silverbullet import Connection, Mode\n# conn = Connection(mode=Mode.GUI)\n# scene = Scene(timestep=0.01, frame_skip=4, connection=conn)\n\nscene = Scene(timestep=0.01, frame_skip=4)\nrobot = Robot.load_urdf(scene, "robot.urdf")\nrobot.bring_on_the_ground()\n\nwhile True:\n\n  # You can control and observe the robot\n  # e.g. robot.set_joint_torque(\'joint1\', 1)\n\n  do_something(robot)\n\n  # This will step simulation\n  scene.step()\n```\n',
    'author': 'coord.e',
    'author_email': 'me@coord-e.com',
    'url': 'https://github.com/MonoMotion/silverbullet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
