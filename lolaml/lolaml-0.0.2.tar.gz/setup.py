# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['lolaml', 'lolaml.tests']

package_data = \
{'': ['*'], 'lolaml': ['templates/*']}

install_requires = \
['altair>=2.3,<3.0',
 'click>=6.0,<7.0',
 'cloudstorage>=0.9.0,<0.10.0',
 'dataclasses>=0.6.0,<0.7.0',
 'filelock>=3.0,<4.0',
 'flask>=1.0,<2.0',
 'google-cloud-storage>=1.14,<2.0',
 'minilog>=0.4,<0.5',
 'numpy',
 'pandas>=0.24.1,<0.25.0',
 'tomlkit>=0.5.3,<0.6.0',
 'xattr>=0.9.6,<0.10.0']

setup_kwargs = {
    'name': 'lolaml',
    'version': '0.0.2',
    'description': 'TODO description',
    'long_description': '``LolaML`` - track your ML experiments\n======================================\n\n.. image:: https://readthedocs.org/projects/lolaml/badge/?version=latest\n   :target: https://lolaml.readthedocs.io/en/latest/?badge=latest\n   :alt: Documentation Status\n\n.. image:: https://gitlab.com/stefan-otte/lolaml/badges/master/pipeline.svg\n   :target: https://gitlab.com/stefan-otte/lolaml/commits/master\n   :alt: Pipeline Status\n\n.. image:: https://gitlab.com/stefan-otte/lolaml/badges/master/coverage.svg\n   :target: https://gitlab.com/stefan-otte/lolaml/commits/master\n   :alt: Coverage Report\n\n.. image:: https://img.shields.io/pypi/v/lolaml.svg\n   :target: https://pypi.org/project/lolaml\n   :alt: PyPI Version\n\n.. [![Windows Build Status](https://img.shields.io/appveyor/ci/sotte/lolaml/master.svg?label=window)](https://ci.appveyor.com/project/sotte/lolaml)\n.. [![Scrutinizer Code Quality](https://img.shields.io/scrutinizer/g/sotte/lolaml.svg)](https://scrutinizer-ci.com/g/sotte/lolaml/?branch=master)\n\nTHIS IS AN ALPHA. DON\'T USE IT!\n\nTrack your machine learning experiments with LolaML,\nnever lose any information or forget which parameter yielded which results.\nLola creates a simple JSON representation of the run that contains all the\ninformation you logged.\nThe JSON can easily be shared to collaborate with friends and colleagues.\nLola strives to be non-magic and simple but configurable.\n\n**Features:**\n\n- a simple logging interface\n- a simple representation of the logged data\n- works with any machine learning library\n- automatically creates an artifact folder for each run\n- automatically uploads artifacts to a remote bucket (if you want)\n- simple jupyter notebook dashboard (more to come...)\n\n::\n\n    import lolaml as lola\n\n    # Use the run context manager to start/end a run\n    with lola.Run(project="mnist", prefix_path="data/experiments") as run:\n        # a unique id for the run\n        print(run.run_id)\n        # store all artifacts (model files, images, etc.) here\n        print(run.path)  # -> data/experiments/<run_id>\n\n        run.log_param("lr", 0.1)\n        run.log_param("epochs", 10)\n\n        run.log_tags("WIP", "RNN")\n\n        # Create and train your model...\n\n        run.log_metric("loss", loss, step=1)\n        run.log_metric("train_acc", train_acc, step=1)\n        run.log_metric("val_acc", val_acc, step=1)\n\n        model.save(os.path.join(run.path, "model.pkl"))\n\n    # After a run there is a lola_run*.json file under run.path.\n    # It contails all the information you logged.\n\nAfter the run there is a JSON file that looks something like this::\n\n    {\n        "project": "mnist",\n        "run_id": "9a531da0-dc43-4dcc-8968-77fd480ff7ee",\n        "status": "done",\n        "path": "data/experiments/9a531da0-dc43-4dcc-8968-77fd480ff7ee",\n        "user": "stefan",\n        "start_time": "2019-02-16 12:49:32.782958",\n        "end_time": "2019-02-16 12:49:32.814529",\n        "metrics": [\n            {\n                "name": "loss",\n                "value": 1.5\n                "step": 1,\n                "ts": "2019-02-16 12:49:32.813750"\n            },\n            ...\n        ],\n        "params": {\n            "lr": "0.1",\n            "epochs": 10,\n        },\n        "tags": ["WIP", "RNN"],\n        "artifacts": {\n            "data/experiments/9a531da0-dc43-4dcc-8968-77fd480ff7ee/lola_run_9a531da0-dc43-4dcc-8968-77fd480ff7ee.json": {},\n            ...\n        },\n        "git": {\n            "sha": "41cb4fb11b7e937c602c2282b9275200c88b8797",\n            "status": "...",\n            "diff": "...",\n        },\n        "call_info": {\n            "__file__": "somefile.py",\n            "argv": [],\n        }\n    }\n\n\nLola can automatically upload all artifacts to a remote storage bucket for you::\n\n  with lola.run(\n      remote_location="gs://somewhere",\n      remote_credentials="service_account.json",\n  ) as run:\n      # train and log ...\n\n  # All artifacts are uploaded now\n\n\nThe remote location can also be configured with the `.lola.toml` file.\n\nAdditionally, Lola offers some helpers to analyse the your experiments:\n\nTODO add image of dashboard\n\nSetup\n=====\n\nRequirements\n------------\n\n* Python 3.6+ (probably works with other versions as well, but must be tested)\n\nInstallation\n------------\n\nInstall this library directly into an activated virtual environment::\n\n    $ pip install lolaml\n\nor add it to your `Poetry <https://poetry.eustace.io/>`_ project::\n\n    $ poetry add lolaml\n\nMisc\n====\n\nThis project was generated with `cookiecutter <https://github.com/audreyr/cookiecutter>`_\nusing `jacebrowning/template-python <https://github.com/jacebrowning/template-python>`_.\nThanks!\n',
    'author': 'Stefan Otte',
    'author_email': 'stefan.otte@gmail.com',
    'url': 'https://pypi.org/project/lolaml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
