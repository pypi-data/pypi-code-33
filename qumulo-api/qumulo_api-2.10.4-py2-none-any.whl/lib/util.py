# Copyright (c) 2012 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

from contextlib import contextmanager

import os.path
import re

def get_bytes(byte_string):
    symbol = { 'KB': 10**3, 'KiB': 2**10,
               'MB': 10**6, 'MiB': 2**20,
               'GB': 10**9, 'GiB': 2**30,
               'TB': 10**12, 'TiB': 2**40,
               'PB': 10**16, 'PiB': 2**50,
               'EB': 10**18, 'EiB': 2**60,}
    if byte_string.isdigit():
        return int(byte_string)
    elif byte_string[-2:] in symbol:
        return int(float(byte_string[0:-2]) * symbol[byte_string[-2:]])
    elif byte_string[-3:] in symbol:
        return int(float(byte_string[0:-3]) * symbol[byte_string[-3:]])
    else:
        raise ValueError("Limit format is not acceptable!")

# Wrapper needed mocking.
# (patching __builtin__.open directly causes issues when running tests)
@contextmanager
def open_file(*args, **kwargs):
    f = open(*args, **kwargs)
    yield f
    f.close()

def bool_from_string(value):
    value = value.lower()
    if value in ['t', 'true', '1', 'yes', 'on', 'enabled']:
        return True
    if value in ['f', 'false', '0', 'no', 'off', 'disabled']:
        return False
    raise ValueError('Unable to convert "%s" to boolean' % value)

figlet_yes_or_no = '''\
__   _______ ____      _   _  ___ ___
\\ \\ / / ____/ ___|    | \\ | |/ _ \\__ \\
 \\ V /|  _| \\___ \\    |  \\| | | | |/ /
  | | | |___ ___) |   | |\\  | |_| |_|
  |_| |_____|____/ or |_| \\_|\\___/(_) '''

def ask(prompt):
    return raw_input('{} '.format(prompt)).strip().lower()

def are_you_sure():
    prompts = ['yes or no?', 'Yes or No?', 'YES or NO?', figlet_yes_or_no]
    times = 0
    answer = ask(prompts[times])
    while answer != 'yes' and answer != 'no':
        times += 1
        answer = ask(prompts[min(times, len(prompts) - 1)])
    return answer == 'yes'

# Join two paths, force basename to be relative
def path_join(dirname, basename):
    if basename.startswith('/'):
        basename = basename[1:]
    return '{}/{}'.format(dirname, basename)

# Emulate UNIX basename behavior: basename('/foo/bar/') => 'bar'
def unix_path_split(path):
    dirname, basename = os.path.split(path)
    if not basename:
        dirname, basename = os.path.split(dirname)
    return (dirname, basename)

def parse_ascii(string, string_type):
    result = ''
    try:
        # str() throws an exception if there are non-ASCII characters.
        # But first 'cast' it as unicode so the escaped characters are detected
        # as such.
        result = str(unicode(string))
    except UnicodeEncodeError:
        # Output a more descriptive error, the unicode chars are being replaced
        # by '?'.
        msg = 'The string "%s" for the %s contains invalid characters'
        raise ValueError(msg % (string.encode('ascii', 'replace'), string_type))
    return result

def get_certificate_from_pem_format_string(content):
    CERT_RE = (
    r'-----BEGIN CERTIFICATE-----\s+' +
    r'([\S\s]*)\s+' +
    r'-----END CERTIFICATE-----')

    match = re.search(CERT_RE, content)
    return match.group(1) if match else None

def get_rsa_private_key_from_pem_format_string(content):
    RSA_PRIV_KEY_RE = (
    r'-----BEGIN RSA PRIVATE KEY-----\s+' +
    r'([\S\s]*)\s+' +
    r'-----END RSA PRIVATE KEY-----')

    match = re.search(RSA_PRIV_KEY_RE, content)
    return match.group(1) if match else None

def tabulate(table, headers=None):
    '''
    Print a pretty table with fixed-width columns.
    @p table A list of rows, which are also lists.  All rows must have the same
         length.
    @p headers A list of column header strings, or "firstrow" to use the first
         row as column headers, or None to not print column headers.
    This implements a subset of the functionality of the tabulate module that's
    in the toolchain.  It is re-implemented to avoid taking that dependency for
    our public CLI package.
    '''

    # Pull the header row out of the table, if it is integrated:
    if headers == 'firstrow':
        headers = table[0]
        table = table[1:]

    # Find the width of each columnn
    if headers:
        col_widths = [max(len(unicode(h)), 1) for h in headers]
    else:
        col_count = len(table[0]) if table else 0
        col_widths = [1] * col_count
    for row in table:
        assert len(row) == len(col_widths)
        col_widths = [max(m, len(unicode(v))) for m, v in zip(col_widths, row)]

    sep = u'  '
    lines = []
    if headers:
        lines.append(sep.join(
            u'{:<{}}'.format(h, w) for h, w in zip(headers, col_widths)))
        lines.append(sep.join(u'=' * w for w in col_widths))
    for row in table:
        lines.append(sep.join(
            u'{:<{}}'.format(v, w) for v, w in zip(row, col_widths)))

    return u'\n'.join(lines)
