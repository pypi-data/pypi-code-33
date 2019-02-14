import os
from io import StringIO
import sys
from unittest.mock import patch
import pytest
import zml
from zml.core import Template, TemplateLookup
from zml.exceptions import (TemplateNotDefinedException,
                            FileNotLoadedException,
                            IndentationException)
from zml.util import minimise


def run_test(code, target, global_context={}):
    out = zml.render(code, global_context=global_context)
    # print()
    # print(out)
    assert minimise(out) == minimise(target)


class TestZml(object):

    def setup(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        zml.set_base_path(base_path)

    def test_module_render_with_code_param_returns_string(self):
        code = "'ZML'"
        result = zml.render(code)
        assert isinstance(result, str)

    def test_template_render_with_code_param_returns_string(self):
        code = "'ZML'"
        t = Template()
        result = t.render(source=code)
        assert isinstance(result, str)

    def test_template_render_code_with_code_param_returns_string(self):
        code = "'ZML'"
        t = Template()
        result = t.render_source(source=code)
        assert isinstance(result, str)

    def test_template_render_with_template_param_returns_string(self):
        filename = 'test_plain_text.zml'
        t = Template(filename)
        result = t.render()
        assert isinstance(result, str)

    def test_render_accepts_string(self):
        code = "'ZML'"
        result = zml.render(code)
        assert isinstance(result, str)

    @patch('zml.core.Template.render')
    def xtest_render_with_filename_calls_template_render(self, mock_render):
        filename = 'test/test_plain_text.zml'
        zml.render(filename)
        assert mock_render.called is True

    def test_templatelookup_get_template_with_wrong_path_raised_exception(self):
        with pytest.raises(TemplateNotDefinedException):
            templatefile = 'test/doesnotexist.zml'
            lookup = TemplateLookup(['.'])
            lookup.get_template(templatefile)

    def test_templatelookup_get_template_returns_template(self):
        templatefile = 'test_plain_text.zml'
        lookup = TemplateLookup(['.'])
        t = lookup.get_template(templatefile)
        assert isinstance(t, Template)

    def test_render_without_template_raises_exception(self):
        with pytest.raises(TemplateNotDefinedException):
            t = Template()
            t.render()

    def test_render_with_wrong_filename_raises_exception(self):
        with pytest.raises(TemplateNotDefinedException):
            t = Template('some_path_not_exists.zml')
            t.render()

    def test_missing_file_raises_exception(self):
        with pytest.raises(TemplateNotDefinedException):
            t = Template('some_path_not_exists.zml')
            t.render()

    @patch('builtins.open')
    def test_wrong_encoded_file_raises_exception(self, mock_open):
        mock_open.side_effect = IOError
        with pytest.raises(FileNotLoadedException):
            t = Template('test_file_wrong_encoding.zml')
            t.render()

    def test_wrong_indentation_raises_exception(self):
        code = \
"""
*a
  b
    d
 c
    e
"""
        with pytest.raises(IndentationException):
            template = Template(code)
            template.source_to_tree(code)

    def test_attributes(self):
        code = \
"""
        div somekey='somevalue' secondkey='secondvalue'
"""
        target = \
"""
<div somekey="somevalue" secondkey="secondvalue">
</div>
"""
        run_test(code, target)

    def test_attributes2(self):
        code = \
"""
a href='article1.html': 'more'
"""
        target = \
"""
<a href="article1.html">more</a>
"""
        run_test(code, target)

    def test_empty_attributes(self):
        code = \
"""
form:
  input type='text' disabled
"""
        target = \
"""
<form>
  <input type="text" disabled>
</form>
"""
        run_test(code, target)

    def test_all(self):
        code = \
"""
div#myid.someclass.secondclass data_one='first_value' data_two='second_value' selected
"""
        target = \
"""
<div id="myid" class="someclass secondclass" data_one="first_value" data_two="second_value" selected>
</div>
"""
        run_test(code, target)

    def test_id_classes(self):
        code = \
"""
div#myid.someclass.secondclass
"""
        target =  \
"""
<div id="myid" class="someclass secondclass">
</div>
"""
        run_test(code, target)

    def test_inline_content(self):
        code = \
"""
p: 'Some awesome text'
"""
        target = \
"""
<p>Some awesome text
</p>
"""
        run_test(code, target)

    def test_elements(self):
        code = \
"""
h1: 'One headline'
"""
        target = \
"""
<h1>One headline</h1>
"""
        run_test(code, target)

    def test_multiple(self):
        code = \
"""
p.intro: 'A teaser intro'
h1: 'One headline'
img src='article.jpg'
p: 'Some article text...'
a href='article1.html': 'more'
"""
        target = \
"""
<p class="intro">A teaser intro
</p>
<h1>One headline</h1>
<img src="article.jpg">
<p>Some article text...
</p>
<a href="article1.html">more</a>
"""
        run_test(code, target)

    def test_inline_semantics(self):
        code = \
"""
p: 'View this <strong.green data-info="cite": simple> rules to assign inline semantics to text.'
"""
        target = \
"""
<p>View this <strong class="green" data-info="cite">simple</strong> rules to assign inline semantics to text.
</p>
"""
        run_test(code, target)

    def test_text_content_nodes(self):
        code = \
"""
p:
  : 'There are some'
  strong: 'simple'
  : 'rules to assign inline semantics to text.'
  : 'This bodytext has some'
  span.highlight:
    em.red data-info='animate': 'important words'
  : 'which are emphasized.'
"""
        target = \
"""
<p>
  There are some
  <strong>simple</strong>
  rules to assign inline semantics to text.
  This bodytext has some
  <span class="highlight">
    <em class="red" data-info="animate">important words</em>
  </span>
  which are emphasized.
</p>
"""
        run_test(code, target)

    def test_nesting_structures(self):
        code = \
"""
div#sidebar:
  div.teaser:
    p.intro: 'A teaser intro'
    h1: 'One headline'
    img src='article.jpg'
    p: 'Some article text'
a href='article1.html': 'more'
"""
        target = \
"""
<div id="sidebar">
  <div class="teaser">
    <p class="intro">A teaser intro
    </p>
    <h1>One headline</h1>
    <img src="article.jpg">
    <p>Some article text
    </p>
  </div>
</div>
<a href="article1.html">more</a>
"""
        run_test(code, target)

    def test_moustache_context_item(self):
        context = {
            'title': 'Some headline in the title variable'
        }
        code = \
"""
h1: '{title}'
"""
        target = \
"""
<h1>{title}</h1>
"""
        target = target.format(title=context['title'])
        run_test(code, target, context)

    def test_moustache_context_item_with_property(self):
        context = {
            'user': {
                'firstname': 'Richard',
                'lastname': 'Langly',
                'email': 'ringo@l4ngly.org'
            }
        }
        code = \
"""
div.card:
  p: '{user.firstname}'
  p: '{user.lastname}'
  p: '{user.email}'

"""
        target = \
"""
<div class="card">
  <p>{firstname}
  </p>
  <p>{lastname}
  </p>
  <p>{email}
  </p>
</div>
"""
        target = target.format(**context['user'])
        run_test(code, target, context)

    def test_inherit_template(self):
        code = \
"""
#inherit 2col

*col1_content:
  div.panel:
    h1: 'User'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <h1>zml - zero markup language</h1>
    <div class="grid">
      <div class="m66">
        <div class="left">
          <div class="panel">
            <h1>User</h1>
          </div>
        </div>
      </div>
      <div class="m33">
        <div class="right">some sidebar stuff
        </div>
      </div>
    </div>
  </body>
</html>
"""
        run_test(code, target)

    def test_routes(self):
        code = \
"""
#import components
#inherit base

~routes:
  list: '/blog/posts'
  show: '/blog/post/{id}'
  edit: '/blog/post/{id}/edit'

*content:
  ul:
    li:
      base-linkto action='list': 'List'
    li:
      base-linkto action='show' id=1: 'Details'
    li:
      base-linkto action='edit' id=1: 'Edit'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <ul>
      <li>
        <a href="/blog/posts">List</a>
      </li>
      <li>
        <a href="/blog/post/1">Details</a>
      </li>
      <li>
        <a href="/blog/post/1/edit">Edit</a>
      </li>
    </ul>
  </body>
</html>
"""
        run_test(code, target)

    def test_components(self):
        context = {'page': {'title': 'Some title',
                            'stylesheets': ['main.css', 'content.css'],
                            'scripts': ['main.js', 'content.js']
                            },
                   'pages': [
            {'title': 'Page 1'},
            {'title': 'Page 2'},
            {'title': 'Page 3'},
        ]
        }
        code = \
"""
#import components

html:
  head:
    title: 'zml'
    %for style in page.stylesheets:
      base-style src='{style}'
    %for script in page.scripts:
      script src='{script}'
  body:
    base-menu items=.pages
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
    <link rel="stylesheet" type="text/css" href="main.css">
    <link rel="stylesheet" type="text/css" href="content.css">
    <script src="main.js">
    </script>
    <script src="content.js">
    </script>
  </head>
  <body>
    <div class="menu">
      <ul class="navitems">
        <li>Page 1
        </li>
        <li>Page 2
        </li>
        <li>Page 3
        </li>
      </ul>
    </div>
  </body>
</html>
"""
        run_test(code, target, context)

    def test_list_items(self):
        code = \
"""
# import components
# inherit base

$users:
  -
    firstname: 'Richard'
    lastname: 'Langly'
    email: 'ringo@l4ngly.org'
    active: True
  -
    firstname: 'Melvin'
    lastname: 'Frohike'
    email: 'melvin@frohike1.net'
    active: True
  -
    firstname: 'John Fitzgerald'
    lastname: 'Byers'
    email: 'jfb@byers23.org'
    active: True

*content:
  %for user in users:
    div.card:
      %if user.active:
        p: '{user.firstname}'
        p: '{user.lastname}'
        p: '{user.email}'
      %else:
        p: 'The user is not active'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <div class="card">
      <p>Richard
      </p>
      <p>Langly
      </p>
      <p>ringo@l4ngly.org
      </p>
    </div>
    <div class="card">
      <p>Melvin
      </p>
      <p>Frohike
      </p>
      <p>melvin@frohike1.net
      </p>
    </div>
    <div class="card">
      <p>John Fitzgerald
      </p>
      <p>Byers
      </p>
      <p>jfb@byers23.org
      </p>
    </div>
  </body>
</html>
"""
        run_test(code, target)

    def test_data_sections(self):
        code = \
"""
# import components
# inherit base

$users:
  -
    firstname: 'Richard'
    lastname: 'Langly'
    email: 'ringo@l4ngly.org'
    active: True
  -
    firstname: 'Melvin'
    lastname: 'Frohike'
    email: 'melvin@frohike1.net'
    active: True
  -
    firstname: 'John Fitzgerald'
    lastname: 'Byers'
    email: 'jfb@byers23.org'
    active: True

$pages:
  -
    title: 'About'
    url: '/about'
  -
    title: 'Services'
    url: '/services'
  -
    title: 'Contact'
    url: '/contact'

$page:
  stylesheets:
    - 'files/css/base.css'
    - 'files/css/content.css'
  scripts:
    - 'files/js/jquery.js'
    - 'files/js/main.js'

*content:
  %for user in users:
    div.card:
      %if user.active:
        p: '{user.firstname}'
        p: '{user.lastname}'
        p: '{user.email}'
      %else:
        p: 'The user is not active'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <div class="card">
      <p>Richard
      </p>
      <p>Langly
      </p>
      <p>ringo@l4ngly.org
      </p>
    </div>
    <div class="card">
      <p>Melvin
      </p>
      <p>Frohike
      </p>
      <p>melvin@frohike1.net
      </p>
    </div>
    <div class="card">
      <p>John Fitzgerald
      </p>
      <p>Byers
      </p>
      <p>jfb@byers23.org
      </p>
    </div>
  </body>
</html>
"""
        run_test(code, target)

    def test_data_property_accessors(self):
        code = \
"""
# import components
# inherit base

$test1:
  test2:
    test3: 4+3

*content:
  div: '{test1.test2.test3}'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <div>7
    </div>
  </body>
</html>
"""
        run_test(code, target)

    def test_translations(self):
        code = \
"""
#import components
#inherit base

!en:
  labels:
    title: 'Title'
    date: 'Date'
    bodytext: 'Bodytext'
  save: 'Save'
!de:
  labels:
    title: 'Titel'
    date: 'Datum'
    bodytext: 'Haupttext'
  save: 'Speichern'

*content:
  form:
    div.formrow:
      label: !labels.title
      input type='text' name='title'
    div.formrow:
      label: !labels.bodytext
      textarea name='bodytext'
    button type='submit': !save

"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <form>
      <div class="formrow">
        <label>Title</label>
        <input type="text" name="title">
      </div>
      <div class="formrow">
        <label>Bodytext</label>
        <textarea name="bodytext">
        </textarea>
      </div>
      <button type="submit">Save</button>
    </form>
  </body>
</html>
"""
        run_test(code, target)

    def test_models(self):
        code = \
"""
#import components
#inherit base

!en:
  labels:
    title: 'Title'
    date: 'Date'
    bodytext: 'Bodytext'
  buttons:
    save: 'Save'
!de:
  labels:
    title: 'Titel'
    date: 'Datum'
    bodytext: 'Haupttext'
  buttons:
    save: 'Speichern'

+post:
  .title:
    @label: !labels.title
    @type: 'str'
  .date:
    @label: !labels.date
    @type: 'datetime'
  .bodytext:
    @label: !labels.bodytext
    @type: 'str'


*content:
  base-form model=+post
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <form>
      <div class="formrow">
        <label>Title</label>
        <input type="text" name="title">
      </div>
      <div class="formrow">
        <label>Date</label>
        <input type="text" name="date">
      </div>
      <div class="formrow">
        <label>Bodytext</label>
        <input type="text" name="bodytext">
      </div>
      <button type="submit">Save</button>
    </form>
  </body>
</html>
"""
        run_test(code, target)

    def test_debug_function(self):
        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        from zml import deb
        from zml.semantic import ELEMENT
        deb(ELEMENT.parseString("h1: 'test'"))
        sys.stdout = sys.__stdout__
        assert 'inline_content' in capturedOutput.getvalue()

    def test_rendering_context_exception(self):
        from zml import RenderingContext
        from zml.exceptions import VariableNotDefinedException
        with pytest.raises(VariableNotDefinedException):
            rc = RenderingContext()
            # create empty local and global context
            rc.local_context = {}
            rc.global_context = {}
            rc.get_var('some_var_not_defined')

    def test_template_rendering_context_exception(self):
        from zml import TemplateRenderingContext
        from zml.exceptions import TranslationNotDefinedException
        trc = TemplateRenderingContext()
        # create empty translations
        trc.translations = {}
        with pytest.raises(TranslationNotDefinedException):
            trc.get_translation('some_translation_not_defined')
        # create single language with empty translations
        trc.translations = {'en': {}}
        with pytest.raises(TranslationNotDefinedException):
            trc.get_translation('some_translation_not_defined')

    def test_template_rendering_context_set_translation(self):
        from zml import TemplateRenderingContext
        trc = TemplateRenderingContext()
        trc.set_translation('en', 'send', 'Send')
        assert trc.translations['en']['send'] == 'Send'

    def test_tree_node_set_ancestor(self):
        from zml import TreeNode
        ancestor = TreeNode()
        child = TreeNode('', is_root=False, is_ancestor=False, ancestor=ancestor)
        assert child.ancestor == ancestor

    def test_treenode_repr(self):
        from zml import TreeNode
        capturedOutput = StringIO()
        sys.stdout = capturedOutput
        line = "h1: 'test'"
        node = TreeNode(line)
        print(node)
        sys.stdout = sys.__stdout__
        assert line in capturedOutput.getvalue()

    def test_add_children(self):
        from zml import Node, Egg
        root = Node('root', local_context={}, is_root=True, is_ancestor=True)
        root.template = self
        source = \
"""
div:
  p: 'test'
    p: 'test'
"""
        root.add_children([Egg(line) for line in source.splitlines() if line.strip()])

    def test_context_item_model_accessor(self):
        code = \
"""
+post:
  .title:
    @label: 'Title'
    @type: 'str'
$data: +post
"""
        zml.render(code)

    def test_field_meta_data(self):
        code = \
"""
+post:
  .title:
    @label: 'Title'
    @type: 'str'
p: +post.title@type
"""
        zml.render(code)

    def xtest_code_if_statement(self):
        code = \
"""
# import components
# inherit base

$user_active: True
$user_deleted: False

*content:
  %if user_active:
    p: 'User is active'
  %if user_deleted:
    p: 'User is deleted'
"""
        target = \
"""
<html>
  <head>
    <title>zml</title>
  </head>
  <body>
    <p>User is active
    </p>
  </body>
</html>
"""
        run_test(code, target)
