# Copyright (c) 2012-2014 Kapiche Limited
# Author: Kris Rogers <kris@mammothlabs.com.au>, Ryan Stuart <ryan@kapiche.com>
"""Tests for caterpillar.storage.sqlite.py."""
from collections import defaultdict
import os
import shutil
import tempfile

import pytest
import apsw

from caterpillar.storage import StorageNotFoundError, DuplicateStorageError, SchemaMismatchError, MigrationError

from caterpillar.storage.sqlite import SqliteReader, SqliteWriter, CURRENT_SCHEMA


@pytest.fixture
def tmp_dir(request):
    path = tempfile.mkdtemp()

    def clean():
        shutil.rmtree(path)

    request.addfinalizer(clean)
    new_path = os.path.join(path, "test")
    os.makedirs(new_path)
    return new_path


def test_add_get_delete_fields(tmp_dir):
    """ Test adding indexed fields to the schema. """
    writer = SqliteWriter(tmp_dir, create=True)

    add_fields1 = ['test', 'test2']
    add_fields2 = ['test1', '']
    writer.begin()
    writer.add_structured_fields(add_fields1)
    writer.add_unstructured_fields(add_fields2)
    writer.commit()

    reader = SqliteReader(tmp_dir)
    reader.begin()
    structured = reader.structured_fields
    unstructured = reader.unstructured_fields
    reader.commit()

    for field in structured:
        assert field in add_fields1
    for field in unstructured:
        assert field in add_fields2


def test_nonexistent_path(tmp_dir):
    with pytest.raises(StorageNotFoundError):
        SqliteWriter(tmp_dir + '/nonexistent_dir')


def test_alternate_document_format(tmp_dir):
    pass


def test_bad_document_format(tmp_dir):
    writer = SqliteWriter(tmp_dir, create=True)

    bad_document = [
        'A badly formatted document',
        {},
        {'text': ['An example', 'document without', 'anything fancy'],
         'invalid_field': []},
        {'text': [
            {'An': [0, 5, 7], 'example': [0, 5, 7]},
            {'document': [0, 5, 7], 'without': [0, 5, 7]},
            {'anything': [0, 5, 7], 'fancy': [0, 5, 7]}
        ]}
    ]

    writer.begin()
    writer.add_unstructured_fields(['text'])

    # Non matching fields
    with pytest.raises(ValueError):
        writer.add_analyzed_document('v1', bad_document)

    # Non matching numbers of frames and positions:
    bad_document[2] = {'text': ['An example', 'frame']}
    with pytest.raises(ValueError):
        writer.add_analyzed_document('v1', bad_document)

    with pytest.raises(ValueError):
        writer.add_analyzed_document('unknown_format', bad_document)

    writer.close()


