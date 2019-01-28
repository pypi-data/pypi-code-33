# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.typedefinitions import (AnonymousProjectData, SaveProjectFromDataMessageArguments,
                                        AnonymousActivityData, AnonymousBlockData)
from .engineapi.api import EngineAPI, get_engine_api
from .dataflow import Dataflow, Step
from copy import copy
from pathlib import Path
from textwrap import dedent, indent
from typing import List, TypeVar
import os

PackageArgs = TypeVar('PackageArgs', Dataflow, List[Dataflow])


class Package:
    """
    A Package encapsulates one or more Dataflows.

    .. remarks::

        Packages can be saved to a file and opened again via the DataPrep API or 'Project Pendleton'.
    """
    def __init__(self, arg: PackageArgs):
        """
        Package constructor which ensures all given Dataflows have mutually unique names.

        :param arg: Single Dataflow or List[Dataflow] to construct Package with.
        """
        self._engine_api = get_engine_api()
        self._dataflows = arg if isinstance(arg, List) else [arg]
        self._path = None
        names = [df.name for df in self._dataflows]
        if len(names) > len(set(names)):
            raise NameError('Two or more Dataflows have the same name,'
                            'please ensure all supplied Dataflows are uniquely named.')
        for name in names:
            if not name:
                raise NameError('Dataflow must have a name in order to save. '
                                'Please call the set_name method on dataflow to set a name.')

        self._project_data = None
        self._name = None

    def __getitem__(self, key) -> Dataflow:
        if not isinstance(key, str):
            raise KeyError('Packages only support string keys.')
        for df in self._dataflows:
            if df.name == key:
                return df
        raise KeyError(key)

    def __repr__(self):
        result = dedent("""\
        Package
          name: {_name}
          path: {_path}
          dataflows: [\n""".format(**vars(self)))
        result += ''.join(
            indent(
                dedent("""\
                    Dataflow {{
                      name: {name}
                      steps: {numSteps}
                    }},\n""".format(**{'name': dflow.name, 'numSteps': len(dflow._steps)})),
                '  ' * 2)
            for dflow in self._dataflows)
        result += '  ]'
        return result

    @staticmethod
    def open(file_path: str) -> 'Package':
        """
        Open Package at 'file_path'.

        :param file_path: Filesystem path to Package File (.dprep).
        :return: New Package object constructed from file.
        """
        engine_api = get_engine_api()
        file_path = os.path.abspath(os.path.expanduser(file_path))
        project_data = engine_api.get_project(file_path)
        return package_from_project_data(project_data, file_path)

    @staticmethod
    def from_json(package_json: str) -> 'Package':
        """
        Load package from 'package_json'.

        :param package_json: JSON string representation of the Package.
        :return: New Package object constructed from the JSON string.
        """
        engine_api = get_engine_api()
        project_data = engine_api.load_project_from_json(package_json)
        return package_from_project_data(project_data, '')

    def save(self, file_path: str, overwrite: bool=True) -> 'Package':
        """
        Save Package to 'file_path', raise on failure.

        :param file_path: Filesystem path to save Package to.
        :param overwrite: Indicates whether or not file at 'file_path' should be overwritten if it exists.
        """

        # We use os.path.abspath instead of Path.resolve because Path.resolve('./asd') returns 'asd' instead of
        # resolving the relative component correctly.
        file_path = os.path.abspath(os.path.expanduser(file_path))
        if Path(file_path).is_file() and not overwrite:
            raise FileExistsError('Path to save Package to already exists and overwrite was set False.')
        self._engine_api.save_project_from_data(
            SaveProjectFromDataMessageArguments(file_path, package_to_anonymous_project_data(self)))

        def update_dataflow(df: Dataflow) -> Dataflow:
            new_df = copy(df)
            new_df._parent_package_path = file_path
            return new_df

        updated_dataflows = [update_dataflow(df) for df in self._dataflows]
        new_pkg = copy(self)
        new_pkg._dataflows = updated_dataflows
        new_pkg._path = file_path
        return new_pkg

    def to_json(self) -> str:
        """
        Get the JSON string representation of the Package.
        """
        return self._engine_api.save_project_to_json(package_to_anonymous_project_data(self))

    def add_dataflow(self, new_df: Dataflow) -> 'Package':
        """
        Return clone of current Package with 'new_df' added.

        .. remarks::

            Packages, like Dataflows, are immutable so a new Package is created cloned from the current one.
            Similar to the Package constructor Dataflow names are checked to ensure mutual uniqueness.

        :param new_df: Dataflow to add to current Package.
        :return: New Package containing current Dataflows and 'new_df'.
        """
        if any(df.name == new_df.name for df in self._dataflows):
            raise NameError('Two or more Dataflows have the same name,'
                            'please ensure all supplied Dataflows are uniquely named.')
        cloned_pkg = copy(self)
        new_df = copy(new_df)
        new_df._parent_package_path = self._path
        cloned_pkg._dataflows = cloned_pkg._dataflows + [new_df]
        return cloned_pkg

    def delete_dataflow(self, name: str) -> 'Package':
        """
        Return clone of current Package with Dataflow named 'name' removed.

        .. remarks::

            If no Dataflow with 'name' is found then returned Dataflow will be an identical clone.

        :param name: Name of Dataflow to remove from Package.
        :return: New Package containing altered list of Dataflows.
        """
        cloned_pkg = copy(self)
        cloned_pkg._dataflows = list(filter(lambda df: df.name != name, cloned_pkg.dataflows))
        return cloned_pkg

    @property
    def dataflows(self) -> List[Dataflow]:
        """
        The Dataflows contained in this package.

        :return: Cloned list of Dataflows in this Package.
        """
        return self._dataflows[:]

    @property
    def name(self) -> str:
        """
        Name of Package, either manually set or auto-generated upon save.
        """
        return self._name

    def rename(self, new_name: str) -> 'Package':
        """
        Change name of Package. Returns new Package with changed name.

        :param new_name: New name for Package.
        :return: New Package with changed name.
        """
        cloned_pkg = copy(self)
        cloned_pkg._name = new_name
        return cloned_pkg


def package_from_project_data(project_data: AnonymousProjectData, path: str) -> Package:
    dataflows = [dataflow_from_activity_data(ad,
                                             path,
                                             get_engine_api()) for ad in project_data.activities]
    pkg = Package(dataflows)
    pkg._path = path
    pkg._project_data = project_data
    return pkg


def package_to_anonymous_project_data(package: Package) -> AnonymousProjectData:
    return AnonymousProjectData([dataflow_to_anonymous_activity_data(df) for df in package.dataflows])


def dataflow_from_activity_data(activity_data: AnonymousActivityData,
                                parent_package_path: str,
                                engine_api: EngineAPI) -> Dataflow:
    steps = [step_from_block_data(bd) for bd in activity_data.blocks]
    df = Dataflow(engine_api,
                  steps,
                  activity_data.name,
                  activity_data.id,
                  parent_package_path=parent_package_path)
    df._activity_data = activity_data
    return df


def dataflow_to_anonymous_activity_data(dataflow: Dataflow) -> AnonymousActivityData:
    return AnonymousActivityData(
        [AnonymousBlockData(step.arguments, step.id, step.local_data, step.step_type) for step in dataflow._get_steps()],
        dataflow.id,
        dataflow.name
    )


def step_from_block_data(block_data: AnonymousBlockData):
    step = Step(block_data.type, block_data.arguments.to_pod(), block_data.local_data.to_pod())
    step.id = block_data.id
    step._block_data = block_data
    return step
