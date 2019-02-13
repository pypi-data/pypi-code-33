# Copyright (c) 2012-2014 Kapiche Limited
# Author: Kris Rogers <kris@kapiche.com>, Ryan Stuart <ryan@kapiche.com>
"""
An index represents a collection of documents and associated information about those documents. When a document is added
to an index using an :class:`.IndexWriter`, some or all of its fields will be analysed
(see :mod:`caterpillar.processing.schema`) and information about those fields stored in various sub-indexes.
Caterpillar stores a number of sub-indexes:

* The frequencies index::
    {
        "term": count,
        "term": count,
        ...
    }
* The positions index (an inverted text index)::
    {
        "term": {
            "frame_id": [(start, end), (start, end)],
            ...
        },
        ...
    }
* The associations index::
    {
        term: {
            other_term: count,
            ...
        },
        ...
    }

Documents can be added to an index using an :class:`.IndexWriter`. Data can be read from an index using
:class:`.IndexReader`. There can only ever be one ``IndexWriter`` active per index. There can be an unlimited number of
``IndexReader``s active per index.

The type of index stored by caterpillar is different from those stored by regular information retrieval libraries (like
Lucene for example). Caterpillar is designed for text analytics as well as information retrieval. One side affect of
this is that caterpillar breaks documents down into *frames*. Breaking documents down into smaller parts (or context
blocks) enables users to implement their own statistical methods for analysing text. Frames are a configurable
component. See :class:`.IndexWriter` for more information.

Here is a quick example:

    >>> from caterpillar.processing import index
    >>> from caterpillar.processing import schema
    >>> from caterpillar.storage.sqlite import SqliteStorage
    >>> config = index.IndexConfig(SqliteStorage, schema.Schema(text=schema.TEXT))
    >>> with index.IndexWriter('/tmp/test_index', config) as writer:
    ...     writer.add_document(text="This is my text")...
    >>> with index.IndexReader('/tmp/test_index') as reader:
    ...     reader.get_document_count()
    ...
    1

"""

from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
import logging
import os
import pickle
import math
import json

import nltk

from .analysis.tokenize import ParagraphTokenizer, Token
from caterpillar.locking import PIDLockFile, LockTimeout, AlreadyLocked
from caterpillar.storage import StorageNotFoundError, SchemaMismatchError
from caterpillar import __version__ as version


logger = logging.getLogger(__name__)


class CaterpillarIndexError(Exception):
    """Common base class for index errors."""


class DocumentNotFoundError(CaterpillarIndexError):
    """No document by that name exists."""


class SettingNotFoundError(CaterpillarIndexError):
    """No setting by that name exists."""


class IndexNotFoundError(CaterpillarIndexError):
    """No index exists at specified location."""


class TermNotFoundError(CaterpillarIndexError):
    """Term doesn't exist in index."""


class IndexWriteLockedError(CaterpillarIndexError):
    """There is already an existing writer for this index."""


class NonIndexedFieldError(ValueError):
    """The field is not a searchable indexed field. """


class UnknownFieldError(ValueError):
    """The field is not defined on the index. """


class UnsupportedOperatorError(ValueError):
    """The operator is not supported for the given field."""


class NonSearchableOperatorError(ValueError):
    """The operator is valid for the field, but not supported for search."""


class IndexConfig(object):
    """
    Stores configuration information about an index.

    This object is a core part of any index. It is serialised and stored with every index so that an index can be
    opened. It tells an :class:`IndexWriter` and :class:`IndexReader` what type of storage class to use via
    ``storage_cls`` (must be a subclass of :class:`Storage <caterpillar.storage.Storage>`) and structure of the index
    via ``schema`` (an instance of :class:`Schema <caterpillar.processing.schema.Schema>`).

    In the interest of future proofing this object, it will also store a ``version`` number with itself so that
    older/new version have the best possible chance at opening indexes.

    This class might be extended later to store other things.

    """

    def __init__(self, storage_cls, schema):
        self._storage_reader_cls = storage_cls.reader
        self._storage_writer_cls = storage_cls.writer
        self._schema = schema
        self._version = version

    @property
    def storage_reader_cls(self):
        return self._storage_reader_cls

    @property
    def storage_writer_cls(self):
        return self._storage_writer_cls

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, schema):
        self._schema = schema

    @property
    def version(self):
        return self._version

    @staticmethod
    def loads(data):
        """
        Create an instance of this class from a string generated via :meth:`.dumps`.

        Raises :exc:`ValueError` if the ``data`` (str) can't be parsed into an instance of ``IndexConfig``.

        """

        # Note: this is mostly a horrible hack to bridge Python 2 and Python 3 schema formats
        # Mostly we are working around the horribleness of pickle as a long term persistence mechanism, at the same
        # time as we deal with Python 2 and 3 compatability. Eventually we will refactor this entire thing, and
        # explicitly store data representing the schema, not the schema objects directly.
        try:  # This is the Python 3 happy path
            instance = pickle.loads(data)
            if not isinstance(instance, IndexConfig):
                raise TypeError('The pickled object was not an IndexConfig object')
        except UnicodeDecodeError:
            try:
                from caterpillar.processing.schema import Schema
                from caterpillar.storage.sqlite import SqliteStorage
                # We will end up here when we attempt to decode Python2 stored pickles. So what we're going
                # to instead is restore the attributes, and reconstruct the original schema with Python3 objects.
                # This is a bit of a hack, and assumes that we have no customised analysers anywhere.
                instance = pickle.loads(data, encoding='bytes')
                if not isinstance(instance, IndexConfig):  # pragma: no cover
                    raise TypeError('The pickled object was not an IndexConfig object')
                # We will inspect the _fields of the unpickled object's schema, and use that to recrete a working object
                schema_fields = instance.__dict__[b'_schema'].__dict__[b'_fields']
                field_types_params = {
                    key.decode('utf-8') if isinstance(key, bytes) else key: type(field)(
                        stored=field.__dict__[b'_stored'], indexed=field.__dict__[b'_indexed']
                    )
                    for key, field in schema_fields.items()
                }
                this_schema = Schema(**field_types_params)
                instance = IndexConfig(SqliteStorage, this_schema)
            except Exception:  # pragma: no cover
                raise ValueError('The passed data couldn\'t be parsed.')

        except Exception:
            raise ValueError('The passed data couldn\'t be parsed.')

        return instance

    def dumps(self):
        """Dump this instance as a string for serialization."""
        return pickle.dumps(self)


