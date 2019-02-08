
import json
import markdown

from copy import deepcopy as copy
from mdx_gfm import GithubFlavoredMarkdownExtension


class Div:
    """"""

    def __init__(self, verbose=False, **kwargs):
        """
        TBD
        """
        # attributes
        self.type = 'Div'
        self.id_name = None
        self.class_name = None
        self.content = None
        self.content_md = None
        self.width = None
        self.is_markdown = False

        for k, v in kwargs.items():
            setattr(self, k, v)
        self.valid = self.check(verbose=verbose)

        # print('T1')
        # print(self.content_md)
        if self.is_markdown:
            md = markdown.Markdown(extensions=[GithubFlavoredMarkdownExtension()])
            # print('********* inside')
            self.content = md.convert(self.content)
            if verbose:
                print('Div {} markdown content converted to html'.format(self.id_name))
        # print('T2')
        # print(self.content_md)
        # print('end T2')

    def check(self, verbose=False):
        isDivProp = any([getattr(self, k) is not None for k in [
            'id_name', 'class_name', 'content', 'width', 'is_markdown']])
        isIdMarkdownDefined = (self.is_markdown and self.id_name) or True
        isDiv = isDivProp and isIdMarkdownDefined
        if verbose:
            print('Div: isDivProp=', isDivProp)
            print('Div: isIdMarkdownDefined=', isIdMarkdownDefined)
            print('Div: isDiv=', isDiv)
        msg = 'Div must contain a div element defined by at least one attribute\n' + \
              'Div id_name must be defined if is_markdown is True'

        assert isDiv, msg

        return True

    def to_dict(self):
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def pprint(self, indent=2):
        d = json.dumps(self.to_dict(), sort_keys=True, indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())
