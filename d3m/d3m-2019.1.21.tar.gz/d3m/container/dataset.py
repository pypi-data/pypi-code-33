import abc
import datetime
import hashlib
import io
import json
import logging
import os
import os.path
import pprint
import sys
import typing
from urllib import error as urllib_error, parse as url_parse

import dateparser  # type: ignore
import networkx  # type: ignore
import numpy  # type: ignore
import pandas  # type: ignore
from pandas.io import common as pandas_io_common  # type: ignore
from sklearn import datasets  # type: ignore

from . import pandas as container_pandas
from d3m import deprecate, exceptions, utils
from d3m.metadata import base as metadata_base

# See: https://gitlab.com/datadrivendiscovery/d3m/issues/66
try:
    from pyarrow import lib as pyarrow_lib  # type: ignore
except ModuleNotFoundError:
    pyarrow_lib = None

__all__ = ('Dataset',)

logger = logging.getLogger(__name__)

UNITS = {
    'B': 1, 'KB': 10**3, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12, 'PB': 10**15,
    'KiB': 2*10, 'MiB': 2*20, 'GiB': 2*30, 'TiB': 2*40, 'PiB': 2*50,
}

# A map between D3M dataset constants and semantic type URIs.
# TODO: Define properly those semantic types at those URIs.
SEMANTIC_TYPES = {
    # Resource types (files collections).
    'image': 'http://schema.org/ImageObject',
    'video': 'http://schema.org/VideoObject',
    'audio': 'http://schema.org/AudioObject',
    'text': 'http://schema.org/Text',
    'speech': 'https://metadata.datadrivendiscovery.org/types/Speech',
    'raw': 'https://metadata.datadrivendiscovery.org/types/UnspecifiedStructure',
    # Resource types (other)
    'graph': 'https://metadata.datadrivendiscovery.org/types/Graph',
    'edgeList': 'https://metadata.datadrivendiscovery.org/types/EdgeList',
    'table': 'https://metadata.datadrivendiscovery.org/types/Table',
    'timeseries': 'https://metadata.datadrivendiscovery.org/types/Timeseries',
    # Column types.
    'boolean': 'http://schema.org/Boolean',
    'integer': 'http://schema.org/Integer',
    'real': 'http://schema.org/Float',
    'string': 'http://schema.org/Text',
    'categorical': 'https://metadata.datadrivendiscovery.org/types/CategoricalData',
    'dateTime': 'http://schema.org/DateTime',
    'realVector': 'https://metadata.datadrivendiscovery.org/types/FloatVector',
    'json': 'https://metadata.datadrivendiscovery.org/types/JSON',
    'geojson': 'https://metadata.datadrivendiscovery.org/types/GeoJSON',
    # Column roles.
    'index': 'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
    'key': 'https://metadata.datadrivendiscovery.org/types/UniqueKey',
    'attribute': 'https://metadata.datadrivendiscovery.org/types/Attribute',
    'suggestedTarget': 'https://metadata.datadrivendiscovery.org/types/SuggestedTarget',
    'suggestedPrivilegedData': 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData',
    'timeIndicator': 'https://metadata.datadrivendiscovery.org/types/Time',
    'locationIndicator': 'https://metadata.datadrivendiscovery.org/types/Location',
    'boundaryIndicator': 'https://metadata.datadrivendiscovery.org/types/Boundary',
    'instanceWeight': 'https://metadata.datadrivendiscovery.org/types/InstanceWeight',
    'boundingBox': 'https://metadata.datadrivendiscovery.org/types/BoundingBox',
}

INTERVAL_SEMANTIC_TYPES = (
    'https://metadata.datadrivendiscovery.org/types/IntervalStart',
    'https://metadata.datadrivendiscovery.org/types/IntervalEnd',
)

BOUNDING_BOX_SEMANTIC_TYPES = (
    'https://metadata.datadrivendiscovery.org/types/BoundingBoxXMin',
    'https://metadata.datadrivendiscovery.org/types/BoundingBoxYMin',
    'https://metadata.datadrivendiscovery.org/types/BoundingBoxXMax',
    'https://metadata.datadrivendiscovery.org/types/BoundingBoxYMax',
)

BOUNDARY_SEMANTIC_TYPES = (
    'https://metadata.datadrivendiscovery.org/types/Interval',
    'https://metadata.datadrivendiscovery.org/types/BoundingBox',
) + INTERVAL_SEMANTIC_TYPES + BOUNDING_BOX_SEMANTIC_TYPES

# A map between D3M resource formats and media types.
MEDIA_TYPES = {
    'audio/aiff': 'audio/aiff',
    'audio/flac': 'audio/flac',
    'audio/ogg': 'audio/ogg',
    'audio/wav': 'audio/wav',
    'audio/mpeg': 'audio/mpeg',
    'image/jpeg': 'image/jpeg',
    'image/png': 'image/png',
    'video/mp4': 'video/mp4',
    'video/avi': 'video/avi',
    'text/csv': 'text/csv',
    'text/plain': 'text/plain',
    'text/gml': 'text/vnd.gml',
}

# A map between D3M file extensions and media types.
# Based on: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/blob/shared/documentation/supportedResourceTypesFormats.json
FILE_EXTENSIONS = {
    '.aif': 'audio/aiff',
    '.aiff': 'audio/aiff',
    '.flac': 'audio/flac',
    '.ogg': 'audio/ogg',
    '.wav': 'audio/wav',
    '.mp3': 'audio/mpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.csv': 'text/csv',
    '.gml': 'text/vnd.gml',
    '.txt': 'text/plain',
    '.mp4': 'video/mp4',
    '.avi': 'video/avi',
}


class ComputeDigest(utils.Enum):
    """
    Enumeration of possible approaches to computing dataset digest.
    """

    NEVER = 1
    ONLY_IF_MISSING = 2
    ALWAYS = 3


def parse_size(size_string: str) -> int:
    number, unit = [string.strip() for string in size_string.split()]
    return int(float(number) * UNITS[unit])


def is_simple_boundary(semantic_types: typing.Tuple[str]) -> bool:
    """
    A simple boundary is a column with only "https://metadata.datadrivendiscovery.org/types/Boundary"
    semantic type and no other.
    """

    return 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types and not any(boundary_semantic_type in semantic_types for boundary_semantic_type in BOUNDARY_SEMANTIC_TYPES)