def test_add_get_document(tmp_dir):

    sample_format_document = (
        'An example document without anything fancy',
        {'test_field': 1, 'other_field': 'other'},
        {'text': ['An example', 'document without', 'anything fancy']},
        {'text': [
            {'An': [0, 5, 7], 'example': [0, 5, 7]},
            {'document': [0, 5, 7], 'without': [0, 5, 7]},
            {'anything': [0, 5, 7], 'fancy': [0, 5, 7]}
        ]}
    )

    writer = SqliteWriter(tmp_dir, create=True)

    # Add one document
    writer.begin()
    writer.add_structured_fields(['test_field', 'other_field'])
    writer.add_unstructured_fields(['text'])
    writer.add_analyzed_document('v1', sample_format_document)

    with pytest.raises(apsw.SQLError):
        writer._execute('select * from nonexistent_table')
    with pytest.raises(apsw.SQLError):
        writer._executemany('insert into nonexistent_table values(?)', [(None,)])

    writer.commit()

    reader_transaction = SqliteReader(tmp_dir)
    reader_transaction.begin()

    reader = SqliteReader(tmp_dir)

    with pytest.raises(apsw.SQLError):
        reader._execute('select * from nonexistent_table')
    with pytest.raises(apsw.SQLError):
        reader._executemany('insert into nonexistent_table values(?)', [(None,)])

    doc = list(reader.iterate_documents([1]))[0]  # Cheating with sequential document_id's here
    assert doc[1] == sample_format_document[0]
    assert reader.count_documents() == 1 == reader_transaction.count_documents()
    assert reader.count_vocabulary() == 6 == reader_transaction.count_vocabulary()

    # Add 100 more documents:
    writer.begin()
    for i in range(100):
        writer.add_analyzed_document('v1', sample_format_document)
    writer.commit()

    assert reader.count_documents() * 3 == 303 == reader.count_frames()
    assert reader_transaction.count_documents() == 1
    assert reader.count_vocabulary() == 6
    assert sum(i[1] for i in reader.iterate_term_frequencies()) == 606

    reader_transaction.commit()
    assert reader_transaction.count_documents() == 101

    meta = list(reader.iterate_metadata())
    assert len(meta) == 202

    meta = list(reader.iterate_metadata(return_documents=False))
    assert len(meta) == 606

    # Delete all the documents
    writer.begin()
    writer.delete_documents([d_id for d_id, _ in reader.iterate_documents()])
    writer.commit()

    assert reader.count_documents() == 0 == reader.count_frames()
    assert reader.count_vocabulary() == 6
    assert sum(i[1] for i in reader.iterate_term_frequencies()) == 0


