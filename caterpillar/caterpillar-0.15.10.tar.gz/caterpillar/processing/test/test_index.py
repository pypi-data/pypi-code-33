# Copyright (c) 2012-2014 Kapiche Limited
# Author: Kris Rogers <kris@kapiche.com>, Ryan Stuart <ryan@kapiche.com>
"""Tests for caterpillar.processing.index."""
from __future__ import division

from collections import Counter, defaultdict
import csv
from glob import glob
from itertools import product
import pickle
import shutil
import tempfile
import multiprocessing as mp
import multiprocessing.dummy as mt  # threading dummy with same interface as multiprocessing
import os

import pytest

from caterpillar import __version__ as version
from caterpillar.storage import Storage, SchemaMismatchError, MigrationError
from caterpillar.storage.sqlite import SqliteStorage, CURRENT_SCHEMA
from caterpillar.processing.analysis.analyse import EverythingAnalyser
from caterpillar.processing.index import (
    IndexWriter, IndexReader, IndexConfig, IndexNotFoundError, DocumentNotFoundError,
    SettingNotFoundError, IndexWriteLockedError
)
from caterpillar.processing.schema import ID, NUMERIC, TEXT, FieldType, Schema
from caterpillar.test_util import TestAnalyser


def test_index_open(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r', encoding='utf-8') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                             Schema(text1=TEXT(analyser=analyser),
                                    text2=TEXT(analyser=analyser),
                                    document=TEXT(analyser=analyser, indexed=False),
                                    flag=FieldType(analyser=EverythingAnalyser(),
                                    indexed=True, categorical=True))))

        # Just initialise the index to check the first revision number
        with writer:
            pass

        with IndexReader(index_dir) as reader:
            assert reader.revision == (0, 0, 0, 0)

        with writer:
            writer.add_document(text1=data, text2=data, document='alice.txt', flag=True, frame_size=2)

        # Identical text fields should generate the same frames and frequencies
        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_frequencies('text1')) == 501
            assert sum(1 for _ in reader.get_frequencies('text2')) == 501
            assert reader.get_term_frequency('Alice', 'text1') == 23
            assert reader.get_term_frequency('Alice', 'text2') == 23
            assert reader.get_document_count() == 1
            assert reader.get_frame_count(['text1']) == 52
            assert reader.get_frame_count(['text2']) == 52
            assert reader.get_documents_with_frames_count(['text1']) == 1
            assert reader.get_documents_with_frames_count(['text2']) == 1
            assert reader.get_documents_with_frames_count() == 1
            assert isinstance(reader.get_schema()['text1'], TEXT)
            assert isinstance(reader.get_schema()['text2'], TEXT)
            assert reader.revision == (1, 1, 0, 104)

            with pytest.raises(DocumentNotFoundError):
                reader.get_frame(10000)

        # Adding the same document twice should double the frame, term_frequencies and document counts
        with writer:
            writer.add_document(text1=data, text2=data, document='alice.txt', flag=True, frame_size=2)

        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_frequencies('text1')) == 501
            assert reader.get_term_frequency('Alice', 'text1') == 46
            assert reader.get_document_count() == 2
            assert reader.get_frame_count(['text1']) == 104
            assert reader.get_documents_with_frames_count(['text1']) == 2
            assert reader.get_documents_with_frames_count(['text2']) == 2
            assert reader.get_documents_with_frames_count() == 2
            assert isinstance(reader.get_schema()['text1'], TEXT)
            assert reader.revision == (2, 2, 0, 208)

        # To test a document that only has one of the text fields and not the other
        with writer:
            writer.add_document(text1=data, document='alice.txt', flag=True, frame_size=2)

        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_frequencies('text1')) == 501
            assert sum(1 for _ in reader.get_frequencies('text2')) == 501
            # three times the original amount because this was the third document added
            assert reader.get_term_frequency('Alice', 'text1') == 69
            assert reader.get_term_frequency('Alice', 'text2') == 46
            assert reader.get_document_count() == 3
            assert reader.get_frame_count(['text1']) == 156
            assert reader.get_frame_count(['text2']) == 104
            assert reader.get_documents_with_frames_count(['text1']) == 3
            assert reader.get_documents_with_frames_count(['text2']) == 2
            assert reader.get_documents_with_frames_count() == 3
            assert isinstance(reader.get_schema()['text1'], TEXT)
            assert reader.revision == (3, 3, 0, 260)

        # To test a document that has no text fields (highlights difference between get_document_count and
        # get_documents_with_frames_count.
        with writer:
            writer.add_document(document='alice.txt', flag=True, frame_size=2)

        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_frequencies('text1')) == 501
            assert sum(1 for _ in reader.get_frequencies('text2')) == 501
            # three times the original amount because this was the third document added
            assert reader.get_term_frequency('Alice', 'text1') == 69
            assert reader.get_term_frequency('Alice', 'text2') == 46
            assert reader.get_document_count() == 4
            assert reader.get_frame_count(['text1']) == 156
            assert reader.get_frame_count(['text2']) == 104
            assert reader.get_documents_with_frames_count(['text1']) == 3
            assert reader.get_documents_with_frames_count(['text2']) == 2
            assert reader.get_documents_with_frames_count() == 3
            assert isinstance(reader.get_schema()['text1'], TEXT)
            assert reader.revision == (4, 4, 0, 260)

        path = tempfile.mkdtemp()
        new_dir = os.path.join(path, "no_reader")
        try:
            with pytest.raises(IndexNotFoundError):
                IndexWriter(new_dir, IndexConfig(SqliteStorage, Schema(text=TEXT)))
                IndexReader(new_dir)  # begin() was never called on the writer
            with pytest.raises(IndexNotFoundError):
                with IndexWriter(new_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
                    pass
                os.remove(os.path.join(new_dir, "storage.db"))
                IndexReader(new_dir)  # The written container no longer exists
        finally:
            shutil.rmtree(path)

    with pytest.raises(IndexNotFoundError):
        IndexReader("fake")


def test_index_writer_not_found(index_dir):
    with pytest.raises(IndexNotFoundError):
        IndexWriter(index_dir)


def test_index_settings(index_dir):
    writer = IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT())))
    with writer:
        writer.set_setting('test', True)
        writer.set_setting('is_testing_fun', False)

    with IndexReader(index_dir) as reader:
        assert reader.get_setting('test')
        assert not reader.get_setting('is_testing_fun')
        settings = {k: v for k, v in reader.get_settings(['test', 'is_testing_fun'])}
        assert len(settings) == 2
        assert 'test' in settings
        with pytest.raises(SettingNotFoundError):
            reader.get_setting('dummy')


