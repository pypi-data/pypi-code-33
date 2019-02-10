from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.utils.text import slugify
try:

    unicode("test")

except NameError as e:
    #we must be in python 3
    unicode = str



from loremipsum import generate_paragraphs
from mycms.creole import creole2html
from pprint import pformat
import simplejson as json

from django.conf import settings
import shlex


from xml.sax.saxutils import escape

try:
    from pygments import highlight
    from pygments.formatters.html import HtmlFormatter
    PYGMENTS = True
except ImportError:
    PYGMENTS = False

from mycms.creole.shared.utils import get_pygments_lexer, get_pygments_formatter

def html(text):
    """
    Macro tag <<html>>...<</html>>
    Pass-trought for html code (or other stuff)
    """
    return text

#----------------------------------------------------------------------
def  HTML(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    return html(text)


def NEWLINE(*args, **kwargs):
    
    text = kwargs.get("text",0)
    
    text_result = "</br>"
    try:
        numlines = int(text)
        for i in range(numlines):
            text_result += "</br>"
        return text_result;
       
    except ValueError as e: 
        return "[[ERROR: NEWLINE tag requires a number. {} was given".format(text)
        
def pre(text):
    """
    Macro tag <<pre>>...<</pre>>.
    Put text between html pre tag.
    """
    return '<pre>%s</pre>' % escape(text)


def code(*args, **kwargs):
    """
    Macro tag <<code ext=".some_extension">>...<</code>>
    If pygments is present, highlight the text according to the extension.
    """

    text = kwargs.get("text", None)
    ext = kwargs.get("ext", ".sh")
    nums = kwargs.get("nums",None)

    if not PYGMENTS:
        return pre(text)

    try:
        source_type = ''
        if '.' in ext:
            source_type = ext.strip().split('.')[1]
        else:
            source_type = ext.strip()
    except IndexError:
        source_type = ''

    lexer = get_pygments_lexer(source_type, text)
    #formatter = get_pygments_formatter()

    try:
        if nums:
            formatter = HtmlFormatter(linenos='table',lineseparator="\n")
        else:
            formatter = HtmlFormatter(lineseparator="\n")
        
        #highlighted_text = highlight(text, lexer, formatter).decode('utf-8')
        #It seems with python3 there is no need to do a decode.
        highlighted_text = highlight(text, lexer, formatter)
    except Exception as e:
        print(e)
        highlighted_text = pre(text)
    #finally:
    #    return highlighted_text.replace('\n', '<br />\n')

    return highlighted_text

#----------------------------------------------------------------------
def  alertblock(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    return template.format(text)

#----------------------------------------------------------------------
def  alerterror(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    template = """<div class="alert alert-error">{}</div>"""
    return template.format(text)

#----------------------------------------------------------------------
def  alertsuccess(*args, **kwargs):
    """"""

    text = kwargs.get("text", None)
    template = """<div class="alert alert-success">{}</div>"""
    return template.format(text)

#----------------------------------------------------------------------
def  alertinfo(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    template = """<div class="alert alert-info">{}</div>"""
    return template.format(text)


#----------------------------------------------------------------------
def H1(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    template = """<a  name="{}"></a><h1 class="multipage-submenu-h1">{}</h2> """

    anchor_text_url = slugify(text)
    return template.format(text, anchor_text_url)


def H2(*args, **kwargs):
    """"""
    text = kwargs.get("text", None)
    template = """<h2 class="multipage-submenu-h2">{}</h2><a name="{}"></a> """
    anchor_text_url = slugify(text)

    return template.format(text, anchor_text_url)



#----------------------------------------------------------------------
def  infoblock(*args, **kwargs):
    """"""

    text = kwargs.get("text", "No text provided.")
    style = kwargs.get("style", "width: 400px; float: right; margin-left:10px")
    image = kwargs.get("image", None)
    author = kwargs.get("author", None)


    if image:
        image = """<div class="quote-photo"><img src="img/temp/user.jpg" alt=""></div>"""
    else:
        image = ""

    if author:
        author = """<div class="quote-author">James Livinston - <span>The New York Post</span></div>"""
    else:
        author=""

    template = """
<div class="boxinfo" style="{}">
        <div class="testimonials-user">{}<p>{}</p>{}</div>
</div>""".format(style,image, text, author)

    return template


#----------------------------------------------------------------------
def  image(*args, **kwargs):
    """
    We parse the content of the text to get the information about the image.
    """

    text = kwargs.get("text", None)
    name = kwargs.get("name", None)
    view = kwargs.get("view", None)
    style = kwargs.get("style", "width:80%")
    path_str = view.path_str



    img_url = "/static/assets/{}/{}".format(view.path_str, name)
    img = """<img src="{}" style="{}" />""".format(img_url, style)

    

    return img


def google_addsense_code(*args, **kwargs):
    
    """"""
    text = kwargs.get("text", None)
    #template = """<h2 class="multipage-submenu-h2">{}</h2><a name="{}"></a> """
    #anchor_text_url = slugify(text)

    if settings.FORCE_SHOW_ADVERTS or (settings.DEBUG == False):
    
        code = """
<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
<!-- 200x200 -->
<ins class="adsbygoogle"
     style="display:inline-block;width:200px;height:200px"
     data-ad-client="ca-pub-9449210019187312"
     data-ad-slot="6494365200"></ins>
<script>
(adsbygoogle = window.adsbygoogle || []).push({});
</script>
	"""
    else:
        code = """<img src="/static/mycms/images/200x200.png">"""
    
    frame = """<div class="frame_200x200" style="float: right;width: 205px;height: 205px;padding-left:15px;">{}</div>""".format(code)
    
    
    return frame

#----------------------------------------------------------------------
def  debug(*args, **kwargs):

    """
    Just a simple example which shows the view's json_data.

    """

    view = kwargs.get("view", None)

    if view is None:
        return "MACRO: Debug did not get a view"

    result =  "Object dictionary: {} ".format(view.json_data)

    return result


########################################################################
class  CreoleFormatter(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, raw_content=None, view=None):
        """Constructor"""
        self.raw_content = raw_content
        self.view = view

    #----------------------------------------------------------------------
    def  html(self, fake_content=False, view=None):
        """Returns the html"""

        if view is None:
            view = self.view

        if fake_content:
            paragraphs = generate_paragraphs(5, start_with_lorem=False)
            p = ""
            for paragraph in paragraphs:
                p =  unicode(paragraph[2]) + "\n\n" + p
            return creole2html(p)



        #The view object is actually passed to the macro being called such that
        #it can manipulate the view object to update it.
        return creole2html(self.raw_content, macros={ "code": code,
                                                   "pre": pre,
                                                   "html": html,
                                                   "HTML":HTML,
                                                   "H1": H1,
                                                   "H2":H2,
                                                   "alertblock":alertblock,
                                                   "alertsuccess":alertsuccess,
                                                   "alertinfo":alertinfo,
                                                   "alerterror":alerterror,
                                                   "infoblock":infoblock,
                                                   "image": image,
                                                   "debug":debug,
                                                   "google_addsense_code":google_addsense_code, 
                                                   "NEWLINE": NEWLINE,
                                                  },
                                           verbose=None,
                                           stderr=None,
                                           view=view)


