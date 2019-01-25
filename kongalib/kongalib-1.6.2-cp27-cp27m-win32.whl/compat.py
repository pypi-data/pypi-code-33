from __future__ import print_function
import sys

PY3K = (sys.version_info[0] > 2)

if PY3K:
	text_base_types = (str,)
	text_type = str
	data_base_types = (bytes,)
	data_type = bytes
	int_types = (int,)

else:
	text_base_types = (basestring,)
	text_type = unicode
	data_base_types = (basestring, buffer)
	data_type = bytes
	int_types = (int, long)


def ensure_text(text, error='replace'):
	if isinstance(text, text_type):
		return text
	return data_type(text).decode('utf-8', error)
