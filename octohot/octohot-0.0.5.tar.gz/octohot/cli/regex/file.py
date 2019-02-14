import click


class File(object):
    def __init__(self, filename=None):
        if not filename:
            raise ValueError("filename not be None")

        self.filename = filename
        self.content = open(self.filename, 'rb').read()

    def line(self, charpos):
        return self.content.decode()[0:charpos].count('\n')+1

    def find(self, pattern):
        import re
        return list(re.finditer(pattern.encode(), self.content))

    def save(self):
        with open(self.filename, 'wb') as f:
            f.write(self.content)

    def replace(self, find, replace, dryrun):
        if dryrun:
            matches = self.find(find)
            for match in matches:
                click.echo("%s: (%s,%s)" % (self.filename, match.start(), match.end()))
        else:
            import re
            self.content = re.sub(find.encode(), replace.replace('\\n', '\n').encode(), self.content)
            self.save()
