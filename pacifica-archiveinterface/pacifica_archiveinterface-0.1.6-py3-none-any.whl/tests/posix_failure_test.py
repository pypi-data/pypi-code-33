#!/usr/bin/python
# -*- coding: utf-8 -*-
"""File used to unit test the pacifica archive interface."""
import unittest
import mock
from pacifica.archiveinterface.backends.posix.archive import PosixBackendArchive
from pacifica.archiveinterface.exception import ArchiveInterfaceError


class TestPosixBackendArchive(unittest.TestCase):
    """Test the Posix backend archive."""

    def test_posix_backend_error(self):
        """Test opening a file from posix backend."""
        with self.assertRaises(ArchiveInterfaceError):
            filepath = '1234'
            mode = 'w'
            backend = PosixBackendArchive('/tmp')
            # easiest way to unit test is look at class variable
            # pylint: disable=protected-access
            backend._file = 'none file object'
            backend.open(filepath, mode)
            # pylint: enable=protected-access

    @mock.patch('os.utime')
    def test_posix_file_mod_time_failed(self, mock_utime):
        """Test the correct setting of a file mod time."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        my_file.close()
        mock_utime.side_effect = OSError('Unable to set utime.')
        hit_exception = False
        try:
            my_file.set_mod_time(1000000)
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue("Can't set posix file mod time with error" in str(ex))
        self.assertTrue(hit_exception)

    @mock.patch('os.chmod')
    def test_posix_file_perms_failed(self, mock_chmod):
        """Test the correct setting of a file mod time."""
        filepath = '1235'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        my_file = backend.open(filepath, mode)
        my_file.close()
        hit_exception = False
        mock_chmod.side_effect = OSError('Unable to chmod.')
        try:
            my_file.set_file_permissions()
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue("Can't set posix file permissions with error" in str(ex))
        self.assertTrue(hit_exception)

    def test_posix_backend_failed_write(self):
        """Test writing to a failed file."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open(filepath, mode)

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.write = mock.MagicMock(side_effect=IOError('Unable to Write!'))
        # pylint: enable=protected-access
        hit_exception = False
        try:
            backend.write('write stuff')
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue("Can't write posix file with error" in str(ex))
        self.assertTrue(hit_exception)

    def test_posix_backend_failed_stat(self):
        """Test status to a failed file."""
        filepath = '1234'
        mode = 'r'
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open(filepath, mode)

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.status = mock.MagicMock(side_effect=IOError('Unable to Read!'))
        # pylint: enable=protected-access
        hit_exception = False
        try:
            backend.status()
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue("Can't get posix file status with error" in str(ex))
        self.assertTrue(hit_exception)

    def test_posix_backend_failed_read(self):
        """Test reading to a failed file."""
        filepath = '1234'
        mode = 'r'
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open(filepath, mode)

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.read = mock.MagicMock(side_effect=IOError('Unable to Read!'))
        # pylint: enable=protected-access
        hit_exception = False
        try:
            backend.read(1024)
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue("Can't read posix file with error" in str(ex))
        self.assertTrue(hit_exception)

    def test_posix_backend_failed_fd(self):
        """Test reading to a failed file fd."""
        filepath = '1234'
        mode = 'w'
        backend = PosixBackendArchive('/tmp/')
        # test failed write
        backend.open(filepath, mode)

        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file = None
        # pylint: enable=protected-access
        hit_exception = False
        try:
            backend.write('Something to write')
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Internal file handle invalid' in str(ex))
        self.assertTrue(hit_exception)
        hit_exception = False
        try:
            backend.read(1024)
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Internal file handle invalid' in str(ex))
        self.assertTrue(hit_exception)
        hit_exception = False
        try:
            backend.stage()
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Internal file handle invalid' in str(ex))
        self.assertTrue(hit_exception)
        hit_exception = False
        try:
            backend.status()
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Internal file handle invalid' in str(ex))
        self.assertTrue(hit_exception)

    def test_posix_backend_failed_stage(self):
        """Test reading a file from posix backend."""
        filepath = '1234'
        mode = 'r'
        backend = PosixBackendArchive('/tmp/')
        backend.open(filepath, mode)
        # easiest way to unit test is look at class variable
        # pylint: disable=protected-access
        backend._file.stage = mock.MagicMock(side_effect=IOError('Unable to Stage!'))
        # pylint: enable=protected-access
        hit_exception = False
        try:
            backend.stage()
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Can\'t stage posix file with error' in str(ex))
        self.assertTrue(hit_exception)

    @mock.patch('shutil.move')
    def test_patch_failed(self, mock_move):
        """Test patching file."""
        old_path = '/tmp/1234'
        new_path = '5678'
        mode = 'w'
        mock_move.side_effect = OSError('Unable to move')
        backend = PosixBackendArchive('/tmp')
        my_file = backend.open('1234', mode)
        my_file.close()
        hit_exception = False
        try:
            backend.patch(new_path, old_path)
        except ArchiveInterfaceError as ex:
            hit_exception = True
            self.assertTrue('Can\'t move posix file with error' in str(ex))
        # Error would be thrown on patch so nothing to assert
        self.assertTrue(hit_exception)