def update_digest(hash: typing.Any, file_path: str) -> None:
    with open(file_path, 'rb') as file:
        while True:
            # Reading is buffered, so we can read smaller chunks.
            chunk = file.read(hash.block_size)
            if not chunk:
                break
            hash.update(chunk)


# This exists as a reference implementation for computing a digest of D3M dataset.
# Loader below does an equivalent computation as part of dataset loading process.
def get_d3m_dataset_digest(dataset_doc_path: str) -> str:
    hash = hashlib.sha256()

    with open(dataset_doc_path, 'r') as dataset_doc_file:
        dataset_doc = json.load(dataset_doc_file)

    dataset_path = os.path.dirname(dataset_doc_path)

    for data_resource in dataset_doc['dataResources']:
        if data_resource['isCollection']:
            collection_path = os.path.join(dataset_path, data_resource['resPath'])

            # We assume that we can just concat "collection_path" with a value in the column.
            assert collection_path[-1] == '/'

            for filename in utils.list_files(collection_path):
                file_path = os.path.join(collection_path, filename)

                # We include both the filename and the content.
                hash.update(os.path.join(data_resource['resPath'], filename).encode('utf8'))
                update_digest(hash, file_path)

        else:
            resource_path = os.path.join(dataset_path, data_resource['resPath'])

            # We include both the filename and the content.
            hash.update(data_resource['resPath'].encode('utf8'))
            update_digest(hash, resource_path)

    # We remove digest, if it exists in dataset description, before computing the digest over the rest.
    dataset_doc['about'].pop('digest', None)

    # We add to hash also the dataset description, with sorted keys.
    hash.update(json.dumps(dataset_doc, sort_keys=True).encode('utf8'))

    return hash.hexdigest()


class Loader(metaclass=utils.AbstractMetaclass):
    """
    A base class for dataset loaders.
    """

    @abc.abstractmethod
    def can_load(self, dataset_uri: str) -> bool:
        """
        Return ``True`` if this loader can load a dataset from a given URI ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load a dataset from.

        Returns
        -------
        bool
            ``True`` if this loader can load a dataset from ``dataset_uri``.
        """

    @abc.abstractmethod
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, merge_score_targets: bool = True) -> 'Dataset':
        """
        Loads the dataset at ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.
        lazy : bool
            If ``True``, load only top-level metadata and not whole dataset.
        compute_digest : ComputeDigest
            Compute a digest over the data?
        strict_digest : bool
            If computed digest does not match the one provided in metadata, raise an exception?
        merge_score_targets : bool
            If a scoring dataset has target values in a separate file, merge them in?

        Returns
        -------
        Dataset
            A loaded dataset.
        """


class Saver(metaclass=utils.AbstractMetaclass):
    """
    A base class for dataset savers.
    """

    @abc.abstractmethod
    def can_save(self, dataset_uri: str) -> bool:
        """
        Return ``True`` if this saver can save a dataset to a given URI ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to save a dataset to.

        Returns
        -------
        bool
            ``True`` if this saver can save a dataset to ``dataset_uri``.
        """

    @abc.abstractmethod
    def save(self, dataset: 'Dataset', dataset_uri: str, *, resource_id: str = None) -> None:
        """
        Saves the dataset ``dataset`` to ``dataset_uri``.

        Parameters
        ----------
        dataset : Dataset
            A dataset to save.
        dataset_uri : str
            A URI to save to.
        resource_id : str
            Save only resource with this ID. Some savers might not support saving datasets with multiple resources.
        """