class IndexWriter(object):

    """
    Write to an existing index or create a new index and write to it.

    An instance of an ``IndexWriter`` represents a transaction. To begin the transaction, you need to call
    :meth:`.begin` on this writer. There can only be one active IndexWriter transaction per index. This is enforced
    via a write lock on the index. When you begin the write transaction the IndexWriter instance tries to acquire the
    write lock. By default it will block indefinitely until it gets the write lock but this can be overridden using the
    ``timeout`` argument to `begin()`. If `begin()` times-out when trying to get a lock, then
    :exc:`IndexWriteLockedError` is raised.

    Once you have performed all the writes/deletes you like you need to call :meth:`.commit` to finalise the
    transaction. Alternatively, if there was a problem during your transaction, you can call :meth:`.rollback` instead
    to revert any changes you made using this writer. **IMPORTANT** - Finally, you need to call :meth:`.close` to
    release the lock.

    Using IndexWriter this way should look something like this:

        >>> writer = IndexWriter('/some/path/to/an/index')
        >>> try:
        ...     writer.begin(timeout=2)  # timeout in 2 seconds
        ...     # Do stuff, like add_document() etc...
        ...     writer.commit()  # Write the changes...
        ... except IndexWriteLockedError:
        ...     # Do something else, maybe try again
        ... except SomeOtherException:
        ...     writer.rollback()  # Error occurred, undo our changes
        ... finally:
        ...     writer.close()  # Release lock

    This class is also a context manager and so can be used via the with statement. **HOWEVER**, be aware that using
    this class in a context manager will block indefinitely until the lock becomes available. Using the context manager
    has the added benefit of calling ``commit()``/``rollback()`` (if an exception breaks the context) and ``close()`` \
    for you automatically::

        >>> writer = IndexWriter('/some/path/to/a/index')
        >>> with writer:
        ...     add_document(field="value")

    Again, be warned that this will block until the write lock becomes available!

    Finally, pay particular attention to the ``frame_size`` arguments of :meth:`.add_document`. This determines the size
    of the frames the document will be broken up into.

    """

    # Where is the config?
    CONFIG_FILE = "index.config"

    def __init__(self, path, config=None, auto_migrate=True):
        """
        Open an existing index for writing or create a new index for writing.

        If ``path`` (str) doesn't exist and ``config`` is not None, then a new index will created when :meth:`begin` is
        called (after the lock is acquired). Otherwise, :exc:`IndexNotFoundError` is raised.

        If present, ``config`` (IndexConfig) must be an instance of :class:`IndexConfig`.

        """
        self.auto_migrate = auto_migrate
        self._path = path
        if not config and not os.path.exists(path):
            # Index path doesn't exist and no schema passed
            raise IndexNotFoundError('No index exists at {}'.format(path))
        elif config and not os.path.exists(path):
            # Index doesn't exist. Delay creating until we have the lock in begin().
            self.__config = config
            self.__schema = config.schema
            self.__storage = None
        else:
            # Fetch the config
            with open(os.path.join(path, IndexWriter.CONFIG_FILE), 'rb') as f:
                self.__config = IndexConfig.loads(f.read())
            self.__storage = self.__config.storage_writer_cls(path, create=False)
            self.__schema = self.__config.schema
            self.__lock = None  # Should declare in __init__ and not outside.
        self.__committed = False

        # Attribute to store the details of the most recent commit
        self.last_committed_documents = []
        self.last_deleted_documents = []
        self.last_updated_plugins = []

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

    def begin(self, timeout=None):
        """
        Acquire the write lock and begin the transaction.

        If this index has yet to be created, create it (folder and storage). If ``timeout``(int) is omitted (or None),
        wait forever trying to lock the file. If ``timeout`` > 0, try to acquire the lock for that many seconds. If the
        lock period expires and the lock hasn't been acquired raise :exc:`IndexWriteLockedError`. If timeout <= 0,
        raise :exc:`IndexWriteLockedError` immediately if the lock can't be acquired.

        """
        created = os.path.exists(self._path)
        if not created:
            os.makedirs(self._path)
        self.__lock = PIDLockFile(os.path.join(self._path, 'writer'))
        try:
            self.__lock.acquire(timeout=timeout)
        except (AlreadyLocked, LockTimeout):
            raise IndexWriteLockedError('Index {} is locked for writing'.format(self._path))
        else:
            logger.debug("Index write lock acquired for {}".format(self._path))
            if not created:
                # Store config
                with open(os.path.join(self._path, IndexWriter.CONFIG_FILE), 'wb') as f:
                    f.write(self.__config.dumps())
                # Initialize storage
                storage = self.__config.storage_writer_cls(self._path, create=True)

                # Initialise our fields:
                storage.begin()

                storage.add_unstructured_fields([''])  # Metadata hack until we have document search
                storage.add_unstructured_fields(self.__schema.get_indexed_text_fields())
                storage.add_structured_fields(self.__schema.get_indexed_structured_fields())

                storage.commit()

            if not self.__storage:
                # This is a create or the index was created after this writer was opened.
                self.__storage = self.__config.storage_writer_cls(self._path, create=False)

            try:
                self.__storage.begin()

            except SchemaMismatchError:
                if self.auto_migrate:
                    try:
                        self.__storage.migrate()
                        self.__storage.begin()
                    except Exception:
                        self.__lock.release()
                        raise
                else:
                    self.__lock.release()
                    raise

    def commit(self):
        """Commit changes made by this writer by calling :meth:``commit()`` on the storage instance."""
        self.last_committed_documents, self.last_deleted_documents, self.last_updated_plugins = self.__storage.commit()
        self.__committed = True

    def rollback(self):
        """Rollback any changes made by this writer."""
        self.__storage.rollback()
        self.__committed = True

    def close(self):
        """
        Close this writer.

        Calls :meth:`.rollback` if we are in the middle of a transaction.

        """
        # Do we need to rollback?
        if not self.__committed:
            logger.info('IndexWriter transaction wasn\'t committed, rolling back....')
            self.rollback()

        # Close the storage connection
        self.__storage.close()
        self.__storage = None
        logger.debug("Releasing index write lock for {}....".format(self._path))
        self.__lock.release()

    def add_document(self, frame_size=2, **fields):
        """
        Add a document to this index.

        We index :class:`TEXT <caterpillar.schema.TEXT>` fields by breaking them into frames for analysis. The
        ``frame_size`` (int) param controls the size of those frames. Setting ``frame_size`` to an int < 1 will result
        in all text being put into one frame or, to put it another way, the text not being broken up into frames.

        .. note::
            Because we always store a full positional index with each index, we are still able to do document level
            searches like TF/IDF even though we have broken the text down into frames. So, don't fret!

        ``**fields`` is the fields and their values for this document. Calling this method will look something like
        this::

            >>> writer.add_document(field1=value1, field2=value2).

        Any unrecognized fields are just ignored.

        Raises :exc:`TypeError` if something other then str or bytes is given for a TEXT field and :exec:`IndexError`
        if there are any problems decoding a field. All string objects are assumed to be unicode.

        ..Warning:
            This interface is expected to change in the future: The schema object will become responsible for handling
            all document processing and analysis coordination, including error handling. This function will simply
            become a central entry API for coordinating schema, document analysis and storage objects.

        Documents are assigned an ID only at commit time. the attribute ``last_committed_documents`` of the
        writer contains the ID's of the documents added in the last completed write transaction for that
        writer.

        """
        logger.debug('Adding document')
        schema_fields = self.__schema.items()
        sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        # Build the frames by performing required analysis.
        frames = {}  # Frame data:: field_name -> [frame1, frame2, frame3]
        term_positions = {}  # Token streams

        metadata = {}  # Inverted frame metadata:: field_name -> field_value

        # Shell frame includes all non-indexed and categorical fields
        shell_frame = {}
        for field_name, field in schema_fields:
            if (not field.indexed or field.categorical) and field.stored and field_name in fields:
                shell_frame[field_name] = fields[field_name]

        # Tokenize fields that need it
        logger.debug('Starting tokenization of document')

        # Analyze document level structured fields separately to inject in the frames.
        for field_name, field in schema_fields:

            if field_name not in fields or fields[field_name] is None \
                    or not field.indexed or not field.categorical:
                # Skip fields not supplied or with empty values for this document.
                continue

            # Record categorical values
            for token in field.analyse(fields[field_name]):
                metadata[field_name] = token.value

        # Now just the unstructured fields
        for field_name, field in schema_fields:

            if field_name not in fields or fields[field_name] is None \
                    or not field.indexed or field.categorical:
                continue

            # Start the index for this field
            frames[field_name] = []
            term_positions[field_name] = []

            # Index non-categorical fields
            field_data = fields[field_name]

            if frame_size > 0:
                # Break up into paragraphs
                paragraphs = ParagraphTokenizer().tokenize(field_data)
            else:
                # Otherwise, the whole document is considered as one paragraph
                paragraphs = [Token(field_data)]

            # Per field counter of the number of frames.
            sequence = 0

            for paragraph in paragraphs:
                # Next we need the sentences grouped by frame
                if frame_size > 0:
                    sentences = sentence_tokenizer.tokenize(paragraph.value, realign_boundaries=True)
                    sentences_by_frames = [sentences[i:i + frame_size] for i in range(0, len(sentences), frame_size)]
                else:
                    sentences_by_frames = [[paragraph.value]]

                for sentence_list in sentences_by_frames:

                    # Build our frames
                    frame = {
                        '_field': field_name,
                        '_positions': {},
                        '_sequence_number': sequence,
                    }
                    frame.update(shell_frame)

                    if field.stored:
                        frame['_text'] = " ".join(sentence_list)

                    token_stream = [
                        token.value for sentence in sentence_list for token in field.analyse(sentence)
                        if not token.stopped
                    ]

                    # Serialised representation of the frame
                    frames[field_name].append(json.dumps(frame))

                    # Tokenised data for the storage engine
                    term_positions[field_name].append(token_stream)

                    sequence += 1

        # Finally add the document to storage.
        doc_fields = {}

        for field_name, field in schema_fields:
            if field.stored and field_name in fields:
                # Only record stored fields against the document
                doc_fields[field_name] = fields[field_name]

        document = json.dumps(doc_fields)

        self.__storage.add_analyzed_document('v1', (document, metadata, frames, term_positions))

        logger.debug('Tokenization of document complete. {} frames staged for storage.'.format(len(frames)))

    def append_frame_attributes(self, attribute_index):
        """
        Append new attributes to existing frames or documents.

        Currently only 1:1 attributes are supported for a frame.

        Currently only datatypes understood by SQLite are supported (numerical,
        text, bytes and None).

        Data format:
            {
                frame_id: {attribute_type: attribute_value}
            }

        """
        self.__storage.append_frame_attributes(attribute_index)

    def delete_document(self, document_id):
        """
        Delete the document with given ``document_id`` (str).

        If the document does not exist, no error will be raised. The ``IndexWriter`` attribute
        ``last_deleted_documents`` contains the ID's of documents that were present in the
        index and deleted during the last transaction.


        """
        self.__storage.delete_documents([document_id])

    def set_plugin_state(self, plugin):
        """ Write the state of the given plugin to the index.

        Any existing state for this plugin instance will be overwritten.

        The ID's of updated plugins are available in the last_updated_plugins attribute of the
        IndexWriter after the transaction is committed.

        """
        # low level calls to plugin storage subsystem.
        self.__storage.set_plugin_state(
            plugin.get_type(), plugin.get_settings(), plugin.get_state()
        )

    def delete_plugin_instance(self, plugin):
        """
        Delete the state corresponding to the given plugin instance.

        """
        self.__storage.delete_plugin_state(plugin.get_type(), plugin_settings=plugin.get_settings())

    def delete_plugin_type(self, plugin_type):
        """
        Delete all plugins and corresponding data of the specified ``plugin_type``.

        """
        self.__storage.delete_plugin_state(plugin_type)

    def add_fields(self, **fields):
        """
        Add new fields to the schema.

        All keyword arguments are treated as ``(field_name, field_type)`` pairs.

        """
        for field_name, field in fields.items():
            self.__schema.add(field_name, field)
            if field_name in self.__schema.get_indexed_text_fields():
                self.__storage.add_unstructured_fields([field_name])
            if field_name in self.__schema.get_indexed_structured_fields():
                self.__storage.add_structured_fields([field_name])

        self.__config.schema = self.__schema
        # Save updated schema
        with open(os.path.join(self._path, IndexWriter.CONFIG_FILE), 'wb') as f:
            f.write(self.__config.dumps())

    def set_setting(self, name, value):
        """Set the setting identified by ``name`` to ``value``."""
        self.__storage.set_setting(name, value)


