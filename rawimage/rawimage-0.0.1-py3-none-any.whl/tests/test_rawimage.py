import unittest
import tempfile
import shutil
import numpy as np
import rawimage


class TestParseFilename(unittest.TestCase):
    def _run_cases(self, cases):
        for filename, expected_result in cases.items():
            if isinstance(expected_result, tuple):
                result = rawimage.parse_filename(filename)
                self.assertIsNotNone(result)
                for expected, actual in zip(expected_result, result):
                    self.assertEqual(expected, actual)
            else:
                self.assertRaises(expected_result, rawimage.parse_filename, filename)
    
    def test_parse_filename_good(self):
        cases = {
            'prefix_32bit_10x20x30' : ('prefix', (30, 20, 10), np.float32),
            'prefix_10x20x30_8bit' : ('prefix', (30, 20, 10), np.uint8),
            'prefix_10x20x30_16bit' : ('prefix', (30, 20, 10), np.float16),
            'prefix_10x20x30_32bit' : ('prefix', (30, 20, 10), np.float32),
            'prefix_10x20x30_64bit' : ('prefix', (30, 20, 10), np.float64)
        }
        self._run_cases(cases)
    
    def test_parse_filename_strange(self):
        cases = {
            'prefix_a_1x_5x_10x20x30_32bit': ('prefix_a_1x_5x', (30, 20, 10), np.float32),
            'prefix-a-1x-5x_10x20x30_16bit': ('prefix-a-1x-5x', (30, 20, 10), np.float16),
            'prefix_10x20x30' : ('prefix', (30, 20, 10), np.uint8),
            '1xAx3_10x20x30': ('1xAx3', (30, 20, 10), np.uint8),
            '10x20x30_16bit' : (None, (30, 20, 10), np.float16)
        }
        self._run_cases(cases)

    def test_parse_filename_wrong(self):
        cases = {
            'prefix_8bit_10x20x30_32bit': RuntimeError
        }
        self._run_cases(cases)


class TestReadWrite(unittest.TestCase):
    def _run_case(self, shape, dtype):
        dirpath = tempfile.mkdtemp("test_rawimage")
        prefix = 'image'
        
        data = (np.random.random(shape) * 100).astype(dtype)
        filepath = rawimage.imsave(dirpath, prefix, data)
        readed_data = rawimage.imread(filepath)
        
        try:
            self.assertIs(data.dtype, readed_data.dtype)
            self.assertEqual(data.size, readed_data.size)
            self.assertSequenceEqual(data.shape, readed_data.shape)
            self.assertListEqual(data.tolist(), readed_data.tolist())
        finally:    
            # Cleenup
            shutil.rmtree(dirpath)

    def test_write_read_1D(self):
        self._run_case(123, np.float32)
    
    def test_write_read_2D(self):
        self._run_case((128, 30), np.uint8)

    def test_write_read_3D(self):
        self._run_case((2, 50, 30), np.float16)

    def test_write_read_4D(self):
        self._run_case((2, 3, 50, 30), np.float32)