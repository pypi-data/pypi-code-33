'''
Preprocessor for Foliant documentation authoring tool.
Converts csv data into markdown tables.
'''

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors.utils.combined_options import (Options, CombinedOptions)
from foliant.utils import output

class Preprocessor(BasePreprocessor):
    defaults = {
        'delimiter': ';',
        'padding_symbol': ' ',
        'paddings_number': 1,
    }
    tags = ('csvtable',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('csvtables')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

        self.config = Options(self.options, defaults=self.defaults)

    def _get_column_widths(self, csv_data):
        for column in range(len(csv_data[0])):
            self._column_widths.append(max(len(csv_data[row][column]) for row in range(len(csv_data))))

    def _build_the_table(self, csv_data, options):
        table_data = []
        for row in range(len(csv_data)):
            string = ''
            for i, item in enumerate(csv_data[row]):
                string = string + ''.join(('|', options['padding_symbol']*options['paddings_number'], item, options['padding_symbol'][::-1]*options['paddings_number'], ' ' * (self._column_widths[i] - len(item))))
            string = string + '|\n'
            table_data.append(string)
        string = ''
        for width in self._column_widths:
            string = string + ''.join(('|', '-' * (width+(len(options['padding_symbol'])*options['paddings_number']*2))))
        string = string + '|\n'
        table_data.insert(1, string)
        table_data.append('')
        for item in table_data:
            self._table += item

    def _process_csv(self, content):

        def _sub(block):
            tag_options = Options(self.get_options(block.group('options')))
            options = CombinedOptions({'config': self.options, 'tag': tag_options}, priority='tag')

            if 'src' in options:
                try:
                    with open(self.working_dir / options['src'], 'r') as f:
                        body = f.read().strip()
                except:
                    output(f"Cannot open file {self.working_dir / options['src']}, skipping",
                           quiet=self.quiet)
                    return ''
            else:
                body = block.group('body').strip()

            csv_data = list(body.split('\n'))
            for i, item in enumerate(csv_data):
                csv_data[i] = item.strip().split(options['delimiter'])

            self._column_widths = []
            self._get_column_widths(csv_data)
            self._table = ''
            self._build_the_table(csv_data, options)

            return self._table

        return self.pattern.sub(_sub, content)

    def apply(self):
        self.logger.info('Applying preprocessor')

        for markdown_file_path in self.working_dir.rglob('*.md'):
            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self._process_csv(content)

            with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
