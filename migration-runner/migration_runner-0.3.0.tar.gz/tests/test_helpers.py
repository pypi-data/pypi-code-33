#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


class TestHelpers(object):
    """Tests for Helpers class in `migration_runner` package."""

    def test_extract_sequence_sql_filename_expected(
            self, helpers, sql_filename_expected
    ):
        version = helpers.extract_sequence_num(sql_filename_expected)
        assert version == 45

    def test_extract_sequence_sql_filename_hyphen(
            self, helpers, sql_filename_hyphen
    ):
        version = helpers.extract_sequence_num(sql_filename_hyphen)
        assert version == 45

    def test_extract_sequence_sql_filename_not_zero_padded(
            self, helpers, sql_filename_not_zero_padded
    ):
        version = helpers.extract_sequence_num(sql_filename_not_zero_padded)
        assert version == 45

    def test_extract_sequence_sql_filename_spaced(
            self, helpers, sql_filename_spaced
    ):
        version = helpers.extract_sequence_num(sql_filename_spaced)
        assert version == 45

    def test_extract_sequence_sql_filename_no_sql_suffix(
            self, helpers, sql_filename_no_sql_suffix
    ):
        version = helpers.extract_sequence_num(sql_filename_no_sql_suffix)
        assert version == 45

    def test_extract_sequence_sql_filename_no_separator(
            self, helpers, sql_filename_no_separator
    ):
        version = helpers.extract_sequence_num(sql_filename_no_separator)
        assert version == 45

    def test_extract_sequence_sql_filename_bigint(
            self, helpers, sql_filename_bigint
    ):
        version = helpers.extract_sequence_num(sql_filename_bigint)
        assert version == 23514352834592347502351435283459234750

    def test_extract_sequence_sql_filename_no_version(
            self, helpers, sql_filename_no_version
    ):
        with pytest.raises(AttributeError):
            helpers.extract_sequence_num(sql_filename_no_version)

    def test_append_migration_sql_filename_expected(
            self, helpers, sql_filename_expected
    ):
        migrations = []
        helpers.append_migration(migrations, sql_filename_expected)
        assert migrations == [(45, sql_filename_expected)]

    def test_append_migration_sql_filename_expected_existing_value(
            self, helpers, sql_filename_expected
    ):
        migrations = [(2, "test.sql")]
        helpers.append_migration(migrations, sql_filename_expected)
        assert migrations == [(2, "test.sql"),
                              (45, sql_filename_expected)]

    def test_find_migrations_expected(
            self, helpers, tmpdir, sql_filename_expected
    ):
        filepath = tmpdir.join(sql_filename_expected)
        filepath.write("test")
        migrations = helpers.find_migrations(str(tmpdir))
        assert migrations == [(45, str(filepath))]

    def test_find_migrations_empty(
            self, helpers, tmpdir
    ):
        migrations = helpers.find_migrations(str(tmpdir))
        assert migrations == []

    def test_find_migrations_no_suffix(
            self, helpers, tmpdir, sql_filename_no_sql_suffix
    ):
        filepath = tmpdir.join(sql_filename_no_sql_suffix)
        filepath.write("test")
        migrations = helpers.find_migrations(str(tmpdir))
        assert migrations == []

    def test_find_migrations_multiple(
            self, helpers, tmpdir,
            sql_filename_expected,
            sql_filename_bigint,
            sql_filename_no_sql_suffix,
            sql_filename_spaced
    ):
        sql_filename_expected_filepath = tmpdir.join(sql_filename_expected)
        sql_filename_expected_filepath.write("test")

        sql_filename_bigint_filepath = tmpdir.join(sql_filename_bigint)
        sql_filename_bigint_filepath.write("test")

        sql_filename_no_sql_suffix_path = tmpdir.join(
            sql_filename_no_sql_suffix)
        sql_filename_no_sql_suffix_path.write("test")

        sql_filename_spaced_path = tmpdir.join(sql_filename_spaced)
        sql_filename_spaced_path.write("test")

        migrations = helpers.find_migrations(str(tmpdir))
        assert migrations == [
            (45, str(sql_filename_expected_filepath)),
            (23514352834592347502351435283459234750,
             str(sql_filename_bigint_filepath)),
            (45, str(sql_filename_spaced_path))
        ]

    def test_sort_migrations_expected(
            self, helpers, unsorted_migrations_tuple_list
    ):
        helpers.sort_migrations(unsorted_migrations_tuple_list)
        assert unsorted_migrations_tuple_list == [
            (1, '/tmp/001.createtable.sql'),
            (2, '/tmp/2-createtable.sql'),
            (45, '/tmp/045.createtable.sql'),
            (60, '/tmp/60.createtable.sql'),
        ]

    def test_sort_migrations_not_tuples(
            self, helpers, unsorted_migrations_string_list
    ):
        with pytest.raises(TypeError):
            helpers.sort_migrations(unsorted_migrations_string_list)

    def test_sort_migrations_not_versioned_tuples(
            self, helpers, unsorted_migrations_non_versioned_list
    ):
        with pytest.raises(TypeError):
            helpers.sort_migrations(unsorted_migrations_non_versioned_list)

    def test_populate_migrations_calls_find_migrations(
            self, helpers, mocker, tmpdir
    ):
        mocker.patch('migration_runner.helpers.Helpers.find_migrations')

        helpers.populate_migrations(str(tmpdir))

        helpers.find_migrations.assert_called_with(str(tmpdir))

    def test_populate_migrations_calls_sort_migrations(
            self, helpers, mocker, tmpdir, sql_filename_expected
    ):
        sql_filename_expected_filepath = tmpdir.join(sql_filename_expected)
        sql_filename_expected_filepath.write("test")

        mocker.patch('migration_runner.helpers.Helpers.sort_migrations')

        helpers.populate_migrations(str(tmpdir))

        helpers.sort_migrations.assert_called_with(
            [(45, sql_filename_expected_filepath)]
        )

    def test_get_unprocessed_migrations_version_0(
            self, helpers, unsorted_migrations_tuple_list
    ):
        result = helpers.get_unprocessed_migrations(
            0,
            unsorted_migrations_tuple_list
        )
        assert result == unsorted_migrations_tuple_list

    def test_get_unprocessed_migrations_version_10(
            self, helpers, unsorted_migrations_tuple_list
    ):
        expected = [
            (45, '/tmp/045.createtable.sql'),
            (60, '/tmp/60.createtable.sql'),
        ]

        result = helpers.get_unprocessed_migrations(
            10,
            unsorted_migrations_tuple_list
        )

        assert result == expected

    def test_get_unprocessed_migrations_version_59(
            self, helpers, unsorted_migrations_tuple_list
    ):
        expected = [
            (60, '/tmp/60.createtable.sql'),
        ]

        result = helpers.get_unprocessed_migrations(
            59,
            unsorted_migrations_tuple_list
        )

        assert result == expected

    def test_get_unprocessed_migrations_version_60(
            self, helpers, unsorted_migrations_tuple_list
    ):
        expected = []

        result = helpers.get_unprocessed_migrations(
            60,
            unsorted_migrations_tuple_list
        )

        assert result == expected

    def test_get_unprocessed_migrations_version_61(
            self, helpers, unsorted_migrations_tuple_list
    ):
        expected = []

        result = helpers.get_unprocessed_migrations(
            61,
            unsorted_migrations_tuple_list
        )

        assert result == expected

    def test_get_unprocessed_migrations_version_string(
            self, helpers, unsorted_migrations_tuple_list
    ):
        with pytest.raises(ValueError):
            helpers.get_unprocessed_migrations(
                'five',
                unsorted_migrations_tuple_list)