def test_index_config():
    """Test the IndexConfig object."""
    mock_storage = Storage('nothing', 'doing')
    conf = IndexConfig(mock_storage, Schema())
    assert conf.version == version

    pickle_data = pickle.dumps(True)
    with pytest.raises(ValueError):
        IndexConfig.loads(pickle_data)
    with pytest.raises(ValueError):
        IndexConfig.loads(" ")


def test_index_alice(index_dir):
    """Whole bunch of functional tests on the index."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r', encoding='utf-8') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                                                    Schema(text=TEXT(analyser=analyser),
                                                           document=TEXT(analyser=analyser, indexed=False),
                                                           blank=NUMERIC(indexed=True), ref=ID(indexed=True))))
        with writer:
            writer.add_document(text=data, document='alice.txt', blank=None, ref=123, frame_size=2)

        doc_id = writer.last_committed_documents[0]

        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_term_positions('nice', 'text')) == 3
            assert sum(1 for _ in reader.get_term_positions('key', 'text')) == 5

            with pytest.raises(KeyError):
                reader.get_term_positions('nonseneterminthisindex', 'text')

            with pytest.raises(KeyError):
                reader.get_term_frequency('nonseneterminthisindex', 'text')

            assert reader.get_vocab_size('text') == sum(1 for _ in reader.get_frequencies('text')) == 501
            assert reader.get_term_frequency('Alice', 'text') == 23
            assert reader.revision == (1, 1, 0, 52)

        with IndexWriter(index_dir) as writer:
            writer.add_fields(field1=TEXT, field2=NUMERIC(indexed=True))

        with IndexReader(index_dir) as reader:
            schema = reader.get_schema()
            assert 'field1' in schema
            assert 'field2' in schema

        with IndexWriter(index_dir) as writer:
            writer.delete_document(doc_id)

        assert len(writer.last_deleted_documents) == 1

        with IndexReader(index_dir) as reader:
            with pytest.raises(DocumentNotFoundError):
                reader.get_document(doc_id)
            assert reader.revision == (2, 1, 1, 52)

        with IndexWriter(index_dir) as writer:
            writer.delete_document(doc_id)

        assert len(writer.last_deleted_documents) == 0

        with IndexReader(index_dir) as reader:
            assert 'Alice' not in reader.get_frequencies('text')
            assert 'Alice' not in reader.get_positions_index('text')
            assert reader.revision == (2, 1, 1, 52)

        # Test not text
        with IndexWriter(index_dir) as writer:
            with pytest.raises(TypeError):
                writer.add_document(text=False, document='alice', frame_size=0)

        # Test frame size = 0 (whole document)
        with IndexWriter(index_dir) as writer:
            writer.add_document(text=data, document='alice', frame_size=0)
            writer.add_document(text="unicode data", document='test', frame_size=0)

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 2


def test_get_document_count_from_frame_ids(index_dir):
    """Whole bunch of functional tests on the index."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                                                    Schema(text1=TEXT(analyser=analyser), text2=TEXT,
                                                           document=TEXT(analyser=analyser, indexed=False),
                                                           blank=NUMERIC(indexed=True), ref=ID(indexed=True))))
        with writer:
            writer.add_document(text1=data, text2=data, document='alice.txt', blank=None, ref=123, frame_size=2)

        with IndexReader(index_dir) as reader:
            frame_ids = list(reader.get_frame_ids('text1'))
            document_count_from_frames = reader.get_document_count_from_frame_ids(frame_ids)
            total_document_count = reader.get_documents_with_frames_count(['text1'])

        assert document_count_from_frames == total_document_count