class D3MDatasetLoader(Loader):
    """
    A class for loading of D3M datasets.

    Loader support only loading from a local file system.
    URI should point to the ``datasetDoc.json`` file in the D3M dataset directory.
    """

    SUPPORTED_VERSIONS = {'3.0', '3.1', '3.1.1', '3.1.2', '3.2.0'}

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri)
        except Exception:
            return False

        if parsed_uri.scheme != 'file':
            return False

        if parsed_uri.netloc not in ['', 'localhost']:
            return False

        if not parsed_uri.path.startswith('/'):
            return False

        if os.path.basename(parsed_uri.path) != 'datasetDoc.json':
            return False

        return True

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_path: str, dataset_doc: typing.Dict,
                   dataset_id: typing.Optional[str], dataset_digest: typing.Optional[str],
                   compute_digest: ComputeDigest, strict_digest: bool, merge_score_targets: bool) -> typing.Tuple[metadata_base.DataMetadata, typing.Optional[str]]:
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or (compute_digest == ComputeDigest.ONLY_IF_MISSING and dataset_digest is None):
            hash = hashlib.sha256()
        else:
            hash = None

        for data_resource in dataset_doc['dataResources']:
            if data_resource['isCollection']:
                resources[data_resource['resID']], metadata = self._load_collection(dataset_path, data_resource, metadata, hash)
            else:
                loader = getattr(self, '_load_resource_type_{resource_type}'.format(resource_type=data_resource['resType']), None)
                if loader is None:
                    raise exceptions.NotSupportedError("Resource type '{resource_type}' is not supported.".format(resource_type=data_resource['resType']))

                resources[data_resource['resID']], metadata = loader(dataset_path, data_resource, metadata, hash)

        # Backwards compatibility. If there is no resource marked as a dataset entry point,
        # check if there is any resource with a suitable filename.
        for data_resource in dataset_doc['dataResources']:
            if metadata.has_semantic_type((data_resource['resID'],), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                break
        else:
            for data_resource in dataset_doc['dataResources']:
                if os.path.splitext(os.path.basename(data_resource['resPath']))[0] == 'learningData':
                    metadata = metadata.add_semantic_type((data_resource['resID'],), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint')

        # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
        # They are the same as TEST dataset splits, but we present them differently, so that
        # SCORE dataset splits have targets as part of data.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
        if merge_score_targets and os.path.exists(os.path.join(dataset_path, '..', 'targets.csv')):
            self._merge_score_targets(resources, metadata, dataset_path, hash)

        if hash is not None:
            # We remove digest, if it exists in dataset description, before computing the digest over the rest.
            # We modify "dataset_doc" here, but this is OK, we do not need it there anymore at this point.
            dataset_doc['about'].pop('digest', None)

            # We add to hash also the dataset description, with sorted keys.
            hash.update(json.dumps(dataset_doc, sort_keys=True).encode('utf8'))

            new_dataset_digest = hash.hexdigest()

            if dataset_digest is not None and dataset_digest != new_dataset_digest:
                if strict_digest:
                    raise exceptions.DigestMismatchError(
                        "Digest for dataset '{dataset_id}' does not match one from dataset description. Dataset description digest: {dataset_digest}. Computed digest: {new_dataset_digest}.".format(
                            dataset_id=dataset_id or dataset_doc['about']['datasetID'],
                            dataset_digest=dataset_digest,
                            new_dataset_digest=new_dataset_digest,
                        )
                    )
                else:
                    logger.warning(
                        "Digest for dataset '%(dataset_id)s' does not match one from dataset description. Dataset description digest: %(dataset_digest)s. Computed digest: %(new_dataset_digest)s.",
                        {
                            'dataset_id': dataset_id or dataset_doc['about']['datasetID'],
                            'dataset_digest': dataset_digest,
                            'new_dataset_digest': new_dataset_digest,
                        },
                    )
        else:
            new_dataset_digest = dataset_doc['about'].get('digest', None)

        return metadata, new_dataset_digest

    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, merge_score_targets: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri)

        dataset_doc_path = parsed_uri.path
        dataset_path = os.path.dirname(dataset_doc_path)

        try:
            with open(dataset_doc_path, 'r') as dataset_doc_file:
                dataset_doc = json.load(dataset_doc_file)
        except FileNotFoundError as error:
            raise exceptions.DatasetNotFoundError("D3M dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error

        if dataset_doc.get('about', {}).get('datasetSchemaVersion', None) not in self.SUPPORTED_VERSIONS:
            raise exceptions.NotSupportedVersionError("Only supporting dataset descriptions whose schema version among {versions}.".format(versions=self.SUPPORTED_VERSIONS))

        # We do not compute digest here, but we use one from dataset description if it exist.
        # This is different from other loaders which compute digest when lazy loading and check
        # it after data is finally loaded to make sure data has not changed in meantime.
        dataset_digest = dataset_doc['about'].get('digest', None)

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_digest = self._load_data(
                resources, metadata, dataset_path=dataset_path, dataset_doc=dataset_doc, dataset_id=dataset_id,
                dataset_digest=dataset_digest, compute_digest=compute_digest, strict_digest=strict_digest,
                merge_score_targets=merge_score_targets,
            )

            metadata = self._load_qualities(dataset_doc, metadata)

        else:
            def load_lazy(dataset: Dataset) -> None:
                nonlocal dataset_digest

                # We disable "for_value" checking while we are modifying both data and metadata.
                dataset.metadata = dataset.metadata.set_for_value(None)

                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_path=dataset_path, dataset_doc=dataset_doc, dataset_id=dataset_id,
                    dataset_digest=dataset_digest, compute_digest=compute_digest, strict_digest=strict_digest,
                    merge_score_targets=merge_score_targets,
                )

                dataset.metadata = self._load_qualities(dataset_doc, dataset.metadata)

                new_metadata = {
                    'dimension': {'length': len(dataset)},
                }

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.set_for_value(dataset)

                dataset._load_lazy = None

        document_dataset_id = dataset_doc['about']['datasetID']
        # Handle a special case for SCORE dataset splits (those which have "targets.csv" file).
        # They are the same as TEST dataset splits, but we present them differently, so that
        # SCORE dataset splits have targets as part of data. Because of this we also update
        # corresponding dataset ID.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/176
        if merge_score_targets and os.path.exists(os.path.join(dataset_path, '..', 'targets.csv')) and document_dataset_id.endswith('_TEST'):
            document_dataset_id = document_dataset_id[:-5] + '_SCORE'

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or document_dataset_id,
            # "datasetVersion" is required by the schema, but we want to be compatible with
            # dataset problem descriptions which do not adhere to the schema.
            'version': dataset_version or dataset_doc['about'].get('datasetVersion', '1.0'),
            'name': dataset_name or dataset_doc['about']['datasetName'],
            'location_uris': [
                # We reconstruct the URI to normalize it.
                'file://{dataset_doc_path}'.format(dataset_doc_path=dataset_doc_path),
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        if dataset_doc['about'].get('description', None):
            dataset_metadata['description'] = dataset_doc['about']['description']

        if dataset_doc['about'].get('approximateSize', None):
            try:
                dataset_metadata['approximate_stored_size'] = parse_size(dataset_doc['about']['approximateSize'])
            except Exception as error:
                raise ValueError("Unable to parse 'approximateSize': {approximate_size}".format(approximate_size=dataset_doc['about']['approximateSize'])) from error

        if dataset_doc['about'].get('datasetURI', None):
            typing.cast(typing.List[str], dataset_metadata['location_uris']).append(dataset_doc['about']['datasetURI'])

        dataset_source = {
            'license': dataset_doc['about']['license'],
            'redacted': dataset_doc['about']['redacted'],
            # "humanSubjectsResearch" is required by the schema, but we want to be compatible with
            # dataset problem descriptions which do not adhere to the schema.
            'human_subjects_research': dataset_doc['about'].get('humanSubjectsResearch', False),
        }

        if dataset_doc['about'].get('source', None):
            dataset_source['name'] = dataset_doc['about']['source']

        if dataset_doc['about'].get('citation', None):
            dataset_source['citation'] = dataset_doc['about']['citation']

        if dataset_doc['about'].get('publicationDate', None):
            try:
                # If no timezone information is provided, we assume UTC. If there is timezone information, we convert
                # timestamp to UTC, but then remove timezone information before formatting to not have "+00:00" added
                # and we then manually add "Z" instead (which has equivalent meaning).
                dataset_source['published'] = dateparser.parse(dataset_doc['about']['publicationDate'], settings={'TIMEZONE': 'UTC'}).replace(tzinfo=None).isoformat('T') + 'Z'
            except Exception as error:
                raise ValueError("Unable to parse 'publicationDate': {publication_date}".format(publication_date=dataset_doc['about']['publicationDate'])) from error

        if dataset_doc['about'].get('sourceURI', None):
            dataset_source['uris'] = [dataset_doc['about']['sourceURI']]

        dataset_metadata['source'] = dataset_source

        if dataset_doc['about'].get('applicationDomain', None):
            # Application domain has no vocabulary specified so we map it to keywords.
            dataset_metadata['keywords'] = [dataset_doc['about']['applicationDomain']]

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata, load_lazy=load_lazy)

    def _load_qualities(self, dataset_doc: typing.Dict, metadata: metadata_base.DataMetadata) -> metadata_base.DataMetadata:
        # An alternative way to describe LUPI datasets using process D3M qualities.
        # See: https://gitlab.com/datadrivendiscovery/d3m/issues/61
        #      https://gitlab.com/datadrivendiscovery/d3m/issues/225
        for quality in dataset_doc.get('qualities', []):
            if quality['qualName'] != 'privilegedFeature':
                continue

            if quality['qualValue'] != 'True':
                continue

            restricted_to = quality.get('restrictedTo', {})

            column_index = restricted_to.get('resComponent', {}).get('columnIndex', None)
            if column_index is not None:
                metadata = self._add_semantic_type_for_column_index(metadata, restricted_to['resID'], column_index, 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData')
                continue

            column_name = restricted_to.get('resComponent', {}).get('columnName', None)
            if column_name is not None:
                metadata = self._add_semantic_type_for_column_name(metadata, restricted_to['resID'], column_name, 'https://metadata.datadrivendiscovery.org/types/SuggestedPrivilegedData')
                continue

        return metadata

    # TODO: Make this part of metadata API.
    def _add_semantic_type_for_column_index(self, metadata: metadata_base.DataMetadata, resource_id: str, column_index: int, semantic_type: str) -> metadata_base.DataMetadata:
        semantic_types = list(metadata.query((resource_id, metadata_base.ALL_ELEMENTS, column_index)).get('semantic_types', []))

        if semantic_type in semantic_types:
            return metadata

        semantic_types.append(semantic_type)

        return metadata.update((resource_id, metadata_base.ALL_ELEMENTS, column_index), {
            'semantic_types': semantic_types,
        })

    # TODO: Make this part of metadata API.
    def _add_semantic_type_for_column_name(self, metadata: metadata_base.DataMetadata, resource_id: str, column_name: str, semantic_type: str) -> metadata_base.DataMetadata:
        for column_index in range(metadata.query((resource_id, metadata_base.ALL_ELEMENTS))['dimension']['length']):
            if metadata.query((resource_id, metadata_base.ALL_ELEMENTS, column_index)).get('name', None) == column_name:
                return self._add_semantic_type_for_column_index(metadata, resource_id, column_index, semantic_type)

        raise exceptions.ColumnNameError(
            "Cannot resolve column name '{column_name}' in resource with ID '{resource_id}'.".format(
                resource_id=resource_id,
                column_name=column_name,
            ),
        )

    def _load_collection(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                         hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert data_resource['isCollection']

        collection_path = os.path.join(dataset_path, data_resource['resPath'])

        # We assume that we can just concat "collection_path" with a value in the column.
        assert collection_path[-1] == '/'

        all_media_types = [MEDIA_TYPES[format] for format in data_resource['resFormat']]

        filenames = []
        media_types = []

        for filename in utils.list_files(collection_path):
            file_path = os.path.join(collection_path, filename)

            filename_extension = os.path.splitext(filename)[1]

            filenames.append(filename)

            try:
                media_type = FILE_EXTENSIONS[filename_extension]
            except KeyError as error:
                raise TypeError("Unsupported file extension for file '{filename}'.".format(filename=filename)) from error

            if media_type not in all_media_types:
                raise TypeError("Unexpected media type '{media_type}' for file '{filename}'. Expected {all_media_types}.".format(
                    media_type=media_type, filename=filename, all_media_types=all_media_types,
                ))

            media_types.append(media_type)

            if hash is not None:
                # We include both the filename and the content.
                hash.update(os.path.join(data_resource['resPath'], filename).encode('utf8'))
                update_digest(hash, file_path)

        data = container_pandas.DataFrame({'filename': filenames}, columns=['filename'], dtype=object, generate_metadata=False)

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/FilesCollection',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': 1,
            },
        })

        location_base_uri = 'file://{collection_path}'.format(collection_path=collection_path)
        if not location_base_uri.endswith('/'):
            location_base_uri += '/'

        column_metadata = {
            'name': 'filename',
            'structural_type': str,
            'location_base_uris': [
                location_base_uri,
            ],
            # A superset of all media types of files in this collection.
            'media_types': all_media_types,
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                'https://metadata.datadrivendiscovery.org/types/FileName',
                SEMANTIC_TYPES[data_resource['resType']],
            ],
        }

        if data_resource.get('columns', None):
            columns_metadata = []

            for column in data_resource['columns']:
                columns_metadata.append(self._get_column_metadata(column))
                columns_metadata[-1]['name'] = column['colName']

            column_metadata['file_columns'] = columns_metadata

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, 0), column_metadata)

        for i, media_type in enumerate(media_types):
            metadata = metadata.update((data_resource['resID'], i, 0), {
                # A media type of this particular file.
                'media_types': [media_type],
            })

        return data, metadata

    def _load_resource_type_table(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                                  hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert not data_resource['isCollection']

        data = None
        column_names = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        expected_names = None
        if data_resource.get('columns', None):
            expected_names = []
            for i, column in enumerate(data_resource['columns']):
                assert i == column['colIndex'], (i, column['colIndex'])
                expected_names.append(column['colName'])

        if data_resource['resFormat'] == ['text/csv']:
            data = pandas.read_csv(
                data_path,
                usecols=expected_names,
                # We do not want to do any conversion of values at this point.
                # This should be done by primitives later on.
                dtype=str,
                # We always expect one row header.
                header=0,
                # We want empty strings and not NaNs.
                na_filter=False,
                encoding='utf8',
                low_memory=False,
                memory_map=True,
            )

            column_names = list(data.columns)

            if expected_names is not None and expected_names != column_names:
                raise ValueError("Mismatch between column names in data {column_names} and expected names {expected_names}.".format(
                    column_names=column_names,
                    expected_names=expected_names,
                ))

            if hash is not None:
                # We include both the filename and the content.
                # TODO: Currently we read the file twice, once for reading and once to compute digest. Could we do it in one pass? Would it make it faster?
                hash.update(data_resource['resPath'].encode('utf8'))
                update_digest(hash, data_path)

        else:
            raise exceptions.NotSupportedError("Resource format '{resource_format}' for table '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath'],
            ))

        if data is None:
            raise FileNotFoundError("Data file for table '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath'],
            ))

        data = container_pandas.DataFrame(data, generate_metadata=False)

        assert column_names is not None

        semantic_types = [SEMANTIC_TYPES[data_resource['resType']]]

        if data_resource['resID'] == 'learningData':
            semantic_types.append('https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint')

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': semantic_types,
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for i, column_name in enumerate(column_names):
            metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, i), {
                'name': column_name,
                'structural_type': str,
            })

        if expected_names is not None:
            for i, column in enumerate(data_resource['columns']):
                column_metadata = self._get_column_metadata(column)

                if 'https://metadata.datadrivendiscovery.org/types/Boundary' in column_metadata['semantic_types'] and 'boundary_for' not in column_metadata:
                    # Let's reconstruct for which column this is a boundary: currently
                    # this seems to be the first non-boundary column before this one.
                    for column_index in range(i - 1, 0, -1):
                        column_semantic_types = metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index)).get('semantic_types', ())
                        if 'https://metadata.datadrivendiscovery.org/types/Boundary' not in column_semantic_types:
                            column_metadata['boundary_for'] = {
                                'resource_id': data_resource['resID'],
                                'column_index': column_index,
                            }
                            break

                metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, i), column_metadata)

            current_boundary_start = None
            current_boundary_list: typing.Tuple[str, ...] = None
            column_index = 0
            while column_index < len(data_resource['columns']):
                column_semantic_types = metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index)).get('semantic_types', ())
                if is_simple_boundary(column_semantic_types):
                    # Let's reconstruct which type of a boundary this is. Heuristic is simple.
                    # If there are two boundary columns next to each other, it is an interval.
                    # If there are four, it is a bounding box.
                    if current_boundary_start is None:
                        assert current_boundary_list is None

                        count = 1
                        for next_column_index in range(column_index + 1, len(data_resource['columns'])):
                            if is_simple_boundary(metadata.query((data_resource['resID'], metadata_base.ALL_ELEMENTS, next_column_index)).get('semantic_types', ())):
                                count += 1
                            else:
                                break

                        if count == 2:
                            current_boundary_start = column_index
                            current_boundary_list = INTERVAL_SEMANTIC_TYPES
                        elif count == 4:
                            current_boundary_start = column_index
                            current_boundary_list = BOUNDING_BOX_SEMANTIC_TYPES
                        else:
                            # Unsupported group of boundary columns, let's skip them all.
                            column_index += count
                            continue

                    column_semantic_types = column_semantic_types + (current_boundary_list[column_index - current_boundary_start],)
                    metadata = metadata.update((data_resource['resID'], metadata_base.ALL_ELEMENTS, column_index), {
                        'semantic_types': column_semantic_types,
                    })

                    if column_index - current_boundary_start + 1 == len(current_boundary_list):
                        current_boundary_start = None
                        current_boundary_list = None

                column_index += 1

        return data, metadata

    def _load_resource_type_timeseries(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                                       hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert not data_resource['isCollection']

        return self._load_resource_type_table(dataset_path, data_resource, metadata, hash)

    def _load_resource_type_edgeList(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata,
                                     hash: typing.Any) -> typing.Tuple[container_pandas.DataFrame, metadata_base.DataMetadata]:
        assert not data_resource['isCollection']

        return self._load_resource_type_table(dataset_path, data_resource, metadata, hash)

    def _load_resource_type_graph(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_base.DataMetadata, hash: typing.Any) -> \
            typing.Tuple[typing.Union[networkx.classes.graph.Graph, networkx.classes.digraph.DiGraph, networkx.classes.multigraph.MultiGraph,
                                      networkx.classes.multidigraph.MultiDiGraph], metadata_base.DataMetadata]:

        assert not data_resource['isCollection']

        data = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        if data_resource['resFormat'] == ['text/gml']:
            data = networkx.read_gml(data_path, label='id')

            if hash is not None:
                # We include both the filename and the content.
                # TODO: Currently we read the file twice, once for reading and once to compute digest. Could we do it in one pass? Would it make it faster?
                hash.update(data_resource['resPath'].encode('utf8'))
                update_digest(hash, data_path)

        else:
            raise exceptions.NotSupportedError("Resource format '{resource_format}' for graph '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath']
            ))

        if data is None:
            raise FileNotFoundError("Data file for graph '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath']
            ))

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [SEMANTIC_TYPES[data_resource['resType']]],
            'dimension': {
                'name': 'nodes',
                'length': len(data),
            },
        })

        return data, metadata

    def _get_column_metadata(self, column: typing.Dict) -> typing.Dict:
        REFERENCE_MAP = {
            'node': 'NODE',
            'nodeAttribute': 'NODE_ATTRIBUTE',
            'edge': 'EDGE',
            'edgeAttribute': 'EDGE_ATTRIBUTE',
        }

        semantic_types = [SEMANTIC_TYPES[column['colType']]]

        for role in column['role']:
            semantic_types.append(SEMANTIC_TYPES[role])

        column_metadata: typing.Dict[str, typing.Any] = {
            'semantic_types': semantic_types,
        }

        if column.get('colDescription', None):
            column_metadata['description'] = column['colDescription']

        if column.get('refersTo', None):
            if isinstance(column['refersTo']['resObject'], str):
                if column['refersTo']['resObject'] == 'item':
                    # We represent collections as a table with one column of filenames.
                    column_metadata['foreign_key'] = {
                        'type': 'COLUMN',
                        'resource_id': column['refersTo']['resID'],
                        'column_index': 0,
                    }
                elif column['refersTo']['resObject'] in REFERENCE_MAP.keys():
                    column_metadata['foreign_key'] = {
                        'type': REFERENCE_MAP[column['refersTo']['resObject']],
                        'resource_id': column['refersTo']['resID'],
                    }
                else:
                    raise exceptions.UnexpectedValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))
            else:
                if 'columnIndex' in column['refersTo']['resObject']:
                    if 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types:
                        column_metadata['boundary_for'] = {
                            'resource_id': column['refersTo']['resID'],
                            'column_index': column['refersTo']['resObject']['columnIndex'],
                        }
                    else:
                        column_metadata['foreign_key'] = {
                            'type': 'COLUMN',
                            'resource_id': column['refersTo']['resID'],
                            'column_index': column['refersTo']['resObject']['columnIndex'],
                        }
                elif 'columnName' in column['refersTo']['resObject']:
                    if 'https://metadata.datadrivendiscovery.org/types/Boundary' in semantic_types:
                        column_metadata['boundary_for'] = {
                            'resource_id': column['refersTo']['resID'],
                            'column_name': column['refersTo']['resObject']['columnName'],
                        }
                    else:
                        column_metadata['foreign_key'] = {
                            'type': 'COLUMN',
                            'resource_id': column['refersTo']['resID'],
                            'column_name': column['refersTo']['resObject']['columnName'],
                        }
                else:
                    raise exceptions.UnexpectedValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))

        return column_metadata

    def _merge_score_targets(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, dataset_path: str, hash: typing.Any) -> None:
        targets_path = os.path.join(dataset_path, '..', 'targets.csv')

        targets = pandas.read_csv(
            targets_path,
            # We do not want to do any conversion of values at this point.
            # This should be done by primitives later on.
            dtype=str,
            # We always expect one row header.
            header=0,
            # We want empty strings and not NaNs.
            na_filter=False,
            encoding='utf8',
            low_memory=False,
            memory_map=True,
        )

        for resource_id, resource in resources.items():
            # We assume targets are only in the dataset entry point.
            if metadata.has_semantic_type((resource_id,), 'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint'):
                # We first make sure targets match resource in row order. At this stage all values
                # are strings, so we can fill simply with empty strings if it happens that index
                # values do not match (which in fact should never happen).
                reindexed_targets = targets.set_index('d3mIndex').reindex(resource.loc[:, 'd3mIndex'], fill_value='').reset_index()

                for column_name in reindexed_targets.columns:
                    if column_name == 'd3mIndex':
                        continue

                    # We match columns based on their names.
                    if column_name in resource.columns:
                        resource.loc[:, column_name] = reindexed_targets.loc[:, column_name]

                resources[resource_id] = resource


