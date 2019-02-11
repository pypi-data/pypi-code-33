# Copyright (c) Microsoft Corporation. All rights reserved.
from .engineapi.api import get_engine_api
from .engineapi.typedefinitions import (ResolveReferenceMessageArguments, ActivityReference,
                                        CreateAnonymousReferenceMessageArguments)
from .step import steps_to_block_datas
from ... import dataprep


def _to_anonymous_reference(df: 'dataprep.Dataflow') -> ActivityReference:
    blocks = steps_to_block_datas(df._steps)
    return get_engine_api().create_anonymous_reference(
        CreateAnonymousReferenceMessageArguments(blocks, df._parent_package_path))


class ExternalReference:
    """
    Class that allows reuse of Dataflows saved in other packages.

    :param package_path: Path to the referenced DataPrep package.
    :param dataflow_name: Name of the Dataflow within the package.
    """
    def __init__(self, package_path: str, dataflow_name: str):
        engine_api = get_engine_api()
        self._reference = engine_api.resolve_reference(ResolveReferenceMessageArguments(package_path=package_path,
                                                                                        dataflow_name=dataflow_name))


def make_activity_reference(reference: 'dataprep.DataflowReference') -> ActivityReference:
    from .dataflow import Dataflow
    if isinstance(reference, Dataflow):
        return _to_anonymous_reference(reference)
    elif isinstance(reference, ExternalReference):
        return reference._reference
    else:
        raise TypeError('Invalid type for Dataflow reference.')