def test_index_alice_attributes(index_dir):
    """Whole bunch of functional tests on the index."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                                                    Schema(text1=TEXT(analyser=analyser), text2=TEXT,
                                                           document=TEXT(analyser=analyser, indexed=False),
                                                           blank=NUMERIC(indexed=True), ref=ID(indexed=True))))
        with writer:
            writer.add_document(text1=data, text2=data, document='alice.txt', blank=None, ref=123, frame_size=2)

        # Label all the frames with some nonsense attributes
        with IndexReader(index_dir) as reader:
            frame_ids = list(reader.get_frame_ids('text1'))

        attribute_index = {}

        for f_id in frame_ids:
            attribute_index[f_id] = {}
            attribute_index[f_id]['numerical_score'] = f_id // 10
            if f_id % 3 == 0:
                attribute_index[f_id]['sentiment'] = 'positive'
            if f_id % 11 == 0:
                attribute_index[f_id]['named_entity'] = str(f_id)

        with writer:
            writer.append_frame_attributes(attribute_index)

        with IndexReader(index_dir) as reader:
            text1_attribute_index = reader.get_attributes(include_fields=['text1'])
            text1_attribute_counts = {}
            for attribute, values in text1_attribute_index.items():
                text1_attribute_counts[attribute] = {}
                for value, frames in values.items():
                    text1_attribute_counts[attribute][value] = len(frames)

            text2_attribute_index = reader.get_attributes(include_fields=['text2'])

            all_attribute_index = reader.get_attributes()
            all_attribute_counts = {}
            for attribute, values in all_attribute_index.items():
                all_attribute_counts[attribute] = {}
                for value, frames in values.items():
                    all_attribute_counts[attribute][value] = len(frames)

            doc_attribute_index = reader.get_attributes(return_documents=True)
            doc_attribute_counts = {}
            for attribute, values in doc_attribute_index.items():
                doc_attribute_counts[attribute] = {}
                for value, docs in values.items():
                    doc_attribute_counts[attribute][value] = len(docs)

        assert text1_attribute_counts['sentiment']['positive'] == 17
        assert text1_attribute_counts['numerical_score'][1] == 10
        assert text1_attribute_counts == all_attribute_counts
        assert all(i == 1 for i in text1_attribute_counts['named_entity'].values())

        assert all([
            count == 1 for attribute, values in doc_attribute_counts.items()
            for value, count in values.items()
        ])

        assert all(
            [text2_attribute_index.get(i, None) is None for i in ['numerical_score', 'sentiment', 'named_entity']]
        )

        with IndexReader(index_dir) as reader:
            attribute_frames = reader.get_frames(None, frame_ids=range(20))
            for f_id, frame in attribute_frames:
                assert frame['_attributes']['numerical_score'] == f_id // 10
                if f_id % 3 == 0:
                    assert frame['_attributes']['sentiment'] == 'positive'
                else:
                    assert 'sentiment' not in frame['_attributes']
                if f_id % 11 == 0:
                    assert frame['_attributes']['named_entity']
                else:
                    assert 'named_entity' not in frame['_attributes']

            upper_page = reader.get_attributes(pagination_key=20)
            lower_page = reader.get_attributes(upper_pagination_key=20)
            both_paged = reader.get_attributes(pagination_key=20, upper_pagination_key=40)

            assert all(
                [f_id > 20 for values in upper_page.values() for frames in values.values() for f_id in frames]
            )
            assert all(
                [f_id <= 20 for values in lower_page.values() for frames in values.values() for f_id in frames]
            )
            assert all(
                [40 >= f_id > 20 for values in both_paged.values() for frames in values.values() for f_id in frames]
            )


def test_index_writer_rollback(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT(analyser=analyser))))
        writer.begin()
        try:
            writer.add_document(text=data)
        finally:
            writer.close()

        with IndexReader(index_dir) as reader:
            assert reader.get_document_count() == 0

        # Test rollback on exception
        try:
            with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT(analyser=analyser)))) as writer:
                writer.add_document(text=data)
                raise ValueError()
        except ValueError:
            pass

        with IndexReader(index_dir) as reader:
            assert reader.get_document_count() == 0


def test_index_writer_lock(index_dir):
    analyser = TestAnalyser()
    with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT(analyser=analyser)))) as writer1:
        writer1.add_document(text="Blah")
        writer2 = IndexWriter(index_dir)
        with pytest.raises(IndexWriteLockedError):
            writer2.begin(timeout=0.5)


def test_index_frames_docs_alice(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                                                    Schema(text=TEXT(analyser=analyser),
                                                           document=TEXT(analyser=analyser, indexed=False))))
        with writer:
            writer.add_document(text=data, document='alice.txt', frame_size=2)

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 52

            frame_id = list(reader.get_term_positions('Alice', 'text').keys())[0]
            frame = reader.get_frame(frame_id)
            assert frame_id == frame['_id']

            doc_id = frame['_doc_id']
            assert doc_id == reader.get_document(doc_id)['_id']
            assert doc_id == next(reader.get_documents())[0]


def test_index_moby_small(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/moby_small.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT(analyser=analyser))))
        with writer:
            writer.add_document(text=data, frame_size=2, )

        with IndexReader(index_dir) as reader:
            assert sum(1 for _ in reader.get_term_positions('Chace', 'text')) == 1
            assert sum(1 for _ in reader.get_term_positions('CONVERSATIONS', 'text')) == 1
            assert sum(1 for _ in reader.get_frequencies('text')) == 39


def test_index_alice_bigram_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/alice.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=40)
            assert ('golden', 'key') in index_bigrams
            assert len(index_bigrams) == 15

            # Increasing the threshold should result in fewer bigrams
            old_n = 1e6  # Nonsense high value for first comparison.
            for threshold in range(0, 100, 10):
                index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=threshold)
                n_bigrams = len(index_bigrams)
                assert n_bigrams <= old_n
                old_n = n_bigrams


def test_index_alice_bigram_npmi_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/alice.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=400, npmi_threshold=0.75)
            assert ('few', 'minutes') in index_bigrams
            assert len(index_bigrams) == 7

            # Increasing the NPMI should result in fewer bigrams
            old_n = 1e6  # Nonsense high value for first comparison.
            for npmi in [i / 100 for i in range(0, 100, 10)]:
                index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=1000, npmi_threshold=npmi)
                n_bigrams = len(index_bigrams)
                assert n_bigrams <= old_n
                old_n = n_bigrams


def test_moby_bigram_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/moby.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=40)
            assert len(index_bigrams) == 63
            assert ('ivory', 'leg') in index_bigrams

            with pytest.raises(ValueError):
                reader.filter_ngrams(['ivory', 'leg'], scoring='potato')

            for bigram in index_bigrams:
                for scoring in ['tf', 'binarised-tf']:
                    found = [
                        reader.filter_ngrams([bigram], scoring=scoring, normalise_length=normalise_length)
                        for scoring, normalise_length in product(['tf', 'binarised-tf'], [True, False])
                    ]
                    for f in found:
                        assert len(f) >= 5
                    tf_norm, tf_raw, btf_norm, btf_raw = [sum(i[0] for i in f.values()) for f in found]
                    assert tf_raw >= btf_raw
                    assert tf_norm >= btf_norm
                    assert tf_raw >= tf_norm
                    assert btf_raw >= btf_norm

            # Test ngrams
            found_documents = reader.filter_ngrams([('bone', 'leg', 'steadied',)], scoring='tf', normalise_length=True)
            assert len(found_documents) == 1
            found_documents = reader.filter_ngrams([('dead', 'Sperm', 'Whale')], scoring='tf', normalise_length=True)
            assert len(found_documents) == 1

            # Plumbing tests for document and pagination options.
            # The whole document is indexed individually, so there should only ever be one result.
            found_documents = reader.filter_ngrams(index_bigrams, return_documents=True)
            assert len(found_documents) == 1

            # Document level pagination key, shouldn't return anything.
            found_documents = reader.filter_ngrams(index_bigrams, return_documents=True, pagination_key=1)
            assert len(found_documents) == 0

            # Upper and lower frame pagination
            found_documents = reader.filter_ngrams(index_bigrams, pagination_key=100, upper_pagination_key=500)
            assert 100 < min(found_documents) <= 500
            assert 100 < max(found_documents) <= 500


def test_moby_bigram_npmi_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/moby.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=400, npmi_threshold=0.75)
            assert len(index_bigrams) == 18
            assert ('BOOK', 'FOLIO') in index_bigrams
            assert ('Cape', 'Horn') in index_bigrams

            for bigram in index_bigrams:
                found_positions = list(reader.filter_ngrams([bigram]))
                assert len(found_positions) >= 5


def test_wikileaks_bigram_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/wikileaks-secret.txt'), 'r', encoding='utf-8') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=40, include_fields=['text'])
            assert len(index_bigrams) == 68
            assert ('internet', 'service') in index_bigrams

            for bigram in index_bigrams:
                found_positions = list(reader.filter_ngrams([bigram], include_fields=['text']))
                assert len(found_positions) >= 5


def test_wikileaks_npmi_bigram_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/wikileaks-secret.txt'), 'r', encoding='utf-8') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=400, npmi_threshold=0.75)
            assert len(index_bigrams) == 22
            assert ('Negotiators', 'Note') in index_bigrams

            for bigram in index_bigrams:
                found_positions = list(reader.filter_ngrams([bigram], include_fields=['text']))
                assert len(found_positions) >= 5


def test_employee_survey_bigram_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/government-emplyee-survey-PC.txt'),
              'r', encoding='utf-8') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=40)
            assert len(index_bigrams) == 31
            assert ('pay', 'rise') in index_bigrams


def test_employee_survey_bigram_npmi_discovery(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/government-emplyee-survey-PC.txt'),
              'r', encoding='utf-8') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data)

        with IndexReader(index_dir) as reader:
            index_bigrams = reader.detect_significant_ngrams(min_count=5, threshold=400, npmi_threshold=0.75)
            assert len(index_bigrams) == 8
            assert ('fixed', 'term') in index_bigrams


def test_term_frequency_vectors(index_dir):
    """Test iterating through the term_frequency vectors. """
    with open(os.path.abspath('caterpillar/test_resources/alice.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data, frame_size=2)

    with IndexReader(index_dir) as reader:
        # the term-frequency vectors should accumulate to the same state as the vocabulary statistics
        tf_vectors = reader.get_term_frequency_vectors()
        # Ensure no duplicate frames come through
        total_frames = set()
        frame_count = 0
        term_counts = Counter()

        for frame, vector in tf_vectors:
            total_frames.add(frame)
            for term in vector:
                term_counts[term] += 1
            frame_count += 1

        assert frame_count == len(total_frames)
        # Some frames are degenerate and contain only punctuation
        assert frame_count != reader.get_frame_count(['text'])

        for term, frequency in reader.get_frequencies('text'):
            assert term_counts[term] == frequency

        # Now with a subset of frames, like for example from a search.
        tf_vectors = reader.get_term_frequency_vectors(frame_ids=range(1, 100))
        total_frames = set()
        frame_count = 0
        term_counts = Counter()

        for frame, vector in tf_vectors:
            total_frames.add(frame)
            for term in vector:
                term_counts[term] += 1
            frame_count += 1

        for frequency in term_counts.values():
            assert frequency <= 99

        assert frame_count == len(total_frames)


def test_skipgram_iteration(index_dir):
    """Test iterating through the term_frequency vectors. """
    with open(os.path.abspath('caterpillar/test_resources/alice.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text1=TEXT, text2=TEXT))) as writer:
            writer.add_document(text1=data, text2=data)

    with IndexReader(index_dir) as reader:

        # Basic argument checking coverage
        with pytest.raises(ValueError):
            reader.get_skipgrams(start_offset=0)

        with pytest.raises(ValueError):
            reader.get_skipgrams(end_offset=0)

        with pytest.raises(ValueError):
            reader.get_skipgrams(start_offset=3, end_offset=1)

        skip0_grams = reader.get_skipgrams()
        skip0_frames = defaultdict(set)
        skip0_all_frames = set()

        for frame_id, left, right in skip0_grams:
            skip0_frames[(left, right)].add(frame_id)
            skip0_all_frames.add(frame_id)

        skip0_counts = {bigram: len(frames) for bigram, frames in skip0_frames.items()}

        for bigram in skip0_counts.keys():
            assert len(list(reader.filter_ngrams([bigram]))) == skip0_counts[bigram]

        skip1_grams = reader.get_skipgrams(start_offset=1, end_offset=2)
        skip1_frames = defaultdict(set)
        skip1_all_frames = set()

        for frame_id, left, right in skip1_grams:
            skip1_frames[(left, right)].add(frame_id)
            skip1_all_frames.add(frame_id)

        skip1_counts = {bigram: len(frames) for bigram, frames in skip1_frames.items()}

        # Exclude adjacent terms from consideration: this + skip0 should be the same as skip1
        skip2_grams = reader.get_skipgrams(start_offset=2, end_offset=2)
        skip2_frames = defaultdict(set)
        skip2_all_frames = set()

        for frame_id, left, right in skip2_grams:
            skip2_frames[(left, right)].add(frame_id)
            skip2_all_frames.add(frame_id)

        skip2_counts = {bigram: len(frames) for bigram, frames in skip1_frames.items()}

        assert len(skip1_all_frames) == len(skip0_all_frames)
        assert len(skip1_counts) > len(skip0_counts)
        assert sum(skip1_counts.values()) > sum(skip0_counts.values())

        # Everything in skip0 should also be included in skip1.
        assert len(skip1_counts.keys() & skip0_counts.keys()) == len(skip0_counts.keys())
        # Everything in skip0 | skip2 should be in skip1
        assert len(skip2_counts.keys() | skip0_counts.keys()) == len(skip1_counts.keys())

        # Confirm that all bigram counts are equal or lesser to the skip1 counts.
        larger_count = 0
        for pair, count in skip0_counts.items():
            window_count = skip1_counts[pair]
            assert window_count >= count
            if window_count > count:
                larger_count += 1

        assert larger_count

        # Field selectivity
        text1_skip0 = reader.get_skipgrams(include_fields=['text1'])
        text1_skip0_counts = Counter()

        for frame_id, left, right in text1_skip0:
            text1_skip0_counts[(left, right)] += 1

        assert len(text1_skip0_counts) == len(skip0_counts) == len(text1_skip0_counts.keys() & skip0_counts.keys())

        # Frame selectivity
        frame_skip0 = reader.get_skipgrams(frame_ids=range(1, 101))
        frames = set()

        for frame_id, left, right in frame_skip0:
            frames.add(frame_id)

        assert max(frames) == 100


def test_alice_case_folding(index_dir):
    """Test constructing indexes with the bigram analyser. """
    with open(os.path.abspath('caterpillar/test_resources/alice.txt'), 'r') as f:
        f.seek(0)
        data = f.read()

        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data)

        with IndexReader(index_dir) as reader:
            normalise_case = reader.get_case_fold_terms(['text'])
            for term, normalise_term in normalise_case:
                assert term.title() == normalise_term or term.lower() == normalise_term
                assert reader.get_term_frequency(term, 'text') < reader.get_term_frequency(normalise_term, 'text')


def test_index_utf8(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/mt_warning_utf8.txt'), 'r') as f:
        data = f.read()
        analyser = TestAnalyser()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage,
                                                    Schema(text=TEXT(analyser=analyser),
                                                           document=TEXT(analyser=analyser, indexed=False))))
        with writer:
            writer.add_document(text=data, document='mt_warning_utf8.txt', frame_size=2)

        assert writer.last_committed_documents


def test_index_state(index_dir):
    with open(os.path.abspath('caterpillar/test_resources/detractors.csv'), 'r') as f:
        csv_reader = csv.reader(f)
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            row = next(csv_reader)
            writer.add_document(text=row[0])

        with IndexReader(index_dir) as reader:
            start_revision = reader.get_revision()

        with writer:
            doc_ids = []
            for row in csv_reader:
                doc_ids.append(writer.add_document(text=row[0]))

        with IndexReader(index_dir) as reader:
            assert start_revision != reader.get_revision()
            revision = reader.get_revision()

        writer = IndexWriter(index_dir, Schema(text=TEXT))
        with writer:
            writer.delete_document(doc_ids[0])

        with IndexReader(index_dir) as reader:
            assert revision != reader.get_revision()


def test_index_reader_writer_isolation(index_dir):
    """Test that readers and writers are isolated."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        writer = IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT)))
        with writer:
            writer.add_document(text=data)

        reader = IndexReader(index_dir)
        reader.begin()

        assert reader.get_frame_count(['text']) == 52
        assert reader.get_term_frequency('Alice', 'text') == 24

        # Add another copy of Alice
        writer = IndexWriter(index_dir, Schema(text=TEXT))
        with writer:
            writer.add_document(text=data)

        # Check reader can't see it
        assert reader.get_frame_count(['text']) == 52
        assert reader.get_term_frequency('Alice', 'text') == 24

        # Open new reader and make sure it CAN see the changes
        with IndexReader(index_dir) as reader1:
            assert reader1.get_frame_count(['text']) == reader.get_frame_count(['text']) * 2
            assert reader1.get_term_frequency('Alice', 'text') == reader.get_term_frequency('Alice', 'text') * 2

        reader.close()