def test_iterators(tmp_dir):
    sample_format_document = (
        'An example document without anything fancy',
        {'test_field': 1, 'other_field': 'other', 'date_field': '2018-09-15T15:53:00'},
        {
            'text': ['An example', 'document without', 'anything fancy'],
            'text1': ['An example', 'document without', 'anything fancy']
        }, {
            'text': [
                {'An': [0, 5, 7], 'example': [0, 5, 7]},
                {'document': [0, 5, 7], 'without': [0, 5, 7]},
                {'anything': [0, 5, 7], 'fancy': [0, 5, 7]}
            ],
            'text1': [
                {'An': [0, 5, 7], 'example': [0, 5, 7]},
                {'document': [0, 5, 7], 'without': [0, 5, 7]},
                {'anything': [0, 5, 7], 'fancy': [0, 5, 7]}
            ]
        },
    )

    writer = SqliteWriter(tmp_dir, create=True)

    # Add many documents.
    writer.begin()
    writer.add_structured_fields(['test_field', 'other_field', 'date_field'])
    writer.add_unstructured_fields(['text', 'text1'])
    for i in range(100):
        writer.add_analyzed_document('v1', sample_format_document)
    writer.commit()

    assert len(writer._SqliteWriter__last_added_documents) == 100

    reader = SqliteReader(tmp_dir)
    reader.begin()

    positions = reader.iterate_positions(include_fields=['text'])
    assert sum(1 for _ in positions) == 6
    positions = reader.iterate_positions(exclude_fields=['text', 'text1'])
    assert sum(1 for _ in positions) == 0
    positions = reader.iterate_positions()
    assert sum(1 for _ in positions) == 6

    positions = reader.iterate_positions(include_fields=['unknown field'])
    # If the field is not indexed, raise an error
    with pytest.raises(ValueError):
        list(positions)

    metadata_frames = [
        (field, value, frame) for field, value, frame in reader.iterate_metadata(return_documents=False)
    ]
    assert len(metadata_frames) == 1800
    assert len({row[0] for row in metadata_frames}) == 3
    assert len({row[1] for row in metadata_frames}) == 3
    assert len({row[2] for row in metadata_frames}) == 600

    metadata_segments = defaultdict(list)
    for field, value in reader.iterate_metadata_values():
        metadata_segments[field].append(value)
    assert len(metadata_segments) == 3
    assert len(metadata_segments['test_field']) == 1 and metadata_segments['test_field'][0] == 1
    assert len(metadata_segments['other_field']) == 1 and metadata_segments['other_field'][0] == 'other'
    assert len(metadata_segments['date_field']) == 1 and metadata_segments['date_field'][0] == '2018-09-15T15:53:00'

    frame_metadata = list(reader._iterate_frame_metadata([1, 10, 100]))
    assert len(frame_metadata) == 9  # 3 frames x 3 metadata fields
    assert len({row[0] for row in frame_metadata}) == 3
    assert len({row[1] for row in frame_metadata}) == 3
    assert len({row[2] for row in frame_metadata}) == 3
    assert sum(1 for _ in reader._iterate_frame_metadata(set(result[2] for result in metadata_frames))) == 1800

    # Test restricting the fields
    frame_metadata = list(reader._iterate_frame_metadata([1, 10, 100], structured_fields=['test_field', 'other_field']))
    assert len(frame_metadata) == 6  # 3 frames x 2 metadata fields
    assert len({row[0] for row in frame_metadata}) == 2
    assert len({row[1] for row in frame_metadata}) == 2
    assert len({row[2] for row in frame_metadata}) == 3

    # Test date field rollup
    frame_metadata = list(reader._iterate_frame_date_metadata([1, 10, 100], ['date_field'], resolution='day'))
    assert len(frame_metadata) == 3  # 3 frames x 1 date metadata field
    assert frame_metadata[0][1] == '2018-09-15'
    frame_metadata = list(reader._iterate_frame_date_metadata([1, 10, 100], ['date_field'], resolution='week'))
    assert len(frame_metadata) == 3  # 3 frames x 1 date metadata field
    assert frame_metadata[0][1] == '2018-09-16'
    frame_metadata = list(reader._iterate_frame_date_metadata([1, 10, 100], ['date_field'], resolution='month'))
    assert len(frame_metadata) == 3  # 3 frames x 1 date metadata field
    assert frame_metadata[0][1] == '2018-09-01'
    frame_metadata = list(reader._iterate_frame_date_metadata([1, 10, 100], ['date_field'], resolution='year'))
    assert len(frame_metadata) == 3  # 3 frames x 1 date metadata field
    assert frame_metadata[0][1] == '2018-01-01'

    # Get documents corresponding to the metadata instead of just the frames.
    metadata_documents = [
        (field, values, documents) for field, values, documents in reader.iterate_metadata()
    ]
    assert len(metadata_documents) == 300
    assert len({row[0] for row in metadata_documents}) == 3
    assert len({row[1] for row in metadata_documents}) == 3
    assert len({row[2] for row in metadata_documents}) == 100

    document_metadata = list(reader._iterate_document_metadata([1, 10, 100]))
    assert len(document_metadata) == 9  # 3 frames x 3 metadata fields
    assert len({row[0] for row in document_metadata}) == 3
    assert len({row[1] for row in document_metadata}) == 3
    assert len({row[2] for row in document_metadata}) == 3

    # Test restricting the fields
    document_metadata = list(reader._iterate_document_metadata(
        [1, 10, 100], structured_fields=['test_field', 'other_field'])
    )
    assert len(document_metadata) == 6  # 3 frames x 2 metadata fields
    assert len({row[0] for row in document_metadata}) == 2
    assert len({row[1] for row in document_metadata}) == 2
    assert len({row[2] for row in document_metadata}) == 3

    # Test date field rollup
    document_metadata = list(reader._iterate_document_date_metadata([1, 10, 100], ['date_field'], resolution='day'))
    assert len(document_metadata) == 3  # 3 frames x 1 date metadata field
    assert document_metadata[0][1] == '2018-09-15'
    document_metadata = list(reader._iterate_document_date_metadata([1, 10, 100], ['date_field'], resolution='week'))
    assert len(document_metadata) == 3  # 3 frames x 1 date metadata field
    assert document_metadata[0][1] == '2018-09-16'  # Sunday
    document_metadata = list(reader._iterate_document_date_metadata([1, 10, 100], ['date_field'], resolution='month'))
    assert len(document_metadata) == 3  # 3 frames x 1 date metadata field
    assert document_metadata[0][1] == '2018-09-01'
    document_metadata = list(reader._iterate_document_date_metadata([1, 10, 100], ['date_field'], resolution='year'))
    assert len(document_metadata) == 3  # 3 frames x 1 date metadata field
    assert document_metadata[0][1] == '2018-01-01'

    metadata_text = [
        (field, values, documents) for field, values, documents
        in reader.iterate_metadata(include_fields=['text'], structured_fields=['test_field'], return_documents=False)
    ]
    assert len(metadata_text) == 300
    assert len({row[0] for row in metadata_text}) == 1
    assert len({row[1] for row in metadata_text}) == 1
    assert len({row[2] for row in metadata_text}) == 300

    reader.close()