class CSVLoader(Loader):
    """
    A class for loading a dataset from a CSV file.

    Loader supports both loading a dataset from a local file system or remote locations.
    URI should point to a file with ``.csv`` file extension.
    """

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri)
        except Exception:
            return False

        if parsed_uri.scheme not in pandas_io_common._VALID_URLS:
            return False

        if parsed_uri.scheme == 'file':
            if parsed_uri.netloc not in ['', 'localhost']:
                return False

            if not parsed_uri.path.startswith('/'):
                return False

        for extension in ('', '.gz', '.bz2', '.zip', 'xz'):
            if parsed_uri.path.endswith('.csv' + extension):
                return True

        return False

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_uri: str,
                   compute_digest: ComputeDigest) -> typing.Tuple[metadata_base.DataMetadata, int, typing.Optional[str]]:
        try:
            buffer, compression, should_close = self._get_buffer_and_compression(dataset_uri)
        except FileNotFoundError as error:
            raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
        except urllib_error.HTTPError as error:
            if error.code == 404:
                raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
            else:
                raise error
        except urllib_error.URLError as error:
            if isinstance(error.reason, FileNotFoundError):
                raise exceptions.DatasetNotFoundError("CSV dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri)) from error
            else:
                raise error

        # CSV files do not have digest, so "ALWAYS" and "ONLY_IF_MISSING" is the same.
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or compute_digest == ComputeDigest.ONLY_IF_MISSING:
            buffer_digest = self._get_digest(buffer)
        else:
            buffer_digest = None

        buffer_size = len(buffer.getvalue())

        data = pandas.read_csv(
            buffer,
            # We do not want to do any conversion of values at this point.
            # This should be done by primitives later on.
            dtype=str,
            # We always expect one row header.
            header=0,
            # We want empty strings and not NaNs.
            na_filter=False,
            compression=compression,
            encoding='utf8',
            low_memory=False,
        )

        if should_close:
            try:
                buffer.close()
            except Exception:
                pass

        column_names = list(data.columns)

        data = container_pandas.DataFrame(data, generate_metadata=False)

        resources['learningData'] = data

        metadata = metadata.update(('learningData',), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for i, column_name in enumerate(column_names):
            metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, i), {
                'name': column_name,
                'structural_type': str,
            })

        return metadata, buffer_size, buffer_digest

    def _get_buffer_and_compression(self, dataset_uri: str) -> typing.Tuple[io.BytesIO, str, bool]:
        compression = pandas_io_common._infer_compression(dataset_uri, 'infer')
        buffer, _, compression, should_close = pandas_io_common.get_filepath_or_buffer(dataset_uri, 'utf8', compression)

        return buffer, compression, should_close

    def _get_digest(self, buffer: io.BytesIO) -> str:
        return hashlib.sha256(buffer.getvalue()).hexdigest()

    # "strict_digest" is ignored, there is no metadata to compare digest against.
    # "merge_score_targets" is ignored as well.
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, merge_score_targets: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri)

        # Pandas requires a host for "file" URIs.
        if parsed_uri.scheme == 'file' and parsed_uri.netloc == '':
            parsed_uri = parsed_uri._replace(netloc='localhost')
            dataset_uri = url_parse.urlunparse(parsed_uri)

        dataset_size = None
        dataset_digest = None

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_size, dataset_digest = self._load_data(
                resources, metadata, dataset_uri=dataset_uri, compute_digest=compute_digest,
            )

        else:
            def load_lazy(dataset: Dataset) -> None:
                # We disable "for_value" checking while we are modifying both data and metadata.
                dataset.metadata = dataset.metadata.set_for_value(None)

                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_size, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_uri=dataset_uri, compute_digest=compute_digest,
                )

                new_metadata = {
                    'dimension': {'length': len(dataset)},
                    'stored_size': dataset_size,
                }

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.set_for_value(dataset)

                dataset._load_lazy = None

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'name': dataset_name or os.path.basename(parsed_uri.path),
            'location_uris': [
                dataset_uri,
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_version is not None:
            dataset_metadata['version'] = dataset_version

        if dataset_size is not None:
            dataset_metadata['stored_size'] = dataset_size

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata, load_lazy=load_lazy)