def test_index_document_delete(index_dir):
    """Sanity test for delete document."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            writer.add_document(text=data)
            doc_id = writer.add_document(text=data)

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 104
            assert reader.get_term_frequency('Alice', 'text') == 48

        with IndexWriter(index_dir) as writer:
            writer.delete_document(doc_id)

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 52
            assert reader.get_term_frequency('Alice', 'text') == 24


def test_index_multi_document_delete(index_dir):
    """Sanity test for deleting multiple documents."""
    with open(os.path.abspath('caterpillar/test_resources/alice_test_data.txt'), 'r') as f:
        data = f.read()
        doc_ids = []
        with IndexWriter(index_dir, IndexConfig(SqliteStorage, Schema(text=TEXT))) as writer:
            doc_ids.append(writer.add_document(text=data))
            doc_ids.append(writer.add_document(text=data))

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 104
            assert reader.get_document_count() == 2

        with IndexWriter(index_dir) as writer:
            for doc_id in doc_ids:
                writer.delete_document(doc_id)

        with IndexReader(index_dir) as reader:
            assert reader.get_frame_count(['text']) == 0
            assert reader.get_document_count() == 0


def test_metadata_only_retrieval_deletion(index_dir):
    """Test we can retrieve metadata only documents"""
    config = IndexConfig(SqliteStorage, schema=Schema(num=NUMERIC(indexed=True), text=TEXT))
    with IndexWriter(index_dir, config) as writer:
        doc_id = writer.add_document(num=1)

    with IndexReader(index_dir) as reader:
        len(reader.filter(metadata={'num': {'=': 1}})) == 1

    with IndexWriter(index_dir, config) as writer:
        writer.delete_document(doc_id)

    with IndexReader(index_dir) as reader:
        assert reader.get_frame_count(['']) == 0
        assert reader.get_document_count() == 0


def test_field_names(index_dir):
    """Test fields with names containing spaces."""
    schema = {"Don't Like": TEXT, "Would Like": TEXT}
    document1 = {"Don't Like": 'The scenery was unpleasant.', "Would Like": 'More cats.'}
    config = IndexConfig(SqliteStorage, schema=Schema(**schema))

    with IndexWriter(index_dir, config) as writer:
        writer.add_document(document1)

    with IndexReader(index_dir) as reader:
        assert reader.get_document_count() == 1


def _acquire_write_single_doc(index_dir):  # pragma: no cover
    """Write a single document."""
    with IndexWriter(index_dir) as writer:
        writer.add_document(field1='test some text')


def _read_document_count(index_dir):  # pragma: no cover
    """Write something to the index, then attempt to read it."""
    with IndexWriter(index_dir) as writer:
        writer.add_document(field1='test some text')
    with IndexReader(index_dir) as reader:
        x = reader.get_document_count()
    return x


def test_concurrent_write_contention(index_dir):
    """Test that high contention for write lock can still proceed. """

    config = IndexConfig(SqliteStorage, schema=Schema(field1=TEXT))

    # initialise
    with IndexWriter(index_dir, config):
        pass

    # Easier case: contention from threads in the same process
    n = 100
    pool = mt.Pool(16)
    pool.map(_acquire_write_single_doc, [index_dir] * n)
    pool.close()

    # Attempt high contention document writes
    pool = mp.Pool(16)
    pool.map(_acquire_write_single_doc, [index_dir] * n)
    pool.close()

    with IndexReader(index_dir) as reader:
        assert reader.get_document_count() == 200


def test_concurrent_read_write_contention(index_dir):
    """Test that high contention for write lock can still proceed. """

    config = IndexConfig(SqliteStorage, schema=Schema(field1=TEXT))

    # initialise
    with IndexWriter(index_dir, config):
        pass

    # Read and write documents concurrently.
    pool = mp.Pool(16)  # Pool for readers
    x = pool.map(_read_document_count, [index_dir] * 100)
    pool.close()

    assert max(x) == 100


def test_unpickle_py2_config():
    """
    Confirm that we can at least unpickle indexes created with config pickles stored from python 2.

    This is not an exhaustive test of functionality, just a confirmation that we can load a pickle file
    without throwing errors.

    """
    test_pickles = glob('caterpillar/test_resources/pickles/*config')

    loaded = []

    for pickled in test_pickles:
        with open(pickled, 'rb') as f:
            loaded.append(IndexConfig.loads(f.read()))

    for l in loaded:
        assert l.schema._fields.keys()


def test_migrate_old_index(index_dir):
    """
    Confirm automatic migration of old indexes works correctly.

    """
    # Copy the files from the test directory to the temporary directory
    migrate_index = os.path.join(index_dir, 'sample_index')
    shutil.copytree('caterpillar/test_resources/alice_v0.13.0', migrate_index)

    reader = IndexReader(migrate_index, auto_migrate=False)
    writer = IndexWriter(migrate_index, auto_migrate=False)

    with pytest.raises(SchemaMismatchError):
        reader.begin()
    with pytest.raises(SchemaMismatchError):
        writer.begin()

    # now we're going to mangle the index to cause a migration failure
    writer = IndexWriter(migrate_index)
    cursor = writer._IndexWriter__storage._db_connection.cursor()
    # Note that we're dancing around the transactions implied by the migrations framework here.
    # We're moving the current frame_posting table out of the way to cause the auto migrate to
    # fail.
    cursor.execute('alter table frame_posting rename to dummy_table')

    # This auto migration will fail, but it will succesfully complete the first migration,
    # leaving us in a weird state.
    with pytest.raises(MigrationError):
        writer.begin()

    # Copy the table we mangled back.
    cursor.execute('drop table frame_posting; alter table dummy_table rename to frame_posting')
    # Auto migrate indexes by default.
    reader = IndexReader(migrate_index)
    reader.begin()

    assert reader._IndexReader__storage.schema_version == CURRENT_SCHEMA
    reader.close()
