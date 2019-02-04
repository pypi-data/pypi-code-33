# Copyright (C) 2019 H. Turgut Uyar <uyar@tekir.org>
#
# Derived from the sphinxjp.themes.revealjs project:
#   https://github.com/tell-k/sphinxjp.themes.revealjs
#
# The copyright text for sphinxjp.themes.revealjs is included below.
#
# =============================================================================
# Copyright (c) 2013 tell-k
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# =============================================================================

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import set_classes


class Slide(nodes.General, nodes.Element):
    """Node for a slide."""


class SpeakerNotes(nodes.General, nodes.Element):
    """Node for speaker notes on a slide."""


class SlideDirective(Directive):
    """A directive for generating a slide."""

    has_content = True
    required_arguments = 0
    optional_arguments = 100
    final_argument_whitespace = False

    option_spec = {
        "id": directives.unchanged,
        "class": directives.class_option,
        "noheading": directives.flag,
        "title-heading": lambda t: directives.choice(t, ("h1", "h2", "h3", "h4", "h5", "h6")),
        "subtitle": directives.unchanged_required,
        "subtitle-heading": directives.unchanged,
        "data-autoslide": directives.unchanged,
        "data-transition": directives.unchanged,
        "data-transition-speed": directives.unchanged,
        "data-background": directives.unchanged,
        "data-background-repeat": directives.unchanged,
        "data-background-size": directives.unchanged,
        "data-background-transition": directives.unchanged,
        "data-state": directives.unchanged,
        "data-markdown": directives.unchanged,
        "data-separator": directives.unchanged,
        "data-separator-vertical": directives.unchanged,
        "data-separator-notes": directives.unchanged,
        "data-charset": directives.unchanged,
    }

    def run(self):
        """Build a slide node from this directive."""
        self.assert_has_content()

        set_classes(self.options)

        text = "\n".join(self.content)
        node = Slide(text, **self.options)
        self.add_name(node)

        if "data-markdown" not in self.options:
            self.state.nested_parse(self.content, self.content_offset, node)

        if self.arguments:
            node["title"] = " ".join(self.arguments)

        node["noheading"] = "noheading" in self.options

        return [node]


class SpeakerNotesDirective(Directive):
    """A directive for generating speaker notes."""

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False

    option_spec = {"class": directives.class_option}

    def run(self):
        """Build a speaker notes node from this directive."""
        self.assert_has_content()

        set_classes(self.options)

        text = "\n".join(self.content)
        node = SpeakerNotes(text, **self.options)
        self.add_name(node)

        self.state.nested_parse(self.content, self.content_offset, node)

        return [node]


_MARKDOWN_HEADINGS = {
    "h1": "#",
    "h2": "##",
    "h3": "###",
    "h4": "####",
    "h5": "#####",
    "h6": "######",
}


def visit_slide(self, node):
    """Build start tag for a slide node."""
    section_attrs = {}

    if node.get("id"):
        section_attrs.update({"ids": [node.get("id")]})

    data_attrs = [a for a in SlideDirective.option_spec if a.startswith("data-")]
    for attr in data_attrs:
        if node.get(attr) is not None:
            section_attrs.update({attr: node.get(attr)})

    title = node.get("title") if (not node.get("noheading")) else None
    title_heading = node.get("title-heading", "h2")

    subtitle = node.get("subtitle")
    subtitle_heading = node.get("subtitle-heading", "h3")

    md_slide = node.get("data-markdown")
    if md_slide is not None:
        template = "%(mark)s %(text)s \n"
        title_mark = _MARKDOWN_HEADINGS.get(title_heading)
        subtitle_mark = _MARKDOWN_HEADINGS.get(subtitle_heading)
    else:
        template = "<%(mark)s>%(text)s</%(mark)s>\n"
        title_mark = title_heading
        subtitle_mark = subtitle_heading

    title_text = (template % {"mark": title_mark, "text": title}) if title else None
    subtitle_text = (template % {"mark": subtitle_mark, "text": subtitle}) if subtitle else None

    self.body.append(self.starttag(node, "section", **section_attrs))
    self.body.append('<div class="content">\n')  # for Bulma

    if md_slide is not None:
        if md_slide == "":
            self.body.append("<script type='text/template'>\n")
            if title_text:
                self.body.append(title_text)
            if subtitle_text:
                self.body.append(subtitle_text)
            self.body.append(node.rawsource)
            self.body.append("</script>\n")
    else:
        if title_text:
            self.body.append(title_text)
        if subtitle_text:
            self.body.append(subtitle_text)
        self.set_first_last(node)


def depart_slide(self, node):
    """Build end tag for a slide node."""
    self.body.append("</div>\n")  # for closing the Bulma content div
    self.body.append("</section>\n")


def visit_speaker_note(self, node):
    """Build start tag for a speaker notes node."""
    self.body.append(self.starttag(node, "aside", **{"class": "notes"}))
    self.set_first_last(node)


def depart_speaker_note(self, node):
    """Build end tag for a speaker notes node."""
    self.body.append("</aside>\n")


def setup(app):
    """Add the directives to a Sphinx application.

    :sig: (sphinx.application.Sphinx) -> None
    :param app: Application to add the directives to.
    """
    app.add_node(Slide, html=(visit_slide, depart_slide))
    app.add_node(SpeakerNotes, html=(visit_speaker_note, depart_speaker_note))
    app.add_directive("slide", SlideDirective)
    app.add_directive("speaker-notes", SpeakerNotesDirective)