class SklearnExampleLoader(Loader):
    """
    A class for loading example scikit-learn datasets.

    URI should be of the form ``sklearn://<name of the dataset>``, where names come from
    ``sklearn.datasets.load_*`` function names.
    """

    def can_load(self, dataset_uri: str) -> bool:
        if dataset_uri.startswith('sklearn://'):
            return True

        return False

    def _load_data(self, resources: typing.Dict, metadata: metadata_base.DataMetadata, *, dataset_path: str,
                   compute_digest: ComputeDigest) -> typing.Tuple[metadata_base.DataMetadata, typing.Optional[str], typing.Optional[str]]:
        bunch = self._get_bunch(dataset_path)

        # Sklearn datasets do not have digest, so "ALWAYS" and "ONLY_IF_MISSING" is the same.
        # Allowing "True" for backwards compatibility.
        if compute_digest is True or compute_digest == ComputeDigest.ALWAYS or compute_digest == ComputeDigest.ONLY_IF_MISSING:
            bunch_digest = self._get_digest(bunch)
        else:
            bunch_digest = None

        bunch_description = bunch.get('DESCR', None) or None

        bunch_data = bunch['data']
        bunch_target = bunch['target']

        if len(bunch_data.shape) == 1:
            bunch_data = bunch_data.reshape((bunch_data.shape[0], 1))
        if len(bunch_target.shape) == 1:
            bunch_target = bunch_target.reshape((bunch_target.shape[0], 1))

        column_names = []
        target_values = None

        if 'feature_names' in bunch:
            for feature_name in bunch['feature_names']:
                column_names.append(str(feature_name))

        if 'target_names' in bunch:
            if len(bunch['target_names']) == bunch_target.shape[1]:
                for target_name in bunch['target_names']:
                    column_names.append(str(target_name))
            else:
                target_values = [str(target_value) for target_value in bunch['target_names']]

        if target_values is not None:
            converted_target = numpy.empty(bunch_target.shape, dtype=object)

            for i, row in enumerate(bunch_target):
                for j, column in enumerate(row):
                    converted_target[i, j] = target_values[column]
        else:
            converted_target = bunch_target

        data = numpy.concatenate((bunch_data, converted_target), axis=1)

        # Add names for any extra columns. We do not really check for duplicates because Pandas allow columns with the same name.
        for i in range(len(column_names), len(data[0])):
            column_names.append('column {i}'.format(i=i))

        data = container_pandas.DataFrame(data, columns=column_names, generate_metadata=False)

        resources['learningData'] = data

        metadata = metadata.update(('learningData',), {
            'structural_type': type(data),
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/Table',
                'https://metadata.datadrivendiscovery.org/types/DatasetEntryPoint',
            ],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for column_index in range(bunch_data.shape[1]):
            column_metadata: typing.Dict[str, typing.Any] = {
                'structural_type': bunch_data.dtype.type,
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Attribute'],
                'name': column_names[column_index],
            }

            metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, column_index), column_metadata)

        for i in range(bunch_target.shape[1]):
            column_index = bunch_data.shape[1] + i

            column_metadata = {
                'structural_type': str if target_values is not None else bunch_target.dtype.type,
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/SuggestedTarget'],
                'name': column_names[column_index],
            }

            if target_values is not None:
                column_metadata['semantic_types'].append('https://metadata.datadrivendiscovery.org/types/CategoricalData')

            metadata = metadata.update(('learningData', metadata_base.ALL_ELEMENTS, column_index), column_metadata)

        return metadata, bunch_description, bunch_digest

    def _get_digest(self, bunch: typing.Dict) -> str:
        hash = hashlib.sha256()

        hash.update(bunch['data'].tobytes())
        hash.update(bunch['target'].tobytes())

        if 'feature_names' in bunch:
            if isinstance(bunch['feature_names'], list):
                for feature_name in bunch['feature_names']:
                    hash.update(feature_name.encode('utf8'))
            else:
                hash.update(bunch['feature_names'].tobytes())

        if 'target_names' in bunch:
            if isinstance(bunch['target_names'], list):
                for target_name in bunch['target_names']:
                    hash.update(target_name.encode('utf8'))
            else:
                hash.update(bunch['target_names'].tobytes())

        if 'DESCR' in bunch:
            hash.update(bunch['DESCR'].encode('utf8'))

        return hash.hexdigest()

    def _get_bunch(self, dataset_path: str) -> typing.Dict:
        return getattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path))()

    # "strict_digest" is ignored, there is no metadata to compare digest against.
    # "merge_score_targets is ignored as well.
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, merge_score_targets: bool = True) -> 'Dataset':
        assert self.can_load(dataset_uri)

        dataset_path = dataset_uri[len('sklearn://'):]

        if not hasattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path)):
            raise exceptions.DatasetNotFoundError("Sklearn dataset '{dataset_uri}' cannot be found.".format(dataset_uri=dataset_uri))

        dataset_description = None
        dataset_digest = None

        resources: typing.Dict = {}
        metadata = metadata_base.DataMetadata()

        if not lazy:
            load_lazy = None

            metadata, dataset_description, dataset_digest = self._load_data(
                resources, metadata, dataset_path=dataset_path, compute_digest=compute_digest,
            )

        else:
            def load_lazy(dataset: Dataset) -> None:
                # We disable "for_value" checking while we are modifying both data and metadata.
                dataset.metadata = dataset.metadata.set_for_value(None)

                # "dataset" can be used as "resources", it is a dict of values.
                dataset.metadata, dataset_description, dataset_digest = self._load_data(
                    dataset, dataset.metadata, dataset_path=dataset_path, compute_digest=compute_digest,
                )

                new_metadata: typing.Dict = {
                    'dimension': {'length': len(dataset)},
                }

                if dataset_description is not None:
                    new_metadata['description'] = dataset_description

                if dataset_digest is not None:
                    new_metadata['digest'] = dataset_digest

                dataset.metadata = dataset.metadata.update((), new_metadata)
                dataset.metadata = dataset.metadata.set_for_value(dataset)

                dataset._load_lazy = None

        dataset_metadata = {
            'schema': metadata_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'name': dataset_name or dataset_path,
            'location_uris': [
                dataset_uri,
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_version is not None:
            dataset_metadata['version'] = dataset_version

        if dataset_description is not None:
            dataset_metadata['description'] = dataset_description

        if dataset_digest is not None:
            dataset_metadata['digest'] = dataset_digest

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata, load_lazy=load_lazy)


D = typing.TypeVar('D', bound='Dataset')


# TODO: It should be probably immutable.
class Dataset(dict):
    """
    A class representing a dataset.

    Internally, it is a dictionary containing multiple resources (e.g., tables).

    Parameters
    ----------
    resources : Mapping
        A map from resource IDs to resources.
    metadata : DataMetadata
        Metadata associated with the ``data``.
    load_lazy : Callable
        If constructing a lazy dataset, calling this function will read all the
        data and convert the dataset to a non-lazy one.
    generate_metadata: bool
        Automatically generate and update the metadata.
    check : bool
        Check if data matches the metadata. DEPRECATED: argument ignored.
    source : primitive or Any
        A source of initial metadata. Can be an instance of a primitive or any other relevant
        source reference. DEPRECATED: argument ignored.
    timestamp : datetime
        A timestamp of initial metadata. DEPRECATED: argument ignored.
    """

    metadata: metadata_base.DataMetadata = None
    loaders: typing.List[Loader] = [
        D3MDatasetLoader(),
        CSVLoader(),
        SklearnExampleLoader(),
    ]
    savers: typing.List[Saver] = []

    @deprecate.arguments('source', 'timestamp', 'check')
    def __init__(self, resources: typing.Mapping, metadata: metadata_base.DataMetadata = None, *,
                 load_lazy: typing.Callable[['Dataset'], None] = None, generate_metadata: bool = True,
                 check: bool = True, source: typing.Any = None, timestamp: datetime.datetime = None) -> None:
        super().__init__(resources)

        if isinstance(resources, Dataset) and metadata is None:
            # We made a copy, so we do not have to generate metadata.
            self.metadata = resources.metadata.set_for_value(self, generate_metadata=False)
        elif metadata is not None:
            # We were provided metadata, so we do not have to generate metadata.
            self.metadata = metadata.set_for_value(self, generate_metadata=False)
        else:
            self.metadata = metadata_base.DataMetadata(for_value=self, generate_metadata=generate_metadata)

        self._load_lazy = load_lazy

    @classmethod
    def load(cls, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None, lazy: bool = False,
             compute_digest: ComputeDigest = ComputeDigest.ONLY_IF_MISSING, strict_digest: bool = False, merge_score_targets: bool = True) -> 'Dataset':
        """
        Tries to load dataset from ``dataset_uri`` using all registered dataset loaders.

        Parameters
        ----------
        dataset_uri : str
            A URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.
        lazy : bool
            If ``True``, load only top-level metadata and not whole dataset.
        compute_digest : ComputeDigest
            Compute a digest over the data?
        strict_digest : bool
            If computed digest does not match the one provided in metadata, raise an exception?
        merge_score_targets : bool
            If a scoring dataset has target values in a separate file, merge them in?

        Returns
        -------
        Dataset
            A loaded dataset.
        """

        for loader in cls.loaders:
            if loader.can_load(dataset_uri):
                return loader.load(
                    dataset_uri, dataset_id=dataset_id, dataset_version=dataset_version, dataset_name=dataset_name,
                    lazy=lazy, compute_digest=compute_digest, strict_digest=strict_digest, merge_score_targets=merge_score_targets,
                )

        raise exceptions.DatasetUriNotSupportedError("No known loader could load dataset from '{dataset_uri}'.".format(dataset_uri=dataset_uri))

    def save(self, dataset_uri: str, *, resource_id: str = None) -> None:
        """
        Tries to save dataset to ``dataset_uri`` using all registered dataset savers.

        Parameters
        ----------
        dataset_uri : str
            A URI to save to.
        resource_id : str
            Save only resource with this ID. Some savers might not support saving datasets with multiple resources.
        """

        for saver in self.savers:
            if saver.can_save(dataset_uri):
                saver.save(self, dataset_uri, resource_id=resource_id)
                return

        raise exceptions.DatasetUriNotSupportedError("No known saver could save dataset to '{dataset_uri}'.".format(dataset_uri=dataset_uri))

    def is_lazy(self) -> bool:
        """
        Return whether this dataset instance is lazy and not all data has been loaded.

        Returns
        -------
        bool
            ``True`` if this dataset instance is lazy.
        """

        return self._load_lazy is not None

    def load_lazy(self) -> None:
        """
        Read all the data and convert the dataset to a non-lazy one.
        """

        if self._load_lazy is not None:
            self._load_lazy(self)

    # TODO: Allow one to specify priority which would then insert loader at a different place and not at the end?
    @classmethod
    def register_loader(cls, loader: Loader) -> None:
        """
        Registers a new dataset loader.

        Parameters
        ----------
        loader : Loader
            An instance of the loader class implementing a new loader.
        """

        cls.loaders.append(loader)

    # TODO: Allow one to specify priority which would then insert saver at a different place and not at the end?
    @classmethod
    def register_saver(cls, saver: Saver) -> None:
        """
        Registers a new dataset saver.

        Parameters
        ----------
        saver : Saver
            An instance of the saver class implementing a new saver.
        """

        cls.savers.append(saver)

    def __repr__(self) -> str:
        return self.__str__()

    def _get_description_keys(self) -> typing.Sequence[str]:
        return 'id', 'name', 'location_uris'

    def __str__(self) -> str:
        metadata = self.metadata.query(())

        return '{class_name}({description})'.format(
            class_name=type(self).__name__,
            description=', '.join('{key}=\'{value}\''.format(key=key, value=metadata[key]) for key in self._get_description_keys() if key in metadata),
        )

    def copy(self: D) -> D:
        # Metadata is copied from provided iterable.
        return type(self)(resources=self, load_lazy=self._load_lazy)

    def __copy__(self: D) -> D:
        return self.copy()


def dataset_serializer(obj: Dataset) -> dict:
    data = {
        'metadata': obj.metadata,
        'dataset': dict(obj),
    }

    if type(obj) is not Dataset:
        data['type'] = type(obj)

    return data


def dataset_deserializer(data: dict) -> Dataset:
    dataset = data.get('type', Dataset)(data['dataset'], data['metadata'])
    return dataset


if pyarrow_lib is not None:
    pyarrow_lib._default_serialization_context.register_type(
        Dataset, 'd3m.dataset',
        custom_serializer=dataset_serializer,
        custom_deserializer=dataset_deserializer,
    )


def main() -> None:
    logging.basicConfig()

    for dataset_file_path in sys.argv[1:]:
        try:
            dataset = Dataset.load('file://{dataset_doc_path}'.format(dataset_doc_path=os.path.abspath(dataset_file_path)))
            pprint.pprint(dataset)
            dataset.metadata.pretty_print()
        except Exception as error:
            raise Exception("Unable to load dataset: {dataset_doc_path}".format(dataset_doc_path=dataset_file_path)) from error


if __name__ == '__main__':
    main()