class IndexReader(object):

    """
    Read information from an existing index.

    Once an IndexReader is opened, it will **not** see any changes written to the index by an :class:`IndexWriter`. To
    see any new changes you must open a new IndexReader.

    To search an index, use :meth:`.searcher` to fetch an :class:`caterpillar.searching.IndexSearcher` instance to
    execute the search with. A searcher will only work while this IndexReader remains open.

    Access to the raw underlying associations, frequencies and positions index is provided by this class but a caller
    needs to be aware that these may consume a **LARGE** amount of memory depending on the size of the index. As such,
    all access to these indexes are provided by generators (see :meth:`.get_frames` for example).

    Once you are finished with an IndexReader you need to call the :meth:`.close` method.

    IndexReader is a context manager and can be used via the with statement to make this easier. For example::

        >>> with IndexReader('/path/to/index') as r:
        ...    # Do stuff
        ...    doc = r.get_document(d_id)
        >>> # Reader is closed

    .. warning::
        While opening an IndexReader is quite cheap, it definitely isn't free. If you are going to do a large amount of
        reading over a relatively short time span, it is much better to do so using one reader.

    There is no limit to the number of IndexReader objects which can be active on an index. IndexReader objects are also
    thread-safe.

    IndexReader doesn't cache any data. Every time you ask for data, the underlying :class:`caterpillar.storage.Storage`
    instance is used to fetch that data. If you were to call :meth:`,get_associations_index` 10 times, each time the
    data will be fetched from the storage instance and not some internal cache. The underlying storage instance may do
    some of it's own caching but that is transparent to us.

    """

    def __init__(self, path, auto_migrate=True):
        """
        Open a new IndexReader for the index at ``path`` (str).

        This constructor only creates the instance. Before you start reading you need to call :meth:`.begin` which is
        automatically called via :meth:`.__enter__`.

        If `auto_migrate` is True, then the underlying index will be automatically migrated to a newer version if it is
        not the appropriate schema version.

        """
        self.__path = path
        self.auto_migrate = auto_migrate

        try:
            with open(os.path.join(path, IndexWriter.CONFIG_FILE), "rb") as f:
                self.__config = IndexConfig.loads(f.read())
            self.__storage = self.__config.storage_reader_cls(path)
        except StorageNotFoundError:
            logger.exception("Couldn't open storage for {}".format(path))
            raise IndexNotFoundError("Couldn't find an index at {} (no storage)".format(path))
        except IOError:
            logger.exception("Couldn't read index config for {}".format(path))
            raise IndexNotFoundError("Couldn't find an index at {} (no config)".format(path))
        else:
            self.__schema = self.__config.schema

    @property
    def revision(self):
        return self.__storage.revision

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def begin(self):
        """
        Begin reading with this IndexReader.

        From this point on, no changes to the underlying index made by an :class:`IndexWriter` will be seen.

        .. warning::
            This method **must** be called before any reading can be done.

        """
        try:
            self.__storage.begin()
        except SchemaMismatchError:
            if self.auto_migrate:
                # Open the writer to perform the actual migration.
                with IndexWriter(self.__path):
                    pass
                self.__storage.begin()
            else:
                raise

    def close(self):
        """
        Release all resources used by this IndexReader.

        Calling this method renders this instance unusable.

        """
        self.__storage.commit()
        self.__storage.close()

    def get_positions_index(self, field):
        """
        Get all term positions for the given indexed text field.

        This is a generator which yields a key/value pair tuple.

        This is what is known as an inverted text index. Structure is as follows::

            {
                "term": {
                    "frame_id": [(start, end), (start, end)],
                    ...
                },
                ...
            }

        """
        return self.__storage.iterate_positions(include_fields=[field])

    def get_term_positions(self, term, field):
        """
        Returns a dict of term positions for ``term`` (str).

        Structure of returned dict is as follows::

        {
            frame_id1: [(start, end), (start, end)],
            frame_id2: [(start, end), (start, end)],
            ...
        }

        """
        try:
            positions = next(self.__storage.iterate_positions(terms=[term], include_fields=[field]))
            return positions[1]
        except StopIteration:
            raise KeyError('"{}" not found in field "{}"'.format(term, field))

    def get_frequencies(self, field):
        """
        Term frequencies for this index.

        Be aware that a terms frequency is only incremented by 1 per frame no matter the frequency within that
        frame. The format is as follows::

            {
                term: count
            }

        This method is a generator that yields key/value paris of tuples (term, count).

        .. note::
            If you want to get the term frequency at a document level rather then a frame level then you should count
            all of the terms positions returned by :meth:`.get_term_position`.

        """
        return self.__storage.iterate_term_frequencies(include_fields=[field])

    def get_term_frequency(self, term, field):
        """Return the frequency of ``term`` (str) as an int."""
        try:
            frequency = next(self.__storage.iterate_term_frequencies(terms=[term], include_fields=[field]))
            return frequency[1]
        except StopIteration:
            raise KeyError('"{}" not found in field "{}"'.format(term, field))

    def get_frame_count(self, field):
        """Return the int count of frames stored on this index."""
        return self.__storage.count_frames(include_fields=[field])

    def get_frame(self, frame_id):
        """Get a single frame by id, raising a DocumentNotFound exception if not present. """
        frames = list(self.get_frames(frame_ids=[frame_id]))

        if frames:
            frame_id, frame = frames[0]
            return frame

        else:
            raise DocumentNotFoundError("No frame '{}'".format(frame_id))

    def get_frames(self, include_fields=None, exclude_fields=None, frame_ids=None):
        """
        Generator across frames from this field in this index.

        If present, the returned frames will be restricted to those with ids in ``frame_ids`` (list). The field
        argument will be ignored if frame_ids are provided.
        Format of theframes index data is as follows::

            {
                frame_id: { //framed data },
                frame_id: { //framed data },
                frame_id: { //framed data },
                ...
            }

        This method is a generator that yields tuples of frame_id and frame data dict.

        """
        for row in self.__storage.iterate_frames(
            frame_ids=frame_ids, include_fields=include_fields, exclude_fields=exclude_fields
        ):
            frame = json.loads(row[4])
            frame.update(_id=row[0], _doc_id=row[1])
            frame['_attributes'] = {key: value for _, key, value in self.__storage.iterate_frame_attributes([row[0]])}
            yield row[0], frame

    def get_frame_ids(self, field):
        """Generator of ids for all frames stored on this index."""
        for row in self.__storage.iterate_frames(include_fields=[field]):
            yield row[0]

    def get_document(self, document_id):
        """Returns the document with the given ``document_id`` (str) as a dict."""
        try:
            document = next(self.__storage.iterate_documents([document_id]))
            # inject _id field
            doc = json.loads(document[1])
            doc['_id'] = document[0]
            return doc

        except StopIteration:
            raise DocumentNotFoundError("No document '{}'".format(document_id))

    def get_document_count(self):
        """Returns the int count of documents added to this index."""
        return self.__storage.count_documents()

    def get_documents(self, document_ids=None):
        """
        Generator that yields documents from this index as (id, data) tuples.

        If present, the returned documents will be restricted to those with ids in ``document_ids`` (list).

        """
        return (
            (doc_id, json.loads(document))
            for doc_id, document in self.__storage.iterate_documents(document_ids=document_ids)
        )

    def get_metadata(
        self, include_fields=None, exclude_fields=None, structured_fields=None, return_documents=False,
        pagination_key=None, upper_pagination_key=None
    ):
        """
        Return the entire metadata index.

        This method returns an inverted index that shows
        which frames or documents have a particular metadata field and the
        value of that that metadata field.


            (
                "attribute_name", {
                    "value": ["frame_id1", "frame_id2"],
                    "value": ["frame_id3"],
                    "value": ["frame_id4", "frame_id5", ..., "frame_idn"],
                    ...
                }
            )

        include_fields: list of unstructured fields to include in the analysis.
            By default this is None, and all fields are included if exclude_fields is also None.

        exclude_fields: list of unstructured fields to exclude from the analysis.
            If include_fields is not None, this argument is ignored.

        structured_fields: optional list of structured fields to iterate through. If this is not specified,
            all structured fields present in the index will be iterated through.

        return_documents: if True, return document_ids rather than frames. Note that the include_fields
            arguments will be ignored if this is True.

        pagination_key | upper_pagination_key: The minimum and maximum frame or document id to return..

        """
        metadata = self.__storage.iterate_metadata(
            include_fields=include_fields, exclude_fields=exclude_fields, return_documents=return_documents,
            pagination_key=pagination_key, upper_pagination_key=upper_pagination_key
        )

        results = defaultdict(_default_dict_list)

        for field, value, match_id in metadata:
            results[field][value].append(match_id)

        return results

    def get_attributes(
        self, include_fields=None, exclude_fields=None, return_documents=False,
        pagination_key=None, upper_pagination_key=None
    ):
        """
        Return entire attribute index for either frames or documents.

        This method returns an inverted index that shows
        which frames or documents have a particular attribute and the value of
        that that attribute. A tuple of the attribute_name and the
        corresponding values: frame_ids mapping is yielded on every iteration:

            (
                "attribute_name", {
                    "value": ["frame_id1", "frame_id2"],
                    "value": ["frame_id3"],
                    "value": ["frame_id4", "frame_id5", ..., "frame_idn"],
                    ...
                }
            )


        Args

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.

            return_documents: if True, return documents with any frame matching that attribute-value
                paid. Default is False. Because attributes correspond to the properties of an
                individual frame, the resulting index needs to be interpreted with care.

            pagination_key | upper_pagination_key: The minimum and maximum frame or document id to return.

        """
        attributes = self.__storage.iterate_attributes(
            include_fields=include_fields, exclude_fields=exclude_fields, return_documents=return_documents,
            pagination_key=pagination_key, upper_pagination_key=upper_pagination_key
        )

        results = defaultdict(_default_dict_list)

        for attribute, value, match_id in attributes:
            results[attribute][value].append(match_id)

        return results

    def get_schema(self):
        """Get the :class:`caterpillar.processing.schema.Schema` for this index."""
        return self.__schema

    def get_revision(self):
        """
        Return the str revision identifier for this index.

        The revision identifier is a version identifier. It gets updated every time the index gets changed.

        """
        return self.__storage.revision

    def get_vocab_size(self, field):
        """
        Get total number of unique terms identified for the specified field in this index (int).

        Note that terms may be shared across fields, so the sum of the vocab_size in each field will
        overcount the number of terms.

        """
        return self.__storage.count_vocabulary(include_fields=[field])

    def get_setting(self, name):
        """Get the setting identified by ``name`` (str)."""
        setting_dict = self.__storage.get_settings([name]).fetchone()
        if setting_dict is None:
            raise SettingNotFoundError("No setting '{}'".format(name))
        else:
            return setting_dict[1]

    def get_settings(self, names):
        """
        A generator of all settings listed in ``names`` (list).

        Names that are not stored in the index are not included in the returned dictionary.

            {
                name: value,
                name: value,
                ...
            }

        """
        return self.__storage.get_settings(names)

    def get_plugin_state(self, plugin):
        """
        Returns the state of the given plugin stored in the index.

        """
        return dict(self.__storage.get_plugin_state(plugin.get_type(), plugin.get_settings()))

    def get_plugin_by_id(self, plugin_id):
        """
        Returns the plugin_type, settings and state corresponding to the given plugin_id.

        """
        plugin_type, settings, state = self.__storage.get_plugin_by_id(plugin_id)
        return plugin_type, settings, dict(state)

    def get_case_fold_terms(self, include_fields=None, exclude_fields=None, merge_threshold=0.7):
        """Suggest case normalised variations on terms.

        Operates across all fields in the corpus.

        """
        # Merge frequencies across all fields specified
        # Note that this requires loading all of the vocabulary into main memory and should be used
        # with care on extremely large vocabularies. Across 1.4 million terms in Simple Wikipedia
        # this takes about 4 seconds and consumes ~150MB of memory.
        frequencies_index = {
            term: freq for term, freq in self.__storage.iterate_term_frequencies(
                include_fields=include_fields, exclude_fields=exclude_fields
            )
        }

        normalise_variants = []

        for w, freq in frequencies_index.items():
            if w.islower() and w.title() in frequencies_index:
                freq_name = frequencies_index[w.title()]

                if freq / freq_name < merge_threshold:
                    # Merge into name
                    normalise_variants.append((w, w.title()))

                elif freq_name / freq < merge_threshold:
                    # Merge into word
                    normalise_variants.append((w.title(), w))

        return normalise_variants

    def list_plugins(self):
        """
        List all plugin instances that have been stored in this index.
        """
        return self.__storage.list_known_plugins()

    def detect_significant_ngrams(
        self, min_count=5, threshold=40, include_fields=None, exclude_fields=None, npmi_threshold=None
    ):
        """
        Find significant n-grams within the index.

        Args

            min_count: the minimum number of frames a bigram must occur in to be considered

            threshold: the minimum score to be considered a significant n-gram

            npmi_threshold: the minimum correlation between the two terms for
                            them to be considered as a significant n-gram

            include_fields, exclude_fields

        Returns

            bigrams: a list of tuples of tokens on the index in their positional order. For example:
                [('hot', 'apple', 'pie'), ('cream', 'cheese'), ('sweet', 'potato')]

        Notes

            - Currently only n=2 (bigram detection) is supported.
            - Frequency is counted by the number of frames a match occurs in, rather than the raw frequency.

        """
        if npmi_threshold is None:
            bigrams_return = []

            bigrams = list(self.__storage.find_significant_bigrams(
                include_fields=include_fields, exclude_fields=exclude_fields, min_count=min_count, threshold=threshold
            ))
            for bigram in bigrams:
                bigrams_return.append((bigram[0:2]))

        else:
            corpus_size = self.__storage.count_frames(
                include_fields=include_fields, exclude_fields=exclude_fields
            )
            bigrams = list(self.__storage.find_significant_bigrams(
                include_fields=include_fields, exclude_fields=exclude_fields, min_count=min_count, threshold=0
            ))

            bigrams_return = []

            for left_term, right_term, left_term_freq, right_term_freq, bigram_freq, score in bigrams:
                numerator = math.log(bigram_freq * corpus_size / (left_term_freq * right_term_freq))
                denominator = -math.log(bigram_freq / corpus_size)
                npmi_score = numerator / denominator
                if (npmi_score > npmi_threshold or score > threshold):
                    bigrams_return.append((left_term, right_term))

        return bigrams_return

    def get_term_frequency_vectors(self, frame_ids=None, include_fields=None, exclude_fields=None, weighting='tf'):
        """
        Iterate through term-frequency vectors for frames in this index.

        Args

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.

            frame_ids: an iterator of frame_ids to consider.
                If this is provided then both include_fields and exclude_fields are ignored.

            weighting: the weighting for each term.
                Currently only term-frequency ('tf') is supported.

        Returns

            Generator of (frame_id, {term1: frequency, term2: frequency}) tuples.

        """
        return self.__storage.iterate_term_frequency_vectors(
            weighting=weighting,
            include_fields=include_fields, exclude_fields=exclude_fields,
            frame_ids=frame_ids
        )

    def get_skipgrams(self, frame_ids=None, include_fields=None, exclude_fields=None, start_offset=1, end_offset=1):
        """
        Iterate through a sliding window of skipgrams/word cooccurrences within an index.

        Return tuples (`frame_id`, `left`, `right`) indicating that in `frame_id` the `right` token occurs between
        `start_offset` and `end_offset` positions after the `left` token.

        For example, if `start_offset` and `end_offset` are 1, then all bigrams are returned.

        For an index with a single frame like 'The dog sat down' and a `start_offset` of 1 and `end_offset` of 2, the
        following would be returned:
            [(1, The, dog), (1, The, sat), (1, dog, sat), (1, dog, down), (1, sat, down)]

        Args

            start_offset: default 1, an integer >= 1.
                The number of token positions to the right of a token to start considering matches. If this is > 1,
                words immediately adjacent will not be considered in the same neighbourhood.

            end_offset: default 1, an integer >= start_offset.
                The number of token positions to the right of a token to end considering matches.

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.

            frame_ids: an iterator of frame_ids to consider.
                If this is provided then both include_fields and exclude_fields are ignored.

        Returns

            Generator of (frame_id, left_token, right_token) tuples.

        """
        return self.__storage.iterate_skipgrams(
            frame_ids=frame_ids, include_fields=include_fields, exclude_fields=exclude_fields,
            start_offset=start_offset, end_offset=end_offset
        )

    def filter_range(
        self, include_fields=None, exclude_fields=None, pagination_key=0, end_key=None,
        limit=100, return_documents=False
    ):
        """
        Return all document or frame id's greater than pagination_key, up to the limit.

        By default returns the first 100 frames in an index, across all fields.

        All returned results have a score of 0 - this is not useful for ranked results. Combining with
        ranked queries gives nonsensical results.

        This method allows you to efficiently page through document or frame ids by the
        order they were added to the index.

        """

        results = self.__storage.filter_range(
            pagination_key, end=end_key, limit=limit, return_documents=return_documents,
            include_fields=include_fields, exclude_fields=exclude_fields
        )

        return {key[0]: [0] for key in results}

    def filter_and_rank(
        self, include_fields=None, exclude_fields=None, must=None, should=None, at_least_n=None, must_not=None,
        metadata=None, limit=100, pagination_key=None, return_documents=False, scoring='tf-idf', normalise_length=False
    ):
        """
        Search for frames or documents matching the given criteria.

        Args

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.

            must: list of terms
                All of these terms must be present in the frame/document to be counted as a match.

            should: list of terms
                Any of these terms may be present in the frame/document to be counted as a match.

            at_least_n: tuple of (integer n, list of terms)
                At least n of the terms in the list must be present in the frame/document to be counted as a match.

            must_not: list of terms
                If any of these terms are present in a frame/document, it will never be counted as a match.

            metadata: dictionary of tuples {metadata_field: (operator, value/s)}
                Only frames/documents matching all metadata operators will be included.
                Supported operators and the format for values depends on the definition of the metadata field
                in the schema. Metadata only queries are not supported for search.

            limit: integer, default 100.
                The maximum number of frames/documents to return.

            pagination_key: None, or tuple (score, frame_id | document_id)
                Restart a search at the given score cutoff and frame/document ID. Providing a pagination
                key avoids sorting and iterating through frames that have already been returned by a search.

            return_documents: True or False.
                If False (default), match the criteria and score on the level of individual frames. Otherwise
                search, score and return whole documents, aggregating frame scores by summing.

            scoring: string representing the scoring algorithm, default tf-idf
                Options are: 'tf, binarised-tf, tf-idf, binarised-tf-idf'

            normalise_length: default False.
                If True, normalise scores by frame lengths (the number of tokens in the frame). This is an approximation
                to full l2 normalisation for cosine distance.

        Returns

            scored: list of tuples in descending score order: [(frame_id | document_id, score), ...]
                The final element of the scored list is the pagination key to restart the search.

        Notes

            Documents are scored by aggregating the individual scores for matching frames in the document.

            Metadata only queries are not supported by search: at least one term must be present in the
            must, should or at_least_n arguments. The filter function can be used for metadata only queries.

            A sequence of terms can be provided as a list of variations wherever a single term is valid. For
            example: must=[('cat', 'dog'), 'pet'] will return documents that contain 'pet' and at least one of
            'cat' or 'dog'. This can be used for synonyms, term variants or other query expansion.

            Another example, a case invariant search for apple pie:
                must=[('Apple', 'apple', 'APPLE'), ('Pie', 'pie', 'PIE')]

        """
        # if metadata, but not unstructured data, raise an error for search.

        if metadata and not (must or should or at_least_n):
            raise ValueError('Metadata only ranking is not supported. Try IndexReader.filter() instead.')

        analysed_metadata = self._validate_analyse_metadata(metadata) if metadata else None

        results = self.__storage.rank_or_filter_unstructured(
            include_fields=include_fields, exclude_fields=exclude_fields,
            must=must, should=should, at_least_n=at_least_n, must_not=must_not,
            metadata=analysed_metadata, limit=limit, pagination_key=pagination_key, return_documents=return_documents,
            search=True, scoring=scoring, normalise_length=normalise_length
        )

        return list(results)

    def filter(
        self, include_fields=None, exclude_fields=None, must=None, should=None, at_least_n=None, must_not=None,
        metadata=None, limit=None, pagination_key=None, upper_pagination_key=None, return_documents=False,
        scoring='tf-idf', normalise_length=False
    ):
        """
        Filter for frames or documents matching the given criteria.

        Args

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.


            must: list of terms
                All of these terms must be present in the frame/document to be counted as a match.

            should: list of terms
                Any of these terms may be present in the frame/document to be counted as a match.

            at_least_n: tuple of (integer n, list of terms)
                At least n of the terms in the list must be present in the frame/document to be counted as a match.

            must_not: list of terms
                Of the frames/documents that match any of the must/should/at_least_n parameters remove those that
                also have these terms.
                must_not is ignored if none of must, should or at_least_n are populated.


            metadata: dictionary of tuples {metadata_field: (operator, value/s)}
                Only frames/documents matching all metadata operators will be included.
                Supported operators and the format for values depends on the definition of the metadata field
                in the schema.


            limit: integer, default 0.
                The maximum number of frames/documents to return. For filtering results are returned
                in batches corresponding to frame_id or document_id order.

            pagination_key: None, or a frame_id | document_id.
                Restart a filtering set at the given frame/document ID.

            upper_pagination_key: None, or a frame_id document_id.
                The maximum document or frame id to return from the query.

            return_documents: True or False.
                If False (default), match the criteria and score on the level of individual frames. Otherwise
                match and return documents.

            scoring: string representing the scoring algorithm, default tf-idf
                Options are: 'tf, binarised-tf, tf-idf, binarised-tf-idf'

            normalise_length: default False.
                If True, normalise scores by frame lengths (the number of tokens in the frame). This is an approximation
                to full l2 normalisation for cosine distance.

        Returns

            filtered_set: a dictionary of {frame_id | document_id: [score]}
                The score is 0 if only metadata is provided for the query.

        Notes

            Documents are scored by aggregating the individual scores for matching frames in the document.

            For term matches a tf-idf score is calculated during filtering, but results are not sorted: this allows
            ordering by score to be done after set intersection operations with other queries. Results can be paged
            through by frame or document_id with limit.

            A sequence of terms can be provided as a list of variations wherever a single term is valid. For
            example: must=[('cat', 'dog'), 'pet'] will return documents that contain 'pet' and at least one of
            'cat' or 'dog'. This can be used for synonyms, term variants or other query expansion.

            Another example, a case invariant search for apple pie:
                must=[('Apple', 'apple', 'APPLE'), ('Pie', 'pie', 'PIE')]


        """

        # Validate and analyze metadata fields.
        analysed_metadata = self._validate_analyse_metadata(metadata) if metadata else None

        # if metadata, but not unstructured data, dispatch to the optimised function
        if metadata and not (must or should or at_least_n):
            results = self.__storage.filter_metadata(
                analysed_metadata, return_documents=return_documents,
                include_fields=include_fields, exclude_fields=exclude_fields,
                limit=limit, pagination_key=pagination_key, upper_pagination_key=upper_pagination_key,
            )
            # Note that metadata only queries do not currently have a defined score.
            return {i[0]: [0] for i in results}

        else:
            results = self.__storage.rank_or_filter_unstructured(
                include_fields=include_fields, exclude_fields=exclude_fields,
                must=must, should=should, at_least_n=at_least_n, must_not=must_not,
                metadata=analysed_metadata, limit=limit, pagination_key=pagination_key,
                upper_pagination_key=upper_pagination_key, return_documents=return_documents, search=False,
                scoring=scoring, normalise_length=normalise_length
            )

            return {key: [score] for key, score in results}

    def filter_nonempty(self, include_fields=None, exclude_fields=None, pagination_key=None, upper_pagination_key=None):
        """
        Return frames that have at least one token generated at index time.

        This is the set of frames that are non-empty for the purposes of searching.

        Args

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.


            pagination_key: None, or a frame_id | document_id.
                Restart a filtering set at the given frame/document ID.

            upper_pagination_key: None, or a frame_id document_id.
                The maximum document or frame id to return from the query.

        Returns

            filtered_set: a dictionary of {frame_id | document_id: [score]}
                The score is 0 if only metadata is provided for the query.

        """
        non_empty_frames = self.__storage.iterate_non_empty_frames(
            include_fields=include_fields, exclude_fields=exclude_fields,
            pagination_key=pagination_key, upper_pagination_key=upper_pagination_key
        )
        return {row[0]: [0] for row in non_empty_frames}

    def filter_ngrams(
        self, ngrams, include_fields=None, exclude_fields=None, bigram_idf_weight=5, return_documents=False,
        pagination_key=None, upper_pagination_key=None, scoring='tf', normalise_length=False
    ):
        """
        Search for frames or documents containing the specified list of n-grams on the given index.

        An arbitrary IDF multiplier will be applied as the IDF score for matching ngrams

        Currently only searching for bigrams (n = 2) is supported.

        Args

            ngrams: iterator of n-gram tuples, in positional order
                Currently only 2-tuples (bigrams) are supported.

            include_fields, exclude_fields

            bigram_idf_weight: default 5.
                The IDF weight to assign to bigram scores. Use 1 for term-frequency weighting.

            return_documents: False by default.
                whether to return matching frames or matching documents.

            pagination_key, upper_pagination_key: default None, behaves the same as in all other functions.

            scoring: One of 'tf' or 'binarised-tf', whether to use term frequency or binary presence/absence of a
                an ngram when scoring. IDF weighting for phrases is not supported, uses the bigram_IDF_weight
                parameter to boost phrases.

            normalise_length: default False.
                If True, normalise scores by frame lengths (the number of tokens in the frame). This is an approximation
                to full l2 normalisation for cosine distance.

        Returns

            {frame_id | document_id : [list of matching ngram scores]}

        """
        results = defaultdict(list)

        for ngram in ngrams:
            matches = self.__storage.iterate_ngram_frames(
                ngram, include_fields=include_fields, exclude_fields=exclude_fields, return_documents=return_documents,
                pagination_key=pagination_key, upper_pagination_key=upper_pagination_key,
                scoring=scoring, normalise_length=normalise_length
            )

            for match_id, freq in matches:
                results[match_id].append(freq * bigram_idf_weight)

        return results

    def _filter_attributes(
        self, attributes, return_documents=False, include_fields=None, exclude_fields=None, limit=0,
        pagination_key=None, upper_pagination_key=None
    ):
        """Return frames or documents containing specific attributes.

        Currently this is a very thin skin over the underlying SQLite storage class - expect this interface to
        be merged with regular term filtering and the schema field API in the future. No type conversion or checking
        is performed - the attribute comparisons will be directly used as bound parameters in an SQL query.

        Don't rely on this API to be stable!

        Args:

            attributes: A dictionary specifying attribute type, value and comparison operator.
                Supported operators are: '=', '>', '>=', '<', '<='
                Example attribute searches:
                {
                    'website': {'=': 'www.website.com'},
                    'sentiment': {'=': 'positive'}
                }
                                {
                    'named_entity': {'=': 'Sydney, Australia'},
                    'sentiment_magnitude': {'>': 0.6}
                    'sentiment_polarity': {'>': 0}
                }


            return_documents: True or False
                If True, return all documents with at least one frame containing those attributes, otherwise
                return only specific frames.

            include_fields: list of unstructured fields to include in the analysis.
                By default this is None, and all fields are included if exclude_fields is also None.

            exclude_fields: list of unstructured fields to exclude from the analysis.
                If include_fields is not None, this argument is ignored.

            limit: default 0
                Limit number of returned frames to this value

            pagination_key: default None
                A frame or document id to begin filter operation from. This allows efficient pagination operations.

            """

        results = self.__storage.filter_attributes(
            attributes, return_documents=return_documents, include_fields=include_fields, exclude_fields=exclude_fields,
            limit=limit, pagination_key=pagination_key, upper_pagination_key=upper_pagination_key
        )

        return {key[0]: [0] for key in results}

    def _validate_analyse_metadata(self, metadata_search_spec):
        """Validate that the fields and operators for this metadata search, and analyse the values."""
        schema = self.get_schema()
        metadata_fields = schema.get_indexed_structured_fields()

        analysed_metadata = {}

        # map from valid operator specs to field specs - most of these are the same as the field specification,
        # however more may be added in the future.
        # Note that in is just a multi comparison equal, where one of the set must match.
        valid_metadata_operators = {
            '<': '<', '>': '>', '<=': '<=', '>=': '>=', 'in': '=', '=': '=',
            'between': 'between', 'not between': 'not between'
        }

        # Validate the search fields
        for field, operators in metadata_search_spec.items():

            if field not in metadata_fields:
                if field in schema:
                    raise NonIndexedFieldError('"{}" is not an indexed structured data field'.format(field))
                else:
                    raise UnknownFieldError('"{}" is not defined on this index'.format(field))

            analysed_metadata[field] = {}

            for operator, values in operators.items():

                if operator not in valid_metadata_operators:
                    raise NonSearchableOperatorError('Operator "{}" not available for search.'.format(operator))

                # Check the operator is supported by the field.
                try:
                    schema[field].evaluate_op(valid_metadata_operators[operator], values, None)
                except NotImplementedError:  # The only exception we actually care about.
                    raise UnsupportedOperatorError(
                        'Operator "{}" not supported by field "{}"'.format(operator, field)
                    )
                except Exception:
                    pass

                # Analyse the values to be associated with the operator.
                if operator == 'in' or operator == 'between' or operator == 'not between':
                    # Value list
                    field_comp_value = [schema[field].value_of(value) for value in values]
                else:
                    # Single value
                    field_comp_value = schema[field].value_of(values)

                analysed_metadata[field][operator] = field_comp_value

        return analysed_metadata


def _default_dict_list():
    """Helper function to return a new default dict of lists."""
    return defaultdict(list)
