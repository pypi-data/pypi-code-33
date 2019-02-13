from enum import Enum
from pathlib import Path
from http import HTTPStatus
from os import chdir, makedirs
from http.server import test, SimpleHTTPRequestHandler
from wsgiref.simple_server import make_server

from horetu import Error, Program, wsgi_form
from horetu.annotations import InputBinaryFile, Regex

from .util import hosts, urls, new_password

NAME = 'send-files'

class PrefixedHTTPRequestHandler(SimpleHTTPRequestHandler):
    prefix = ''
    
    def send_head(self):
        if self.path == self.prefix or self.path.startswith(self.prefix + '/'):
            return super(PrefixedHTTPRequestHandler, self).send_head()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, 'File not found')

    def translate_path(self, path):
        if path == self.prefix:
            path = '/'
        elif path.startswith(self.prefix + '/'):
            path = path[(len(self.prefix)+1):]
        else:
            raise ValueError('Password not in path (should have been caught by send_head): %s' % path)
        return super(PrefixedHTTPRequestHandler, self).translate_path(path)

class Direction(Enum):
    publish = 1
    receive = 2
DIRECTION = {'publish': Direction.publish, 'receive': Direction.receive}

def send_files(
        direction: DIRECTION, directory: Path,
        port: int=11000, overwrite=False, password=None,
    ):
    '''
    Start a web server with a file upload form, provide the URL to access the
    files, and save the uploaded files to the specified directory.

    :param direction: "publish" or "receive"
    :param directory: Directory to publish or to receive into
    :param int port: Port to serve the web server on
    :param bool overwrite: Whether to allow an uploaded file to overwrite
        existing files (only applies for "receive" direction)
    :param password: Set the password manually. If you don't set a password,
        a random password will be generated. The password is included in the
        URL, so you don't need to tell anyone that a password is involved.
    '''

    # Inputs
    if direction == Direction.publish:
        if not directory.is_dir():
            msg = 'The source ("%s") must be a directory. Use "." for the current directory.'
            raise Error(msg % directory)
    else:
        if (not overwrite) and directory.exists():
            if any(directory.iterdir()):
                raise Error('The directory already exists. Choose a different destination or set -overwrite.')
        makedirs(directory, exist_ok=True)

    # URL
    if not password:
        password = new_password()
    for url in urls(port, password):
        yield url

    # Serve
    if direction == Direction.publish:
        chdir(directory)
        class ProtectedHTTPRequestHandler(PrefixedHTTPRequestHandler):
            prefix = '/' + password
        test(HandlerClass=ProtectedHTTPRequestHandler, port=port)
    else:
        def endpoint(file: InputBinaryFile):
            '''
            Upload a file.

            :param file: File to send
            '''

            # Get and validate name.
            if file.filename in {'.', '..'}:
                raise Error('The name "%s" is reserved.' % file.filename)
            elif '/' in file.filename:
                raise Error('Name may not include slashes.')

            # Check if file exists.
            outpath = (directory / file.filename)
            if overwrite:
                pass
            elif outpath.exists():
                raise Error('A file named "%s" already exists.' % file.filename)

            # Save
            with outpath.open('wb') as outfile:
                for chunk in file:
                    outfile.write(chunk)

            # Feedback
            return 'The file has been uploaded.'

        application = wsgi_form(Program({password: endpoint}, name=NAME))
        make_server('0.0.0.0', port, application).serve_forever()
