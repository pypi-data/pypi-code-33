#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Test the metadata module."""
import json
from unittest import TestCase
from pacifica.uploader.metadata import MetaData, MetaObj, metadata_encode, metadata_decode, FileObj
from pacifica.uploader.metadata.metadata import FileObjEncoder


class TestMetaData(TestCase):
    """Test the MetaData class."""

    def test_reference_config(self):
        """Test the metadata module for interface."""
        metadata_str = open('test_data/up-metadata.json').read()
        metadata = metadata_decode(metadata_str)
        self.assertTrue(isinstance(metadata, MetaData))

    def test_reference_upload_config(self):
        """Test the uploaded metadata to see if we can parse that."""
        metadata_str = open('test_data/good-md.json').read()
        metadata = metadata_decode(metadata_str)
        self.assertTrue(isinstance(metadata, MetaData))

    def test_encoding(self):
        """Test the metadata encoding with simple example."""
        md_obj = MetaData([MetaObj(destinationTable='blarg')])
        meta_str = metadata_encode(md_obj)
        self.assertTrue(meta_str == '[{"destinationTable": "blarg"}]')

    def test_encoding_with_error(self):
        """Test the metadata encoding with error."""
        hit_exception = False
        try:
            json.dumps(complex('1+2j'), cls=FileObjEncoder)
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_encoding_with_files(self):
        """Test the metadata encoding with simple example."""
        md_obj = MetaData([FileObj(destinationTable='Files')])
        meta_str = metadata_encode(md_obj)
        self.assertTrue(meta_str == '[{"destinationTable": "Files"}]')

    def test_md_setitem(self):
        """Test the delete features of MetaData."""
        mo_obj = MetaObj(destinationTable='blarg', metaID='aboodaba')
        md_obj = MetaData([MetaObj(destinationTable='blah', metaID='blarg')])
        md_obj[0] = mo_obj
        self.assertTrue(len(md_obj) == 1)
        self.assertTrue(md_obj[0] == mo_obj)
        self.assertTrue(md_obj['aboodaba'] == mo_obj)
        hit_exception = False
        try:
            md_obj['blarg']
        except IndexError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_md_setitem_error(self):
        """A FileObj can't be inserted by an ID it doesn't have."""
        md_obj = MetaData([MetaObj(destinationTable='blarg'), MetaObj(
            destinationTable='blarg2', metaID='aboodaba')])
        file_obj = FileObj()
        hit_exception = False
        try:
            md_obj['aboodaba'] = file_obj
        except IndexError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_md_delete(self):
        """Test the delete features of MetaData."""
        mo_obj = MetaObj(destinationTable='blarg', metaID='aboodaba')
        md_obj = MetaData([mo_obj])
        del md_obj[0]
        self.assertFalse(md_obj)
        hit_exception = False
        try:
            md_obj['aboodaba']
        except IndexError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_md_remove(self):
        """Test the delete features of MetaData."""
        mo_obj = MetaObj(destinationTable='blarg', metaID='aboodaba')
        md_obj = MetaData([mo_obj])
        md_obj.remove(mo_obj)
        self.assertFalse(md_obj)
        hit_exception = False
        try:
            md_obj['aboodaba']
        except IndexError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_md_append(self):
        """Test the append features of MetaData."""
        md_obj = MetaData([MetaObj(destinationTable='blarg')])
        md_obj.append(MetaObj(destinationTable='blarg2', metaID='aboodaba'))
        self.assertTrue(len(md_obj) == 2)
        self.assertTrue(md_obj[1] == md_obj['aboodaba'])

    def test_md_extend(self):
        """Test the append features of MetaData."""
        md_obj = MetaData([MetaObj(destinationTable='blarg')])
        md_obj.extend(
            MetaData([MetaObj(destinationTable='blarg2', metaID='aboodaba')]))
        self.assertTrue(len(md_obj) == 2)
        self.assertTrue(md_obj[1] == md_obj['aboodaba'])

    def test_md_pop(self):
        """Test the pop features of MetaData."""
        md_obj = MetaData([MetaObj(destinationTable='blarg'), MetaObj(
            destinationTable='blarg2', metaID='aboodaba')])
        self.assertTrue(len(md_obj) == 2)
        mo_obj = md_obj.pop()
        self.assertTrue(mo_obj.metaID == 'aboodaba')
        hit_exception = False
        try:
            md_obj['abodaba']
        except IndexError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_md_insert(self):
        """Test the insert features of MetaData."""
        md_obj = MetaData([MetaObj(destinationTable='blarg'), MetaObj(
            destinationTable='blarg2', metaID='aboodaba')])
        mo_obj = MetaObj(destinationTable='insert', metaID='inserted')
        md_obj.insert(1, mo_obj)
        self.assertTrue(md_obj[1] == mo_obj)
        self.assertTrue(md_obj['inserted'] == mo_obj)

    def test_error_md_encoding(self):
        """Fail to parse a MetaData object."""
        hit_exception = False
        try:
            metadata_encode(complex('1+2j'))
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_error_mo_encoding(self):
        """Fail to parse a MetaData object."""
        hit_exception = False
        try:
            metadata_encode(MetaData([complex('1+2j')]))
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_error_md_decoding(self):
        """Fail to parse a MetaData object."""
        hit_exception = False
        try:
            metadata_decode('{}')
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)

    def test_error_mo_decoding(self):
        """Fail to parse a MetaData object."""
        hit_exception = False
        try:
            metadata_decode('["blarg"]')
        except TypeError:
            hit_exception = True
        self.assertTrue(hit_exception)
