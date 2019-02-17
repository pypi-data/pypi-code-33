import re


class Message:
    def __init__(self, data):
        self.data = data
        self.content: str = None
        self.author: str = None
        self.status: bool = 0
        self.channel: str = None
        self.command: str = None
        self.capability = None
        self.tags: str = None
        self._debug = 0

        match = re.match(r':([a-z.]+) ([0-9]{3}) ([A-z0-9]+) :(.*)$', self.data)

        if match:
            # GROUPS
            # 1 : author
            # 2 : status
            # 3 : channel
            # 4 : message
            self.author = self.get_author(match.group(1))
            self.status = int(match.group(2))
            self.channel = match.group(3)
            self.content = match.group(4)
            self._debug = 1

            return

        match = re.match(r':([a-z.]+) (CAP \* ACK) :([a-z./]+)$', self.data)

        if match:
            # GROUPS
            # 1 : author
            # 2 : CAP * ACK
            # 3 : capability
            self.author = self.get_author(match.group(1))
            self.content = match.group(2) + ' ' + match.group(3)
            self.capability = match.group(3)
            self._debug = 2

            return

        match = re.match(r':([a-z0-9.]+) ([0-9]{3}) ([A-z0-9\w]+) #([a-z0-9\w]+) :([A-z0-9\s,!./]+)$', self.data)

        if match:
            # GROUPS
            # 1 : author
            # 2 : status
            # 3 : nickname
            # 4 : channel
            # 5 : message
            self.author = self.get_author(match.group(1))
            self.status = int(match.group(2))
            self.channel = match.group(4)
            self.content = match.group(5)
            self._debug = 3

            return

        match = re.match(r'(?:(@\S+) )?:([^\s]+) (CLEARCHAT|CLEARMSG|GLOBALUSERSTATE|PRIVMSG|ROOMSTATE|USERNOTICE|USERSTATE|NOTICE) #([a-z0-9\w]+)(?: :(.+))?', self.data)

        if match:
            # GROUPS
            # 1 : tags
            # 1 : author
            # 2 : command
            # 3 : channel
            # 4 : content
            self.tags = self.get_tags(match.group(1))
            self.author = self.get_author(match.group(2))
            self.command = match.group(3)
            self.channel = match.group(4)
            self.content = match.group(5)
            self._debug = 4

            return

        self.content = self.data

    @staticmethod
    def get_author(author):
        match = re.match(r'([^\s]+)!([^\s]+)@([^\s]+)', author)
        if match is not None:
            author = match.group(1)

        return author

    @staticmethod
    def get_tags(tags):
        #matches = re.findall(r'([a-z\-]+)=([A-z0-9/#\-]+)?;?', tags)
        matches = re.findall(r'([a-z\-]+)=([^;]+)?;?', tags)

        tags = {}
        for match in matches:
            tags[match[0]] = match[1]

        return tags

    def __str__(self):
        return self.content
