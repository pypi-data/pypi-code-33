# Copyright (c) Kapiche Limited
# Author: Sam Hames <sam.hames@kapiche.com>
"""
Migrating data through different versions of :class:`.SqliteStorage`.

Migrations are a linear history of index format changes through the life of the project.
Each migration is represented by an integer migration_id, and migrations are applied in
order of ascending integer key. Migrating from state m to state n implies running all migration
functions represented m < migration_id <= n.

Each migration must manage it's own transactions, including calling begin and commit at the
start/end.

"""
import json


def initialise_schema(writer):
    """
    Setup the database with the initial schema.

    Also sets up the necessary database file options that will
    persist through all schema versions (WAL and pagesize).

    """
    cursor = writer._db_connection.cursor()
    list(cursor.execute(schema_base))


def row_per_position(writer):
    """
    Migrate the schema to store one row per position

    """
    cursor = writer._db_connection.cursor()

    # Drop the existing posting tables and recreate with the new schema
    expected_rows = list(cursor.execute("""
        begin;
        -- Self check: the new tables should have this many rows.
        select coalesce(sum(frequency), 0) from frame_posting;

        drop table frame_posting;
        drop table term_posting;

        create table frame_posting (
            frame_id integer,
            position integer,
            term_id integer,
            primary key(frame_id, position, term_id),
            foreign key(term_id) references term(id),
            foreign key(frame_id) references frame(id)
        ) without rowid;

        create table term_posting (
            term_id integer,
            frame_id integer,
            position integer,
            primary key(term_id, frame_id, position),
            foreign key(term_id) references term(id),
            foreign key(frame_id) references frame(id)
        ) without rowid;
    """))[0][0]

    # Now we do a roundtrip through python with the JSON serialised frame
    frame_cursor = writer._db_connection.cursor()
    all_frames = frame_cursor.execute(
        'select id, stored from frame'
    )

    # Get the mapping from terms to term_ids:
    vocab_map = {term: term_id for term_id, term in cursor.execute('select id, term from vocabulary')}
    for frame_id, stored in all_frames:
        stored = json.loads(stored)
        new_positions = ((frame_id, p, vocab_map[term]) for term, pos in stored['_positions'].items() for p in pos)
        cursor.executemany('insert into frame_posting values (?, ?, ?)', new_positions)

    migrated_rows = list(cursor.execute('select count(*) from frame_posting'))[0][0]
    if migrated_rows != expected_rows:
        raise ValueError('Row miscount, expected {} rows, actually found {} rows'.format(migrated_rows, expected_rows))

    cursor.execute('insert into term_posting select term_id, frame_id, position from frame_posting order by 1, 2')
    cursor.execute("insert into migrations(id, description) values(1, 'Move to row per position')")
    cursor.execute('commit')


def store_frame_lengths(writer):
    """
    Store the length of each frame in a separate table.

    """
    cursor = writer._db_connection.cursor()

    cursor.execute("""
        begin;

        create table frame_length (
            frame_id integer primary key,
            n_positions integer,
            foreign key (frame_id) references frame(id) on delete cascade
        );

        insert into frame_length(frame_id, n_positions)
            select frame_id, max(position) + 1 -- positions are zero indexed
            from frame_posting
            group by frame_id;

        insert into migrations(id, description) values(2, 'Store frame lengths');
        commit;
    """)


migrations = {
    0: initialise_schema,
    1: row_per_position,
    2: store_frame_lengths,
}


