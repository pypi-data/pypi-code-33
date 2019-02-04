import base64
from datetime import datetime
import subprocess
import re
import uuid
from pathlib import Path
import mimetypes
import click
import hashlib
from lxml import etree

__version__ = '0.7'


def pandoc(data):

    proc = subprocess.Popen(
        ['pandoc', '-t', 'org', '-f', 'html'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    out, err = proc.communicate(data)

    return out.decode('utf-8')


def to_md(data):

    md = pandoc(data)
    # Strip out superfluous HTML styles
    md = re.sub("#\\+BEGIN\\_HTML.*?#\\+END\\_HTML",
                ' ', md, flags=re.M | re.S)
    # Indent everything by 1
    md = re.sub('^\*', '**', md, flags=re.M)
    return md


class Resource:

    UNKNOWN = 0
    HASH_MAP = {}
    # Used to record which hashes have been referenced from
    # within a document (or at least by h2f)
    INDOC = set()

    def __init__(self, encoding):

        self.encoding = encoding or 'base64'
        self.data = []
        self.alt_data = []
        self.members = {}
        self.attrs = {}
        self.md5 = None

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
            fname = re.sub('[ \t/]', '_', self.attrs['file-name'])

        else:
            ext = mimetypes.guess_extension(self.attrs['mime']) \
                  if 'mime' in self.attrs else ''
            fname = f'unknown-{self.UNKNOWN:04d}{ext}'
            self.UNKNOWN += 1

        return fname


    def save(self, pth):

        f = pth / self.name

        if f.exists():
            # Avoid overwriting files with the same name
            # e-mails seem to have images save with filename 'noname'
            f = pth / f'{uuid.uuid4()}{f.suffix}'

        data = ''.join(self.data)

        assert self.encoding == 'base64'
        # Raise an exception if we're non the wiser
        bdata = base64.b64decode(data)
        self.md5 = hashlib.md5(bdata).hexdigest()
        self.HASH_MAP[self.md5] = str(f)

        with open(f, 'wb+') as fd:
            fd.write(bdata)

    def __str__(self):

        return f':Attachments: {self.name}\n' \
            f':ID: {self.uuid}'


    @classmethod
    def h2f(cls, h):

        cls.INDOC.add(h)
        return cls.HASH_MAP.get(h)

    @property
    def used(self):

        return self.md5 in self.INDOC


def rep_en_media(doc):
    """
    Replaces <en-media> elements with image links to local resources
    if it's an image type
    """
    xml = etree.fromstring(doc)
    for enm in xml.findall('.//en-media'):
        if 'hash' not in enm.attrib:
            continue

        fname = Resource.h2f(enm.attrib['hash'])
        if not fname:
            continue

        if enm.attrib.get('type') in ('image/png', 'image/jpeg', 'image/gif'):
            enm.clear()
            enm.tag = 'img'
            enm.attrib['src'] = fname
        else:
            enm.clear()
            enm.tag = 'a'
            enm.attrib['href'] = fname
            enm.text = fname

    with open('/tmp/test.xml', 'ab+') as f:
        f.write(etree.tostring(xml))

    return etree.tostring(xml)


class Note:

    def __init__(self):

        self.title = ''
        self.content = ''
        self.author = ''
        self.created = None
        self.updated = None
        self.tags = []
        self.uuid = str(uuid.uuid4())
        self.attrs = {}
        self.resources = []

    def display(self, no_media=False, gen_links=False):

        dpath = Path(f'data/{self.uuid[:2]}/{self.uuid[2:]}')
        fnames = []
        if len(self.resources) > 0:
            self.tags.append('ATTACH')
            if not dpath.is_dir():
                dpath.mkdir(parents=True)

            for res in self.resources:
                # Also calculate md5
                res.save(dpath)
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

        if no_media:
            c = self.content.encode()
        else:
            try:
                c = rep_en_media(self.content.encode())
            except etree.XMLSyntaxError:
                # unable to parse the xml, continue silently
                # without conversion
                c = self.content.encode()

        print(to_md(c))

        if gen_links:
            links = []
            for res in self.resources:
                if not res.used:
                    links.append(f'[[{str(dpath / res.name)}]]')
            if len(links) > 0:
                print('** Attachments')
                print('\n'.join(links))

        print('\n')


class EnexHandler:

    def __init__(self, no_media, gen_links):

        self.no_media = no_media
        self.gen_links = gen_links
        self.note = None
        self.resource = None
        self.status = []
        self.stack = []

    def start(self, tag, attr):

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

    def end(self, tag):

        self.stack.pop()

        if len(self.status) > 0 and self.status[-1] == tag:
            self.status.pop()

        if tag == 'note':
            self.note.display(self.no_media, self.gen_links)
            self.note = None
            self.resource = None
        elif tag == 'resource':
            self.resource = None

    def data(self, content):

        if len(self.status) == 0:
            return

        if not self.note:
            return

        status = self.status[-1]
        tag = self.stack[-1]

        if status == 'note':
            if tag == 'title':
                self.note.title += content
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

    def comment(self, text):
        pass

    def close(self):
        pass


@click.group(invoke_without_command=True)
@click.argument('fname', required=False)
@click.option('-v', '--version', is_flag=True, help='show verision')
@click.option('-m', '--no-media', is_flag=True, help='disables conversion of en-media')
@click.option('-l', '--links', is_flag=True, help='disable creation of links to attachments')
def cli(fname, version, no_media, links):

    if version:
        print(f'orgenex version {__version__}')

    if fname:
        parser = etree.XMLParser(
            target=EnexHandler(no_media, not links),
            huge_tree=True
        )
        etree.parse(fname, parser=parser)


if __name__ == '__main__':

    cli()
