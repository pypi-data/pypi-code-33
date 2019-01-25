import xml.sax
import base64
from datetime import datetime
import subprocess
import re
import uuid
from pathlib import Path
from urllib.parse import quote
import mimetypes
import click

__version__ = '0.1'


def pandoc(data):

    proc = subprocess.Popen(
        ['pandoc', '-t', 'org', '-f', 'html'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    out, err = proc.communicate(data.encode())

    return out.decode('utf-8')


def to_md(data):

    md = pandoc(data)
    md = re.sub("#\\+BEGIN\\_HTML.*?#\\+END\\_HTML",
                ' ', md, flags=re.M | re.S)
    return md


class Resource:

    UNKNOWN = 0

    def __init__(self, encoding):

        self.encoding = encoding or 'base64'
        self.data = []
        self.alt_data = []
        self.members = {}
        self.attrs = {}

    def __setitem__(self, key, value):

        if key == 'data':
            self.data.append(value)
        elif key == 'alternate-data':
            self.alt_data.append(value)
        elif key in self.members:
            self.members[key] += value
        else:
            self.members[key] = value

    def __getitem__(self, key):

        if key == 'data':
            return self.data
        elif key == 'alternate-data':
            return self.alt_data
        elif key in self.members:
            return self.members[key]
        else:
            raise KeyError

    def attr(self, key, value):
        self.attrs[key] = value

    @property
    def name(self):
        """
        Gets a file name if we have one or generates one
        if we don't'. Also makes sure our file names aren't too long.
        """
        if 'file-name' in self.attrs:
            fname = quote(self.attrs['file-name'], safe='')[:128]

        else:
            ext = mimetypes.guess_extension(self.attrs['mime']) \
                  if 'mime' in self.attrs else ''
            fname = f'unknown-{self.UNKNOWN:04d}{ext}'
            self.UNKNOWN += 1

        return fname

    def save(self, pth):

        f = pth / self.name
        data = ''.join(self.data)

        assert self.encoding == 'base64'
        # Raise an exception if we're non the wiser
        bdata = base64.b64decode(data)

        with open(f, 'wb+') as fd:
            fd.write(bdata)

    def __str__(self):

        return f':Attachments: {self.name}\n' \
            f':ID: {self.uuid}'


class Note:

    def __init__(self):

        self.title = None
        self.content = ''
        self.author = None
        self.created = None
        self.updated = None
        self.tags = []
        self.uuid = str(uuid.uuid4())
        self.attrs = {}
        self.resources = []

    def display(self):

        fnames = []
        if len(self.resources) > 0:
            self.tags.append('ATTACH')
            p = Path(f'data/{self.uuid[:2]}/{self.uuid[2:]}')
            if not p.is_dir():
                p.mkdir(parents=True)

            for res in self.resources:
                res.save(p)
                fnames.append(res.name)

        if len(self.tags) > 0:
            tags = f':{":".join(self.tags)}:'
        else:
            tags = ''

        print(f'* {self.title:<70}{tags}')

        print(':PROPERTIES:')
        if self.author:
            print(f':AUTHOR: {self.author}')
        if self.created:
            try:
                d = datetime.strptime(self.created, '%Y%m%dT%H%M%SZ')
            except ValueError:
                d = datetime.now()
            print(f':DATE: {d:%Y-%m-%d %H:%M}')
        if self.title:
            print(f':TITLE: {self.title}')

        if len(fnames) > 0:
            print(f':Attachments: {" ".join(fnames)}')
        print(f':ID: {self.uuid}')
        print(':END:')
        print(to_md(self.content))

        #print(f'updated: {self.updated}')
        #print(f'attributes: {self.attrs}')

        print('\n')


class EnexHandler(xml.sax.ContentHandler):

    def __init__(self):

        self.note = None
        self.resource = None
        self.status = []
        self.stack = []

    def startElement(self, tag, attr):

        self.stack.append(tag)

        if tag == 'note':
            self.note = Note()
        elif tag == 'resource':
            self.resource = Resource(attr.get('encoding'))
            self.note.resources.append(self.resource)

        if tag in (
                'note',
                'note-attributes',
                'resource',
                'resource-attributes'):
            self.status.append(tag)

    def endElement(self, tag):

        self.stack.pop()

        if len(self.status) > 0 and self.status[-1] == tag:
            self.status.pop()

        if tag == 'note':
            self.note.display()
            self.note = None
            self.resource = None
        elif tag == 'resource':
            self.resource = None

    def characters(self, content):

        if len(self.status) == 0:
            return

        if not self.note:
            return

        status = self.status[-1]
        tag = self.stack[-1]

        if status == 'note':
            if tag == 'title':
                self.note.title = content
            elif tag == 'content':
                self.note.content += content
            elif tag == 'created':
                self.note.created = content
            elif tag == 'updated':
                self.note.updated = content
            elif tag == 'tag':
                self.note.tags.append(content)
            else:
                print(f'unexpected element for {status}: {tag}')

        elif status == 'note-attributes':
            self.note.attrs[tag] = content

        elif status == 'resource':
            if tag == 'data':
                if content != '\n':
                    self.resource['data'].append(content)
            elif tag == 'alternate-data':
                if content != '\n':
                    self.resource['alternate-data'].append(content)
            else:
                self.resource[tag] = content

        elif status == 'resource-attributes':
            self.resource.attr(tag, content)

        else:
            print(f'{tag}: {content[:70]}')


@click.group(invoke_without_command=True)
@click.argument('fname', required=False)
@click.option('-v', '--version', is_flag=True, help='show verision')
def cli(fname, version):

    if version:
        print(f'orgenex version {__version__}')

    if fname:
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        parser.setContentHandler(EnexHandler())
        parser.parse(fname)


if __name__ == '__main__':

    cli()
