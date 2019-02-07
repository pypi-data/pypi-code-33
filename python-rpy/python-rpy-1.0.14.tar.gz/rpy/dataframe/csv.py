# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from rpy.functions import six
from rpy.functions.datastructures import data
from rpy.functions.importutils import import_string_and_call


def fixargs(kw):
    #fix for py2/py3 inconsistency, delimiter must be bytes in py2 and text in py3
    for arg in ('delimiter', 'quotechar', 'escapechar'):
        try:
            if six.PY2 and isinstance(kw[arg], six.text_type):
                kw[arg] = kw[arg].encode('utf-8')
            elif six.PY3 and isinstance(kw[arg], six.binary_type):
                kw[arg] = kw[arg].decode('utf-8')
        except KeyError:
            pass

    return kw

def UnicodeReader(f, **opts):
    return import_string_and_call('unicodecsv.py%i.UnicodeReader' % (six.PY2 and 2 or 3), f, **fixargs(opts))

def UnicodeWriter(f, **opts):
    return import_string_and_call('unicodecsv.py%i.UnicodeWriter' % (six.PY2 and 2 or 3), f, **fixargs(opts))

def get_csv_rows(path, **kwargs):
    if isinstance(path, six.string_types):
        with open(path, six.PY2 and "r" or "rb") as f:
            yield from UnicodeReader(f, **kwargs)
    else:
        yield from UnicodeReader(path, **kwargs)

def get_csv_dicts(path, header_processor = None, data_processor = data, **kwargs):
    lines = get_csv_rows(path, **kwargs)
    if header_processor:
        headers = tuple(map(header_processor, next(lines)))
    else:
        headers = next(lines)
    return (
        data_processor(zip(headers, line))
        for line in lines
    )

def write_to_stream(lines, stream = None, **opts):
    s = stream or six.BytesIO()
    writer = UnicodeWriter(s, **opts)
    for line in lines:
        writer.writerow(line)
    if hasattr(s, 'seek'):
        s.seek(0)
    return s
