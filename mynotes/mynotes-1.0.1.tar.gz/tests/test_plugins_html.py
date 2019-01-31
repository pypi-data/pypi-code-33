"""Unit test for plugins_html.py."""

import mynotes
import pytest


prms = mynotes.utils.Params(
        'index.md',
        'home.md',
        '.md',
        ['excld1'],
        ['exclf1'],
        True)

tocdata = (
    (([mynotes.constants.PLUGIN_HTML_TOC],  # ignored for _toc
      'file.md',
      '.',  # ignored for _toc
      '# H1\n'
      '## H2\n'
      '### H3'),
     ('**TOC**\n\n'
      '* [H1](#anchor0)\n'
      '\t* [H2](#anchor1)\n'
      '\t\t* [H3](#anchor2)\n'
      '\n'
      '# <a name="anchor0"/>H1\n'
      '## <a name="anchor1"/>H2\n'
      '### <a name="anchor2"/>H3',)
     ),
    (([mynotes.constants.PLUGIN_HTML_TOC],  # ignored for _toc
      'file.md',
      '.',  # ignored for _toc
      '# H1\n'
      '## H2a\n'
      '### H3a\n'
      '## H2b\n'
      '### H3b'),
     ('**TOC**\n\n'
      '* [H1](#anchor0)\n'
      '\t* [H2a](#anchor1)\n'
      '\t\t* [H3a](#anchor2)\n'
      '\t* [H2b](#anchor3)\n'
      '\t\t* [H3b](#anchor4)\n'
      '\n'
      '# <a name="anchor0"/>H1\n'
      '## <a name="anchor1"/>H2a\n'
      '### <a name="anchor2"/>H3a\n'
      '## <a name="anchor3"/>H2b\n'
      '### <a name="anchor4"/>H3b',)
     ),
    (([mynotes.constants.PLUGIN_HTML_TOC],  # ignored for _toc
      prms.index,
      '.',  # ignored for _toc
      '# H1\n'
      '## H2\n'
      '### H3'),
     ('# H1\n'
      '## H2\n'
      '### H3',)
     ),
)

linksdata = (
    # Index file at root dir, should not have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      prms.index,
      '.',
      '...'),
     ('...',)),
    # Index file, should have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      prms.index,
      './dir',
      '...'),
     (f'[Up](../{prms.index}) - [Top](../{prms.index})\n\n...',)),
    # Index file, should have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      prms.index,
      './dir/dir',
      '...'),
     (f'[Up](../{prms.index}) - [Top](../../{prms.index})\n\n...',)),
    # Another file at root dir, should have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      'file.md',
      '.',
      '...'),
     (f'[Up]({prms.index})\n\n...',)),
    # Another file in the tree, should have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      'file.md',
      './dir',
      '...'),
     (f'[Up]({prms.index})\n\n...',)),
    # Another file in the tree, should have links to index
    (([mynotes.constants.PLUGIN_HTML_LINKS_INDEX],  # ignored for _links_index
      'file.md',
      './dir/dir',
      '...'),
     (f'[Up]({prms.index})\n\n...',)),
)

toclinksdata = [
    # Index file at root dir, should not have links to index nor TOC
    ((mynotes.constants.PLUGINS_HTML, prms.index, '.',
      '# H1\n'
      '## H2\n'
      '### H3'),
     ('# H1\n'
      '## H2\n'
      '### H3',)),
    # Index file, should have links to index but no TOC
    ((mynotes.constants.PLUGINS_HTML, prms.index, './dir',
      '# H1\n'
      '## H2\n'
      '### H3'),
     (f'[Up](../{prms.index}) - [Top](../{prms.index})\n\n'
      '# H1\n'
      '## H2\n'
      '### H3',)),
    # Index file, should have links to index but no TOC
    ((mynotes.constants.PLUGINS_HTML, prms.index, './dir/dir',
      '# H1\n'
      '## H2\n'
      '### H3'),
     (f'[Up](../{prms.index}) - [Top](../../{prms.index})\n\n'
      '# H1\n'
      '## H2\n'
      '### H3',)),
    # Another file at root dir, should have links to index and TOC
    ((mynotes.constants.PLUGINS_HTML, 'file.md', '.',
      '# H1\n'
      '## H2\n'
      '### H3'),
     (f'[Up]({prms.index})\n\n'
      '**TOC**\n\n'
      '* [H1](#anchor0)\n'
      '\t* [H2](#anchor1)\n'
      '\t\t* [H3](#anchor2)\n'
      '\n'
      '# <a name="anchor0"/>H1\n'
      '## <a name="anchor1"/>H2\n'
      '### <a name="anchor2"/>H3',)),
    # Another file in the tree, should have links to index
    ((mynotes.constants.PLUGINS_HTML, 'file.md', './dir',
      '# H1\n'
      '## H2\n'
      '### H3'),
     (f'[Up]({prms.index})\n\n'
      '**TOC**\n\n'
      '* [H1](#anchor0)\n'
      '\t* [H2](#anchor1)\n'
      '\t\t* [H3](#anchor2)\n'
      '\n'
      '# <a name="anchor0"/>H1\n'
      '## <a name="anchor1"/>H2\n'
      '### <a name="anchor2"/>H3',)),
    # Another file in the tree, should have links to index
    ((mynotes.constants.PLUGINS_HTML, 'file.md', './dir/dir',
      '# H1\n'
      '## H2\n'
      '### H3'),
     (f'[Up]({prms.index})\n\n'
      '**TOC**\n\n'
      '* [H1](#anchor0)\n'
      '\t* [H2](#anchor1)\n'
      '\t\t* [H3](#anchor2)\n'
      '\n'
      '# <a name="anchor0"/>H1\n'
      '## <a name="anchor1"/>H2\n'
      '### <a name="anchor2"/>H3',)),
]


@pytest.mark.parametrize("inp, exp", tocdata)
def test__toc(inp, exp):
    """Test _toc function."""
    assert mynotes.plugins_html._toc(prms, inp[1], inp[3]) == exp[0]


@pytest.mark.parametrize("inp, exp", linksdata)
def test__links_index(inp, exp):
    """Test _links_index function."""
    r = mynotes.plugins_html._links_index(prms, inp[1], inp[2], inp[3])
    assert r == exp[0]


@pytest.mark.parametrize("inp, exp",
                         list(tocdata) + list(linksdata) + toclinksdata)
def test_generate_plugins_data(inp, exp):
    """Test generate_plugins_data function."""
    r = mynotes.plugins_html.generate_plugins_data(
        prms, inp[0], inp[1], inp[2], inp[3])
    assert r == exp[0]
