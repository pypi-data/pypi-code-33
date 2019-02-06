# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

TAB = '  '

class Dump:

    def __init__(self, indent='', access='', value='', bits=None, rows=None):
        if rows is None:
            rows = []

        rows.append(self)

        self.rows = rows

        self.indent = indent
        self.access = access
        self.value = value
        self.memory = b''
        self.cls = ''
        self.bits = bits

    def add_level(self, access='', bits=None):
        indent = self.indent + TAB
        return Dump(indent, access, bits=bits, rows=self.rows)

    def add_row(self, access='', value='', memory=None):
        row = Dump(self.indent, access, value, rows=self.rows)
        if memory is not None:
            row.memory = memory
        return row

    HEADERS = ['Offset', 'Access', 'Value', 'Memory', 'Type']

    @property
    def cells(self):
        try:
            pos, size = self.bits
        except TypeError:
            # bits is None
            bits = ''
        else:
            end = pos + size - 1
            if end == pos:
                bits = f'[{pos}]'
            else:
                bits = f'[{pos}:{pos + size - 1}]'

        return {
            'Offset': bits,  # byte offset prepended later
            'Access': self.indent + self.access,
            'Value': str(self.value),
            'Memory': ' '.join('{:02x}'.format(c) for c in self.memory),
            'Type': self.cls if isinstance(self.cls, str) else self.cls.__qualname__,
        }

    def _get_lines(self):
        rows = list(row.cells for row in self.rows)

        # make bit offset information uniform in length
        if any(cells['Offset'] for cells in rows):
            fmt = '{:%ds}' % max(len(cells['Offset']) for cells in rows)
            for cells in rows:
                cells['Offset'] = fmt.format(cells['Offset'])

        # prepend byte offset
        nbytes = sum(len(row.memory) for row in self.rows)
        offset_template = '{:%dd}' % len(str(nbytes))
        filler = ' ' * len(str(nbytes))
        cursor = 0
        for cells, row in zip(rows, self.rows):
            if row.memory:
                byte_offset = offset_template.format(cursor)
                cursor += len(row.memory)
            else:
                byte_offset = filler
            cells['Offset'] = byte_offset + cells['Offset']

        cell_sizes = [
            max([len(name)] + [len(cells[name]) for cells in rows])
            for name in self.HEADERS]

        border = '+{}+'.format('+'.join('-' * (n + 2) for n in cell_sizes))
        row_template = '|{}|'.format('|'.join(' {:%ds} ' % n for n in cell_sizes))

        yield border
        yield row_template.format(*self.HEADERS)
        yield border
        for cells in rows:
            yield row_template.format(*cells.values())
        yield border

    def get_table(self):
        return '\n'.join(self._get_lines())
