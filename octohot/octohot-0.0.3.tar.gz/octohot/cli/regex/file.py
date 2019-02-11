import click


class File(object):
    def __init__(self, filename=None):
        if not filename:
            raise ValueError("filename not be None")

        self.filename = filename
        self.content = ''.join(list(open(self.filename)))

    def line(self, charpos):
        return self.content[0:charpos].count('\n')+1

    def find(self, pattern):
        import re
        return list(re.finditer(pattern, self.content))

    def save(self):
        with open(self.filename, 'w') as f:
            f.write(self.content)

    def replace(self, find, replace, dryrun):
        if dryrun:
            matches = self.find(find)
            for match in matches:
                click.echo("%s: (%s,%s)" % (self.filename, match.start(), match.end()))
        else:
            import re
            self.content = re.sub(find, replace.replace('\\n', '\n'), self.content)
            self.save()
