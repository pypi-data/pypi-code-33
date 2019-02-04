class NaeginImage:
    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        self.nsfw = kwargs.get('nsfw')
        self.gif = kwargs.get('gif')