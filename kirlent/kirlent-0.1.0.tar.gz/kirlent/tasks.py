# Copyright (C) 2017-2019 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of Kırlent.
#
# Kırlent is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kırlent is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kırlent.  If not, see <http://www.gnu.org/licenses/>.

"""The module that contains the tasks for building output items."""

import copy
import sys
from pathlib import Path
from shutil import rmtree

from doit.cmd_base import TaskLoader
from doit.doit_cmd import DoitMain
from doit.loader import generate_tasks
from doit.tools import create_folder

from .model import ContentHierarchy
from .transform import generate_revealjs_sources


SPHINX_CONFIG = {
    "base": {
        "args": [
            "-b html",
            "-C",
            "-Dsource_suffix=.rv",
            "-Dextensions=%(ext)s",
            "-Dmaster_doc=%(base)s",
        ]
    },
    "math": {"extensions": ["sphinx.ext.mathjax"]},
    "ipython": {
        "extensions": [
            "IPython.sphinxext.ipython_console_highlighting",
            "IPython.sphinxext.ipython_directive",
        ]
    },
    "revealjs": {"extensions": ["kirlent_sphinx"], "args": ["-Dhtml_theme=kirlent"]},
}


# sigalias: TaskDesc = Dict[str, Any]


def task_create_build_folders(unit, folder):
    """Get the description of the build folder creation task.

    :sig: (kirlent.Unit, Path) -> TaskDesc
    :param unit: Unit to create the folders for.
    :param folder: Folder to create.
    :return: Task description.
    """
    return {
        "basename": "create_build_folders",
        "name": unit.slug,
        "actions": [(create_folder, [folder])],
        "uptodate": [folder.exists()],
        "targets": [folder],
    }


def task_clean_build_folders(unit, folder):
    """Get the description of the build folder cleanup task.

    :sig: (kirlent.Unit, Path) -> TaskDesc
    :param unit: Unit to remove the folders for.
    :param folder: Folder to remove.
    :return: Task description.
    """
    return {
        "basename": "clean_build_folders",
        "name": unit.slug,
        "actions": [(rmtree, [folder])],
        "uptodate": [not folder.exists()],
    }


def task_generate_revealjs_sources(unit, sources, output):
    """Get the description of the RevealJS source generation task.

    :sig: (kirlent.Unit, List[Path], Path) -> TaskDesc
    :param unit: Unit to generate the slides sources for.
    :param sources: Source files that make up this presentation.
    :param output: RevealJS file to store the result.
    :return: Task description.
    """
    return {
        "basename": "generate_revealjs_sources",
        "name": unit.slug,
        "actions": [(generate_revealjs_sources, [sources, output])],
        "file_dep": sources,
        "task_dep": ["create_build_folders:" + unit.slug],
        "targets": [output],
    }


def task_generate_revealjs_slides(unit, source, output):
    """Get the description of the RevealJS slides generation task.

    :sig: (kirlent.Unit, Path, Path) -> TaskDesc
    :param unit: Unit to generate the slides for.
    :param source: Source file of presentation.
    :param output: Slides file to store the result.
    :return: Task description.
    """
    sphinx_args = copy.copy(SPHINX_CONFIG.get("base").get("args"))

    extensions = []
    for extra in unit.sphinx_extras() + ["revealjs"]:
        section = SPHINX_CONFIG.get(extra)
        # TODO: check for missing section
        extensions.extend(section.get("extensions", []))
        sphinx_args.extend(section.get("args", []))

    sphinx_args.extend(["%(src)s", "%(out)s", "%(file)s"])

    sphinx_cmd = "sphinx-build " + " ".join(sphinx_args) % {
        "src": source.parent,
        "out": output.parent,
        "file": source,
        "base": source.stem,
        "ext": ",".join(extensions),
    }

    return {
        "basename": "generate_revealjs",
        "name": unit.slug,
        "actions": [sphinx_cmd],
        "file_dep": [source],
        "targets": [output],
    }


def task_generate_decktape_slides(unit, source, output):
    """Get the description of the Decktape slides generation task.

    :sig: (kirlent.Unit, Path, Path) -> TaskDesc
    :param unit: Unit to generate the slides for.
    :param source: Source file of the RevealJS slides.
    :param output: Slides file to store the result.
    :return: Task description.
    """
    decktape_args = ["decktape", "-s", "%(size)s", "file:///%(path)s", "%(file)s"]
    decktape_cmd = " ".join(decktape_args) % {
        "size": "1121x795",
        "path": source.absolute(),
        "file": output,
    }

    return {
        "basename": "generate_decktape",
        "name": unit.slug,
        "actions": [decktape_cmd],
        "file_dep": [source],
        "targets": [output],
    }


class TaskGenerator(TaskLoader):
    """Task loader that generates all Kırlent build tasks."""

    def __init__(self, src, out, *, deps):
        """Initialize this task generator.

        :sig: (Path, Path, Path) -> None
        :param src: Root folder for content sources.
        :param out: Root folder for generated output.
        :param deps: Path of task dependency database for incremental builds.
        """
        super().__init__()

        self.content = ContentHierarchy(src)  # sig: ContentHierarchy
        """Content hierarchy that stores the sources for this generator."""

        self.out = out  # sig: Path
        """Root folder where this generator stores the output it generates."""

        self.doit_config = {"dep_file": str(deps)}  # sig: Dict[str, Any]
        """Settings for doit."""

    def generate_tasks(self):
        """Generate the tasks for the units in this loader's folders.

        :sig: () -> Iterable[TaskDesc]
        :return: Task descriptions.
        """
        for unit in self.content.units.values():
            unit_out = self.out / unit.slug

            yield task_create_build_folders(unit, unit_out)

            yield task_clean_build_folders(unit, unit_out)

            lang = "en"

            slide_src = list(unit.sources(medium="slides", lang=lang))
            rv_src = Path(unit_out, f"slides.{lang}.rv")
            yield task_generate_revealjs_sources(unit, slide_src, rv_src)

            rv_out = Path(unit_out, "revealjs", rv_src.with_suffix(".html").name)
            yield task_generate_revealjs_slides(unit, rv_src, rv_out)

            dt_out = Path(unit_out, rv_out.with_suffix(".pdf").name)
            yield task_generate_decktape_slides(unit, rv_out, dt_out)

    def load_tasks(self, cmd, params, args):
        """Provide the task data."""
        return generate_tasks("kirlent", self.generate_tasks()), self.doit_config


class TaskManager:
    """A manager for controlling tasks."""

    def __init__(self, src, out, *, deps=None):
        """Initiliaze this task manager.

        :sig: (Path, Path, Path) -> None
        :param src: Root folder for the content sources.
        :param out: Root folder for generated output.
        :param deps: Path of task dependency database for incremental builds.
        """
        self.loader = TaskGenerator(src, out, deps=deps)  # sig: TaskGenerator
        """Loader for generating the tasks."""

        self.runner = None  # sig: Optional[DoitMain]
        """Runner that will process the tasks."""

    def run(self, task, *, pattern=None, exits=False):
        """Start a task.

        :sig: (str, Optional[str], Optional[bool]) -> int
        :param task: Name of task.
        :param pattern: Pattern for units to process.
        :param exits: Whether to exit after running the task.
        :return: Exit code of the task.
        """
        if self.runner is None:
            self.runner = DoitMain(self.loader)

        pattern_ = Path(pattern).name if pattern is not None else None
        task_ = f"{task}:{pattern_}" if pattern_ is not None else task
        exit_code = self.runner.run(["run", task_])
        if exits:
            sys.exit(exit_code)
        return exit_code
