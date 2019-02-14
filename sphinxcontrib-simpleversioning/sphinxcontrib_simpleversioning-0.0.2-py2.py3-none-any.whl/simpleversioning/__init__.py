"""Sphinx extension that allows adding versioned doc links for self-hosting.

Based on sphinxcontrib-versioning by @Robpol86: https://robpol86.github.io/sphinxcontrib-versioning
"""
from __future__ import absolute_import

import os
from collections import namedtuple

from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.errors import SphinxError
from sphinx.jinja2glue import SphinxFileSystemLoader

__author__ = '@natefoo'
__license__ = 'MIT'
__version__ = '0.0.2'

DEFAULT_BANNER = """This document is not for the latest release of %(project)s. You can alternatively <a
href="%(stable_path)s">view this page in the latest release if it exists</a> or <a href="%(stable_root)s">view the top
of the latest release's documentation</a>."""

STATIC_DIR = os.path.join(os.path.dirname(__file__), '_static')
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '_templates')


class Version(namedtuple('Version', ['id', 'name'])):
    def __str__(self):
        return str(self.name)


class Versions(object):
    def __init__(self, versions, context):
        """Initialize a versions list.

        :param list versions: List with mixture of of strings or dictionaries with keys ``id`` and ``name``.
        :param dict context: Jinja2 HTML context.
        """
        self._versions = []
        for v in versions:
            try:
                v.items()
                _v = Version(**v)
            except TypeError as exc:
                raise SphinxError(
                    "Version dictionary is malformed (must have keys `id` and `name`: %s\n%s\n" % (
                            str(v),
                            str(exc)))
            except AttributeError:
                # it's a string
                _v = Version(v, v)
            self._versions.append(_v)
        self._context = context

    def __iter__(self):
        for v in self._versions:
            yield v, self.vpathto(v)

    def __getitem__(self, item):
        """Retrieve a Version from self._versions by any of its attributes."""
        for key in ('id', 'name'):
            for v in self._versions:
                if getattr(v, key, None) == item:
                    return v
        raise KeyError(item)

    def vpathto(self, other_version, document=None):
        """Return relative path to current document in another version. Like Sphinx's pathto().

        :param Version other_version: Version to link to.
        :param str document: Alternate pagename to link to.

        :return: Templated ``simpleversioning_path_template`` path.
        :rtype: str
        """
        pagename = self._context['pagename']
        return self._context['path_template'].format(
            path_to_root='/'.join(['..'] * pagename.count('/')) or '.',
            version=other_version.id,
            pagename=document or pagename,
        ) + '.html'

    def vpathroot(self, other_version):
        """Return relative path to documentation root in another version.

        :param Version other_version: Version to link to.

        :return: Templated ``simpleversioning_path_template`` path to page ``index``.
        :rtype: str
        """
        return self.vpathto(other_version, document='index')


class EventHandlers(object):
    """Hold Sphinx event handlers as static or class methods.
    """

    @staticmethod
    def builder_inited(app):
        """Update the Sphinx builder.

        :param sphinx.application.Sphinx app: Sphinx application object.
        """
        # Add this extension's _templates directory to Sphinx.
        app.builder.templates.pathchain.insert(0, TEMPLATES_DIR)
        app.builder.templates.loaders.insert(0, SphinxFileSystemLoader(TEMPLATES_DIR))
        app.builder.templates.templatepathlen += 1

        # Add versions.html to sidebar.
        if '**' not in app.config.html_sidebars:
            # default_sidebars was deprecated in Sphinx 1.6+, so only use it if possible (to maintain
            # backwards compatibility), else don't use it.
            try:
                app.config.html_sidebars['**'] = StandaloneHTMLBuilder.default_sidebars + ['versions.html']
            except AttributeError:
                app.config.html_sidebars['**'] = ['versions.html']
        elif 'versions.html' not in app.config.html_sidebars['**']:
            app.config.html_sidebars['**'].append('versions.html')

    @classmethod
    def html_page_context(cls, app, pagename, templatename, context, doctree):
        """Update the Jinja2 HTML context, exposes the Versions class instance to it.

        :param sphinx.application.Sphinx app: Sphinx application object.
        :param str pagename: Name of the page being rendered (without .html or any file extension).
        :param str templatename: Page name with .html.
        :param dict context: Jinja2 HTML context.
        :param docutils.nodes.document doctree: Tree of docutils nodes.
        """
        # Get Versions for this page.
        versions = Versions(app.config.simpleversioning_versions, context)

        # Update Jinja2 context.
        context['html_theme'] = app.config.html_theme
        context['path_template'] = app.config.simpleversioning_path_template
        context['versions'] = versions
        context['current_version'] = versions[app.config.simpleversioning_current_version]
        context['stable_version'] = versions[app.config.simpleversioning_stable_version]
        context['vpathto'] = versions.vpathto
        context['vpathroot'] = versions.vpathroot
        context['banner_message'] = app.config.simpleversioning_banner_message

        # Insert banner into body.
        if app.config.simpleversioning_show_banner and 'body' in context:
            parsed = app.builder.templates.render('banner.html', context)
            context['body'] = parsed + context['body']

        # Reset last_updated with file's mtime (will be last git commit authored date).
        if app.config.html_last_updated_fmt is not None:
            file_path = app.env.doc2path(pagename)
            if os.path.isfile(file_path):
                lufmt = app.config.html_last_updated_fmt or getattr(locale, '_')('%b %d, %Y')
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                context['last_updated'] = format_date(lufmt, mtime, language=app.config.language, warn=app.warn)



def setup(app):
    """Called by Sphinx during phase 0 (initialization).

    :param sphinx.application.Sphinx app: Sphinx application object.

    :returns: Extension version.
    :rtype: dict
    """
    # Used internally. For rebuilding all pages when one or versions fail.
    #app.add_config_value('sphinxcontrib_versioning_versions', SC_VERSIONING_VERSIONS, 'html')

    # Needed for banner.
    #app.config.html_static_path.append(STATIC_DIR)
    #app.add_stylesheet('banner.css')

    # Tell Sphinx which config values can be set by the user.
    app.add_config_value('simpleversioning_path_template', '{path_to_root}/../{version}/{pagename}', 'html')
    app.add_config_value('simpleversioning_versions', ['latest', 'master'], 'html')
    app.add_config_value('simpleversioning_current_version', 'latest', 'html')
    app.add_config_value('simpleversioning_stable_version', 'master', 'html')
    app.add_config_value('simpleversioning_show_banner', False, 'html')
    app.add_config_value('simpleversioning_banner_message', DEFAULT_BANNER, 'html')

    # Event handlers.
    app.connect('builder-inited', EventHandlers.builder_inited)
    app.connect('html-page-context', EventHandlers.html_page_context)
    return dict(version=__version__)