schema_base = """
/* pragma note: the page_size is set for the whole database, and can only change with
and expensive vaccuum operation - it also must be run before anything else is done
with the database. So this line must come first! */
pragma page_size = 4096; -- current recommended value for SQLite.

/* Set write ahead log mode for all connections that will use this database. The WAL
allow concurrent readers and writers, unlike the default journal mode that locks readers
out while writing. */
pragma journal_mode = WAL;

begin;

/* Field names and ID's

Structured and unstructured fields are kept separate because the storage and querying
of each type of data is different.
*/
create table if not exists structured_field (
    id integer primary key,
    name text unique
);

create table if not exists unstructured_field (
    id integer primary key,
    name text unique
);


/*
The core vocabulary table assigns an integer ID to every unique term in the index.

Joins against the core posting tables are always integer-integer and in sorted order.

This table may eventually be merged with the attributes table.

*/
create table if not exists vocabulary (
    id integer primary key,
    term text
);
create index if not exists term_idx on vocabulary(term);


/* Summary statistics for a given term_id by field.

This allows direct lookups for Tf.IDF searches and similar.
*/
create table if not exists term_statistics (
    term_id integer,
    field_id integer,
    frequency integer,
    frames_occuring integer,
    documents_occuring integer,
    primary key(term_id, field_id),
    foreign key(term_id) references term(id),
    foreign key(field_id) references field(id)
);


/* Summary statistics for each field. */
create table if not exists field_statistics (
    field_id integer primary key,
    frame_count integer
);


/* The source table for the document representation. */
create table if not exists document (
    id integer primary key,
    stored text -- This should be a text serialised representation of the document, such as JSON.
);

/*
Storage for 'indexed' structured fields in the schema.

- designed for sparse data and extensible schema's
- primary design purpose is for returning ordered lists of document ID's
- takes advantage of SQLite's permissive type system

*/
create table if not exists document_data (
    field_id integer,
    value,
    document_id integer,
    primary key(field_id, value, document_id),
    foreign key(document_id) references document(id),
    foreign key(field_id) references structured_field(id)
);

/* Make sure we can get document metadata by document, not just field/value */
create index if not exists metadata_document_idx on document_data(document_id, field_id, value);


/* Storage for frames, structured to link between document level metadata and frame level text information. */
create table if not exists frame (
    id integer primary key,
    document_id integer,
    field_id integer,
    sequence integer,
    stored text -- The stored representation of the frame.
);


/* Index to access by document ID

Bridges between:
structured data searches --> frames
unstructured searches --> documents
*/
create index if not exists document_frame_bridge on frame(document_id, field_id);
create index if not exists field_frame_idx on frame(field_id, document_id);


/* Postings organised by term, allowing search operations. */
create table if not exists term_posting (
    term_id integer,
    frame_id integer,
    frequency integer,
    positions integer,
    primary key(term_id, frame_id),
    foreign key(term_id) references term(id),
    foreign key(frame_id) references frame(id)
)
without rowid; -- Ensures that the data in the base table is kept in this sorted order.

/* Postings organised by frame, for term-frequency vector representations of documents and frames. */
create table if not exists frame_posting (
    frame_id integer,
    term_id integer,
    frequency integer,
    positions integer,
    primary key(frame_id, term_id),
    foreign key(term_id) references term(id) on delete cascade
    foreign key(frame_id) references frame(id) on delete cascade
)
without rowid;


/* Frame attribute storage.

This is the equivalent of the vocabulary table for semi-structured frame level data. This
table allows a 1:many mapping of frames --> attributes. An attribute is any structured piece
of information that can be extracted from a frame, such as sentiment scores, named entities,
parsed email addresses or websites, twitter @handles and #hashtags etc.

Although the data layout is conceptually similar to the term_posting + vocabulary table
it is maintained separately here for two reasons:
    1. Avoid overcomplicating the text search API with the addition of attribute types. (Also
       avoid rewriting the complex queries in search.)
    2. Simpler API - in the short term it is expected that attributes will be added
       post indexing/separate to plain text indexing. This means it is advantageous to have
       the attributes separate to the main table to better enhance write locality.

In the future we may consider merging the two tables and having a unified view into
unstructured attributes of a dataset. This might also allow more nuanced interpretation
of text indexing - for example indexing terms with an attribute class of their parts of
speech to allow more complex search operators/ disambiguation.

*/

/* Actual storage of the values of attributes.

Note - if an attribute class should be 1:1 on a frame, this needs to be enforced at the
application/reader level, as this schema needs to necessarily accept 1:many relationships.

*/
create table if not exists attribute (
    id integer primary key,
    type text,
    value,
    constraint attr_class_value unique (type, value) on conflict ignore
);


/* Attribute-frame tables

Analogous to frame_posting and term_posting, store attribute presence on a
frame, ordered by frame for analytical operations and by attribute for search operations.

*/
create table if not exists frame_attribute_posting (
    frame_id integer,
    attribute_id integer,
    primary key (frame_id, attribute_id) on conflict ignore,
    foreign key (frame_id) references frame(id),
    foreign key (attribute_id) references attribute(id)
)
without rowid;

create table if not exists attribute_frame_posting (
    attribute_id integer,
    frame_id integer,
    primary key (attribute_id, frame_id) on conflict ignore,
    foreign key (frame_id) references frame(id),
    foreign key (attribute_id) references attribute(id)
)
without rowid;


/* Plugin header and data tables. */
create table if not exists plugin_registry (
    plugin_type text,
    settings text,
    plugin_id integer primary key,
    constraint unique_plugin unique (plugin_type, settings) on conflict ignore
);

create table if not exists plugin_data (
    plugin_id integer,
    key text,
    value text,
    primary key(plugin_id, key) on conflict replace,
    foreign key(plugin_id) references plugin_registry(plugin_id) on delete cascade
);


/*
An internal representation of the state of the index documents.

The state of the documents in the index is represented by a tuple of:
    (revision_number, added_document_count, deleted_document_count, added_frame_count)

Each number is monotonically increasing and represents the current state of the index over it's
lifetime. The next document and frame added to the index will have ID's of added_document_count + 1
and added_frame_count + 1.

The revision number is incremented by one whenever a write transaction adds or deletes documents
from an index.

For example, a reader might run an operation when the state of the index was (5, 100, 5, 2000), while
the current state is (15, 130, 45, 2200). This means that 30 new documents and 200 new frames were added
in 10 commits, and 40 documents were deleted since that operation was run.

*/
create table if not exists index_revision (
    revision_number integer primary key,
    added_document_count integer,
    deleted_document_count integer,
    added_frame_count integer,
    constraint unique_revision unique(
        added_document_count, deleted_document_count, added_frame_count
    ) on conflict ignore
);

insert or ignore into index_revision values (0, 0, 0, 0);

create table if not exists setting (
    name text primary key on conflict replace,
    value
);

create table if not exists migrations (
    id integer primary key,
    description text,
    timestamp default current_timestamp
);

insert into migrations(id, description) values(0, 'Initial schema');

commit;

"""
