import logging
import os
import sys
import unittest


from seaborn_table.table import SeabornTable

log = logging.getLogger(__file__)

logging.basicConfig(level=logging.DEBUG,
                    format="%(message)s",
                    handlers=[logging.StreamHandler(sys.__stdout__)])

PATH = os.path.split(os.path.abspath(__file__))[0]


class ExampleTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        answer = """
        Behave examples table with the following results::
            | #  | column 1 | col2  | column 3 | output column  | output col2
            | 0  | 1        | Hello | a        |                | 1
            | 1  | 2        | Hello | a        |                | 2
            | 2  | 1        | World | a        |                | 1
            | 3  | 2        | World | a        |                | 2
            | 4  | 2        | Hello | b        |                | 2
            | 5  | 1        | World | b        |                | 1
            | 6  | 2        | World | b        |                | 2
            | 7  | 1        | Hello | c        |                | 1
            | 8  | 2        | Hello | c        |                | 2
            | 9  | 1        | World | c        |                | 1
            | 10 | 2        | World | c        |                | 2
        """.split('::')[-1]
        if isinstance(answer, bytes):
            answer = answer.decode('utf8')
        cls.answer = answer.strip().replace('\n            ', '\n')
        cls.list_of_list = [[r.strip() for r in row.split('|')[1:]]
                            for row in cls.answer.split('\n')]
        cls.list_of_list[0][4] += ' '

    def setUp(self):
        self.maxDiff = None

    def test_pertibate(self):
        def row_filter(**kwargs):
            if (kwargs['column 1'] == 1 and kwargs['column 3'] == 'b' and
                        kwargs['col2'] == 'Hello'):
                return False
            return True

        table = SeabornTable.pertibate_to_obj(
            columns=['#', 'column 1', 'col2', 'column 3', 'output column ',
                     'output col2'],
            pertibate_values={'column 1': [1, 2],
                              'col2': ['Hello', 'World'],
                              'column 3': ['a', 'b', 'c']},
            generated_columns={
                'output col2': lambda **kwargs: kwargs['column 1'],
                '#': lambda _row_index, **kwargs: _row_index},
            filter_func=row_filter,
            deliminator=' | ',
            tab = '| ',
            max_size=100)
        self.assertEqual(self.answer, str(table))
        return table

    def test_sort_by_key(self):
        table = self.test_pertibate()
        table.deliminator = ' | '
        table.tab = '| '
        table.sort_by_key(['column 1', '-column 3'])
        answer = """
            | #  | column 1 | col2  | column 3 | output column  | output col2
            | 7  | 1        | Hello | c        |                | 1
            | 9  | 1        | World | c        |                | 1
            | 5  | 1        | World | b        |                | 1
            | 0  | 1        | Hello | a        |                | 1
            | 2  | 1        | World | a        |                | 1
            | 8  | 2        | Hello | c        |                | 2
            | 10 | 2        | World | c        |                | 2
            | 4  | 2        | Hello | b        |                | 2
            | 6  | 2        | World | b        |                | 2
            | 1  | 2        | Hello | a        |                | 2
            | 3  | 2        | World | a        |                | 2
        """.strip().replace('\n            ', '\n')
        log.debug(str(table))
        self.assertEqual(str(table), answer)

    def test_key_error(self):
        table = SeabornTable(self.list_of_list, deliminator=' | ')
        try:
            missing = table[0]['Missing']
            raise AssertionError("Failed to throw KeyError")
        except KeyError as ex:
            return

    def test_list_of_list(self):
        table = SeabornTable(self.list_of_list, deliminator=' | ',
                             tab='| ')
        log.debug('\nAnswer:\n%s\n\nResult:\n%s\n\n' % (
            self.answer, str(table)))
        self.assertEqual(self.answer, str(table))

    def test_list_of_dict(self):
        columns = self.list_of_list[0]
        list_of_dict = [{k: row[i] for i, k in enumerate(columns)}
                        for row in self.list_of_list[1:]]
        table = SeabornTable(list_of_dict, columns, deliminator=' | ',
                             tab='| ')
        self.assertEqual(self.answer, str(table))

    def test_dict_of_dict(self):
        columns = self.list_of_list[0]
        dict_of_dict = {}
        for i, row in enumerate(self.list_of_list[1:]):
            dict_of_dict[i] = {k: row[i] for i, k in enumerate(columns)}
        table = SeabornTable(dict_of_dict, columns, deliminator=' | ',
                             tab = '| ')
        log.debug('\nAnswer:\n%s\n\nResult:\n%s\n\n' % (
            self.answer, str(table)))
        self.assertEqual(self.answer, str(table))

    def test_dict_of_list(self):
        columns = self.list_of_list[0]
        dict_of_list = {}
        for i, k in enumerate(columns):
            dict_of_list[k] = [row[i] for row in self.list_of_list[1:]]
        table = SeabornTable(dict_of_list, columns, deliminator=' | ',
                             tab = '| ')
        log.debug('\nAnswer:\n%s\n\nResult:\n%s\n\n' % (
            self.answer, str(table)))
        self.assertEqual(self.answer, str(table))
        table.reverse()

    def test_excel_csv(self):
        table = SeabornTable([['aaa', 'a_b_c', 'c'],
                              [1, '2\n2', '3'],
                              ['4', '5', '"Verdi: "Aida""']])
        file_path = os.path.join(PATH, 'test_excel_csv.csv')
        table.obj_to_csv(space_columns=True, file_path=file_path)
        table2 = SeabornTable.csv_to_obj(file_path=file_path)
        table2.naming_convention_columns("underscore")
        log.debug('\nAnswer:\n%s\n\nResult:\n%s\n\n' % (
            str(table), str(table2)))
        self.assertEqual(str(table), str(table2),
                         'Write then Read changed the data')
        os.remove(file_path)

    def test_html(self):
        table = self.test_pertibate()
        answer_file = os.path.join(PATH, 'data', 'test_pertibate.html')
        with open(answer_file, 'r') as f:
            answer = f.read()
        table.obj_to_html(file_path=os.path.join(PATH, 'test_pertibate.html'))
        self.assertEqual(answer, table.obj_to_html())
        os.remove(os.path.join(PATH, 'test_pertibate.html'))

    def test_mark_down(self):
        """
        Tests markdown components by performing a back-and-forth
        translation.
        :return:
        """
        with open(os.path.join(PATH, 'data', 'test.md')) as f:
            prev = f.read()

        test = SeabornTable.mark_down_to_dict_of_obj(
            os.path.join(PATH, 'data', 'test.md'))

        paragraphs = prev.split("####")[1:]
        header = word = text = ''
        for paragraph in paragraphs:
            header, text = paragraph.split('\n', 1)
        testing = str(test[header.strip()].obj_to_mark_down(
            title_columns=False))
        text = text.replace("```\n# comment\n```", "").strip()
        for word in ':- ':
            text = text.replace(word, '')
            testing = text.replace(word, '')
        testing = testing.replace(word, '')
        log.debug('\nAnswer:\n%s\n\nResult:\n%s\n\n' % (text, testing))

        self.assertEqual(text, testing,
                         "Values don't match:\n%s\n%s" % (
                             repr(testing), repr(text)))

    def test_fancy(self):
        expected = SeabornTable.grid_to_obj(os.path.join(
            PATH,'data','test_file.grid'))
        print(str(expected))
        result = SeabornTable.mark_down_to_obj(
            os.path.join(PATH, 'data', 'test_file.md'))

        self.assertEqual(expected.obj_to_grid(), result.obj_to_grid())


if __name__ == '__main__':
    unittest.main()