def test_filter_error(tmp_dir):

    sample_format_document = (
        'An example document without anything fancy',
        {'test_field': 1, 'other_field': 'other'},
        {'text': ['An example', 'document without', 'anything fancy']},
        {'text': [
            {'An': [0, 5, 7], 'example': [0, 5, 7]},
            {'document': [0, 5, 7], 'without': [0, 5, 7]},
            {'anything': [0, 5, 7], 'fancy': [0, 5, 7]}
        ]}
    )

    writer = SqliteWriter(tmp_dir, create=True)

    # Add many documents.
    writer.begin()
    writer.add_structured_fields(['test_field', 'other_field'])
    writer.add_unstructured_fields(['text'])
    for i in range(100):
        writer.add_analyzed_document('v1', sample_format_document)
    writer.commit()

    reader = SqliteReader(tmp_dir)
    reader.begin()

    with pytest.raises(ValueError):
        reader.rank_or_filter_unstructured(must=['example'], metadata={'test_field': {'*=': 1}})
    with pytest.raises(ValueError):
        reader.rank_or_filter_unstructured(metadata={'test_field': {'*=': 1}}, search=True)
    with pytest.raises(ValueError):
        reader.filter_metadata(metadata={'test_field': {'*=': 1}})

    reader.close()


def test_duplicate_database(tmp_dir):
    SqliteWriter(tmp_dir, create=True)
    with pytest.raises(DuplicateStorageError):
        SqliteWriter(tmp_dir, create=True)


def test_open_migrate_old_schema_version(index_dir):
    """Open and attempt to operate storage created with an earlier version. """
    # Copy the old index to the temp dir, as we need to modify it.
    migrate_index = os.path.join(index_dir, 'sample_index')
    shutil.copytree('caterpillar/test_resources/alice_v0.13.0', migrate_index)

    writer = SqliteWriter(migrate_index)
    reader = SqliteReader(migrate_index)
    cursor = writer._db_connection.cursor()

    with pytest.raises(SchemaMismatchError):
        writer.begin()

    with pytest.raises(SchemaMismatchError):
        reader.begin()

    schema_version = writer.migrate()
    assert schema_version == CURRENT_SCHEMA
    # Ensure migrations are idempotent
    schema_version = writer.migrate()
    assert schema_version == CURRENT_SCHEMA

    reader.begin()
    reader.commit()

    # Mess with the schema version table, just to simulate newer schema versions than current.
    cursor.execute('insert into migrations(id) values (?)', [schema_version + 1])
    with pytest.raises(SchemaMismatchError):
        reader.begin()

    with pytest.raises(SchemaMismatchError):
        writer.begin()

    with pytest.raises(MigrationError):
        writer.migrate()


def test_failing_migration_check(index_dir):
    """Open and attempt to operate storage created with an earlier version. """
    # Copy the old index to the temp dir, as we need to modify it.
    migrate_index = os.path.join(index_dir, 'sample_index')
    shutil.copytree('caterpillar/test_resources/alice_v0.13.0', migrate_index)

    writer = SqliteWriter(migrate_index)
    assert writer.schema_version == -1

    cursor = writer._db_connection.cursor()

    # Mangle the on disk data to make sure the integrity check works.
    # We're going to change the json serialised positions so that there is a mismatch.
    cursor.execute("""
        update frame set stored = (
            select stored from frame where id = 100
        )
        where id = 10
    """)
    with pytest.raises(MigrationError):
        writer.migrate()

    assert writer.schema_version == 0
