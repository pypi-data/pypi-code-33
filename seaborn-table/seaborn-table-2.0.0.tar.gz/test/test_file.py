import os
import shutil
import unittest

from seaborn_table.table import main as cli_converter

PATH = os.path.split(os.path.abspath(__file__))[0]


def file(folder, ext):
    return os.path.join(PATH, folder, 'test_file.%s' % ext)


class FileConversionTest(unittest.TestCase):
    def file_conversion(self, source, dest):
        result_folder = os.path.join(PATH, source)
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        source_file = os.path.join(PATH, 'data', 'test_file.%s' % source)
        cli_converter(source_file, file(source, dest))
        self.cmp_file(source, dest)
        shutil.rmtree(result_folder)

    def cmp_file(self, source, ext):
        self.assertTrue(os.path.exists(file(source, ext)),
                        'File not created: %s'%file(source, ext))
        with open(file('data', ext), 'rb') as fp:
            expected = fp.read().decode('utf-8').replace('\r', '').split('\n')

        with open(file(source, ext), 'rb') as fp:
            result = fp.read().decode('utf-8').replace('\r', '').split('\n')

        for i in range(len(result)):
            self.assertEqual(expected[i], result[i],
                             "Failure creating filetype: %s" % ext)

    def test_txt_to_md(self):
        self.file_conversion('txt', 'md')

    def test_txt_to_csv(self):
        self.file_conversion('txt', 'csv')

    def test_txt_to_txt(self):
        self.file_conversion('txt', 'txt')

    def test_txt_to_html(self):
        self.file_conversion('txt', 'html')

    def test_txt_to_grid(self):
        self.file_conversion('txt', 'grid')

    def test_csv_to_md(self):
        self.file_conversion('csv', 'md')

    def test_csv_to_csv(self):
        self.file_conversion('csv', 'csv')

    def test_csv_to_txt(self):
        self.file_conversion('csv', 'txt')

    def test_csv_to_html(self):
        self.file_conversion('csv', 'html')

    def test_csv_to_grid(self):
        self.file_conversion('csv', 'grid')

    def test_md_to_md(self):
        self.file_conversion('md', 'md')

    def test_md_to_csv(self):
        self.file_conversion('md', 'csv')

    def test_md_to_txt(self):
        self.file_conversion('md', 'txt')

    def test_md_to_html(self):
        self.file_conversion('md', 'html')

    def test_md_to_grid(self):
        self.file_conversion('md', 'grid')

    def test_grid_to_md(self):
        self.file_conversion('grid', 'md')

    def test_grid_to_grid(self):
        self.file_conversion('grid', 'grid')

    def test_grid_to_csv(self):
        self.file_conversion('grid', 'csv')

    def test_grid_to_html(self):
        self.file_conversion('grid', 'html')

    def test_grid_to_txt(self):
        self.file_conversion('grid', 'txt')

if __name__ == '__main__':
    unittest.main()
