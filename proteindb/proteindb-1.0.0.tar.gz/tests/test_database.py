from proteindb import ProteinDB
import sqlite3
import pytest
from Bio import SeqIO

TEST_FASTA_FILENAME = './data/uniprot-proteome_UP000207613.fasta'

@pytest.fixture
def db():
    return ProteinDB('test.db')


@pytest.fixture
def cursor(db):
    conn = db._conn
    return conn.cursor()


@pytest.fixture
def populated_db(db):
    db.populate(fasta_filename=TEST_FASTA_FILENAME)
    return db


@pytest.fixture
def fasta_records():
    with open(TEST_FASTA_FILENAME) as f:
        records = list(SeqIO.parse(f, 'fasta'))
    return records


def test_proteindb_contains_database(db):
    assert isinstance(db._conn, sqlite3.Connection)


def test_db_contains_protein_table(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    results = cursor.fetchall()
    assert len(results) == 1
    assert results[0][0] == 'proteins'


def test_db_table_contains_all_columns(cursor):
    cursor.execute("PRAGMA table_info('proteins');")
    results = cursor.fetchall()
    columns = [result[1] for result in results]
    assert 'uniprot_id' in columns and 'sequence' in columns


def test_db_contains_records(db):
    c = db._conn.cursor()
    results = c.execute("SELECT * from proteins").fetchall()
    assert len(results) == 0

    db.populate(fasta_filename=TEST_FASTA_FILENAME)

    results = c.execute("SELECT * from proteins").fetchall()
    assert len(results) > 0


def test_db_contains_all_records(populated_db, fasta_records):
    c = populated_db._conn.cursor()
    results = c.execute("SELECT * from proteins").fetchall()
    assert len(results) == len(fasta_records)


def test_db_contains_correct_records(populated_db, fasta_records):
    c = populated_db._conn.cursor()
    results = c.execute("SELECT * from proteins").fetchall()
    sequences = [str(record.seq) for record in fasta_records]
    for result in results:
        assert result[2] in sequences

    uniprot_ids = [str(record.id.split('|')[1]) for record in fasta_records]
    for result in results:
        assert result[1] in uniprot_ids


def test_querying_uniprot_id_works(populated_db, fasta_records):
    assert not populated_db.result

    for record in fasta_records:
        sequence = str(record.seq)
        uniprot_id = str(record.id.split('|')[1])
        populated_db.query(uniprot_id=uniprot_id)
        assert populated_db.result == sequence

def test_querying_sequence_works(populated_db, fasta_records):
    assert not populated_db.result

    for record in fasta_records:
        sequence = str(record.seq)
        uniprot_id = str(record.id.split('|')[1])
        populated_db.query(sequence=sequence)
        assert populated_db.result == uniprot_id