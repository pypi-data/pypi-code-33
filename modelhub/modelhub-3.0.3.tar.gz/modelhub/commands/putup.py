# -*- coding: utf-8 -*-
from modelhub.core.models import Model, ModelVersion   # noqa
from modelhub.core import conf
from .base import BaseCommand, argument, option, types, register   # noqa
# import os
import pathlib
from jinja2 import Template


SETUP_PY_TEMPLATE = """
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

try:
    README = open('README.md').read()
except Exception:
    README = ""
VERSION = "0.0.1"

requirments = ["modelhub"{%if tf%}, "tensorflow"{%endif%}]

setup(
    name='{{project_name}}',
    version=VERSION,
    description='{{project_name}}',
    url="http://git.patsnap.com/research/{{project_name}}",
    long_description=README,
    author='{{conf.USER_NAME}}',
    author_email='{{conf.USER_EMAIL}}',
    packages=find_packages(),
    install_requires=requirments,
    extras_require={
        # "extra": ["extra_requirments"],
    },
    entry_points={
        # 'console_scripts': [
        #     'modelhub=modelhub.commands:main'
        # ]
    },
)

"""

GITIGNORE_TEMPLATE = """
# Created by .ignore support plugin (hsz.mobi)

### OSX template
*.DS_Store
.AppleDouble
.LSOverride

# Icon must end with two \r
Icon

# Thumbnails
._*

# Files that might appear in the root of a volume
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Directories potentially created on remote AFP share
.AppleDB
.AppleDesktop
Network Trash Folder
Temporary Items
.apdisk

### C++ template
# Compiled Object files
*.slo
*.lo
*.o
*.obj

# Precompiled Headers
*.gch
*.pch

# Compiled Dynamic libraries
*.so
*.dylib
*.dll

# Fortran module files
*.mod
*.smod

# Compiled Static libraries
*.lai
*.la
*.a
*.lib

# Executables
*.exe
*.out
*.app

### IPythonNotebook template
# Temporary data
.ipynb_checkpoints/

### Example user template

# IntelliJ project files
.idea
*.iml
out
gen### Python template
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions

# Distribution / packaging
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*,cover
.hypothesis/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# IPython Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# dotenv
.env

# virtualenv
venv/
ENV/

# Spyder project settings
.spyderproject

# Rope project settings
.ropeproject

### JetBrains template
# Covers JetBrains IDEs: IntelliJ, RubyMine, PhpStorm, AppCode, PyCharm, CLion, Android Studio and Webstorm
# Reference: https://intellij-support.jetbrains.com/hc/en-us/articles/206544839

# User-specific stuff:
.idea/workspace.xml
.idea/tasks.xml
.idea/dictionaries
.idea/vcs.xml
.idea/jsLibraryMappings.xml
build-*/

# Sensitive or high-churn files:
.idea/dataSources.ids
.idea/dataSources.xml
.idea/dataSources.local.xml
.idea/sqlDataSources.xml
.idea/dynamic.xml
.idea/uiDesigner.xml

# Gradle:
.idea/gradle.xml
.idea/libraries

# Mongo Explorer plugin:
.idea/mongoSettings.xml

## File-based project format:
*.iws

## Plugin-specific files:

# IntelliJ
/out/

# mpeltonen/sbt-idea plugin
.idea_modules/

# JIRA plugin
atlassian-ide-plugin.xml

# Crashlytics plugin (for Android Studio and IntelliJ)
com_crashlytics_export_strings.xml
crashlytics.properties
crashlytics-build.properties
fabric.properties


*.ipynb
test/samples/

.vscode/
"""

README_MD_TEMPLATE = """
# {{project_name}}

## Introduction
Project owner: {{conf.USER_NAME}} <{{conf.USER_EMAIL}}>

## Installation

```bash
pip install {{project_name}}
```

## Usage

```python
from {{project_name}}.api_model import Model
model=Model()
model.run()
```
"""


INIT_PY_TEMPLATE = """
# -*- coding: utf-8 -*-
import pkg_resources
__version__ = pkg_resources.get_distribution("{{project_name}}").version
"""

API_MODEL_TEMPLATE = """
# -*- coding: utf-8 -*-
from modelhub.framework import ApiModel


class Model(ApiModel):
    model_name = "{{project_name}}"

    INPUTS_SAMPLE = None
    OUTPUTS_SAMPLE = None

    def prepare(self):
        super().prepare()
        # do prepare

    def is_ready(self):
        # check is ready

    def validate_input_data(self, raw_input):
        # do validation
        pass
        return True

    def run_model(self, preprocessed_data):
        # do run
        pass


if __name__=="__main__":
    model = Model()
    output = model.run(model.INPUTS_SAMPLE)
    print(output)

"""

TF_API_MODEL_TEMPLATE = """
# -*- coding: utf-8 -*-
from modelhub.framework import TFApiModel


class Model(TFApiModel):
    model_name = "{{project_name}}"
    # local_model_version = 1 # specify this when you need use certain version model

    INPUTS_SAMPLE = None
    OUTPUTS_SAMPLE = None

    def preprocess(raw_input):
        # do preprocess here
        return super().preprocess(raw_input)

    def postprocess(self, tf_output, raw_input, preprocessed_item):
        return super().postprocess(self, tf_output, raw_input, preprocessed_item)


if __name__=="__main__":
    model = Model()
    output = model.run(model.INPUTS_SAMPLE)
    print(output)

"""


@register("putup")
class Command(BaseCommand):
    arguments = [
        argument("project_name"),
        option("-tf", help="Is TensorFlow based model", is_flag=True)
    ]

    def run(self, project_name, tf=False):
        """create new api model project layout"""
        root = pathlib.Path(project_name)
        if root.exists():
            self.echo("Error: {} is existed.".format(root))
            return
        root.mkdir()

        self._create_file(root / "setup.py", SETUP_PY_TEMPLATE, project_name=project_name, conf=conf, tf=tf)
        self._create_file(root / ".gitignore", GITIGNORE_TEMPLATE, project_name=project_name, conf=conf, tf=tf)
        self._create_file(root / "README.md", README_MD_TEMPLATE, project_name=project_name, conf=conf, tf=tf)
        src_dir = root / project_name
        src_dir.mkdir()
        self._create_file(src_dir / "__init__.py", INIT_PY_TEMPLATE, project_name=project_name, conf=conf, tf=tf)
        self._create_file(src_dir / "api_model.py", TF_API_MODEL_TEMPLATE if tf else API_MODEL_TEMPLATE, project_name=project_name, conf=conf, tf=tf)

    def _create_file(self, path, template, **content):
        with path.open("w") as f:
            f.write(Template(template).render(**content).strip())
