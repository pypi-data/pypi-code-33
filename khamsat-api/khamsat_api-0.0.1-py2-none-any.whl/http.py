# coding: utf-8

from io import BytesIO
import sys
import codecs
import mimetypes
import random
import string

class MultipartFormDataEncoder(object):
	def __init__(self, boundary=None):
		self.boundary = boundary or \
			''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(30))
		self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

	@classmethod
	def u(cls, s):
		if sys.hexversion < 0x03000000 and isinstance(s, str):
			s = s.decode('utf-8')
		if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
			s = s.decode('utf-8')

		return s

	def iter(self, fields, files):
		encoder = codecs.getencoder('utf-8')
		for (key, value) in fields:
			key = self.u(key)
			yield encoder('--{}\r\n'.format(self.boundary))
			yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
			yield encoder('\r\n')
			if isinstance(value, (int, float)):
				value = str(value)
			yield encoder(self.u(value))
			yield encoder('\r\n')
		for (key, filename, contenttype, fd) in files:
			key = self.u(key)
			filename = self.u(filename)
			yield encoder('--{}\r\n'.format(self.boundary))
			yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
			yield encoder('Content-Type: {}\r\n'.format(
				contenttype or mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
			yield encoder('Content-Transfer-Encoding: binary\r\n')
			yield encoder('\r\n')
			yield (fd, len(fd))
			yield encoder('\r\n')
		yield encoder('--{}--\r\n'.format(self.boundary))

	def encode(self, fields, files):
		body = BytesIO()
		for chunk, _ in self.iter(fields, files):
			body.write(chunk)
		return self.content_type, body.getvalue()
