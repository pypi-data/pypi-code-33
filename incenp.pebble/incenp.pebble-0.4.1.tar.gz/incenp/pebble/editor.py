# -*- coding: utf-8 -*-
# pebble - Passman client
# Copyright (C) 2018 Damien Goutte-Gattat
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import json
from tempfile import mkstemp


def _edit_file(contents):
    editor = os.getenv('EDITOR', 'vim')
    fh, fn = mkstemp(text=True)
    with os.fdopen(fh, 'w') as fd:
        fd.write(contents)

    os.system('{} {}'.format(editor, fn))

    with open(fn, 'r') as fd:
        edited = fd.read()

    os.unlink(fn)

    return (edited, edited != contents)

def _credential_to_text(credential):
    tags = u','.join([tag[u'text'] for tag in credential['tags']])
    lines = [
            u"# The following field is mandatory",
            u"Label: {}".format(credential['label']),
            u"Description: {}".format(credential['description'] or ''),
            u"# Comma-separated list of tags",
            u"Tags: {}".format(tags),
            u"URL: {}".format(credential['url'] or ''),
            u"Email: {}".format(credential['email'] or ''),
            u"Username: {}".format(credential['username'] or ''),
            u"Password: {}".format(credential['password'])
            ]
    return u'\n'.join(lines)


def _text_to_credential(text, credential):
    for line in text.split('\n'):
        if line.startswith('#'):
            continue
        name, sep, value = line.partition(': ')
        if len(name) == 0:
            continue
        if name == 'Tags':
            tags = []
            for tag in [a for a in value.split(',') if len(a) > 0]:
                tags.append({u'text': tag})
            value = tags

        credential[name.lower()] = value
    return credential


def edit_credential(credential, as_json=False):
    if as_json:
        text = json.dumps(credential, ensure_ascii=False, indent=0)
        edited_text, modified = _edit_file(text)
        if modified:
            return json.loads(edited_text)
    else:
        text = _credential_to_text(credential)
        edited_text, modified = _edit_file(text)
        if modified:
            return _text_to_credential(edited_text, credential)
    return None
