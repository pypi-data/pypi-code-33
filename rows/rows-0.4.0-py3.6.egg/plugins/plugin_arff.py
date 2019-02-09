# coding: utf-8

# Copyright 2014-2018 Álvaro Justen <https://github.com/turicas/rows/>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.

#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from io import BytesIO

import arff
import rows.fields as fields
from rows.plugins.utils import create_table, get_filename_and_fobj, serialize


def convert_type(FieldType, distinct):
    if FieldType is fields.BoolField:
        return ['true', 'false', '']

    elif distinct:
        return sorted(set([getattr(row, field_name) for row in table]))

    else:
        return {
            fields.IntegerField: 'NUMERIC',
            fields.FloatField: 'NUMERIC',
            fields.DecimalField: 'NUMERIC',
            fields.PercentField: 'STRING',
            fields.BinaryField: 'STRING',
            fields.DateField: 'STRING',
            #fields.DateField: 'DATE {}'.format(fields.DateField.OUTPUT_FORMAT),
            #TODO: fix arff.BadObject: Invalid attribute type "('data_emissao', 'DATE %Y-%m-%d')"
            fields.DatetimeField: 'STRING',  # TODO: export to DATE?
            fields.TextField: 'STRING',
        }[FieldType]

def import_from_arff(filename_or_fobj, encoding='utf-8', *args, **kwargs):
    """Import data from an ARFF (Weka) file

    If a file-like object is provided it MUST be in binary mode, like in
    `open(filename, mode='rb')`.
    """

    filename, fobj = get_filename_and_fobj(filename_or_fobj, mode='rb')

    # TODO: implement
    #reader = ...

    meta = {'imported_from': 'arff',
            'filename': filename,
            'encoding': encoding}
    return create_table(reader, meta=meta, *args, **kwargs)


def export_to_arff(table, filename_or_fobj=None, encoding='utf-8',
                   distinct_fields=None, *args, **kwargs):
    """Export a `rows.Table` to an ARFF (Weka) file

    If a file-like object is provided it MUST be in binary mode, like in
    `open(filename, mode='wb')`.
    If not filename/fobj is provided, the function returns a string with ARFF
    contents.
    """

    # TODO: will work only if table.fields is OrderedDict
    # TODO: should use fobj? What about creating a method like json.dumps?

    if filename_or_fobj is not None:
        _, fobj = get_filename_and_fobj(filename_or_fobj, mode='wb')
    else:
        fobj = BytesIO()

    data = list(serialize(table, *args, **kwargs))

    distinct_fields = distinct_fields or []
    for field_name in distinct_fields:
        if field_name not in table.field_names:
            raise ValueError('Field name "{}" not found'.format(field_name))

    attributes = []
    for field_name, field_type in table.fields.items():
        calculated_type = convert_type(
            field_type,
            field_name in distinct_fields,
        )
        attributes.append((field_name, calculated_type))

    obj = {
        'attributes': attributes,
        'data': data,
        'description': 'Created with rows + lic-arff',
        'relation': table.name,
    }
    fobj.write(arff.dumps(obj).encode(encoding))
    # TODO: export more than one relation

    if filename_or_fobj is not None:
        fobj.flush()
        return fobj
    else:
        fobj.seek(0)
        result = fobj.read()
        fobj.close()
        return result

# ler Autores Javier Dario Restrepo y Luis Manuel Botello
