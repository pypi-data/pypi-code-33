"""
Generic related documents chain.

: `collation`
    The collation to use when querying for results.

: `hint`
    A hint to use when querying for results.

: `related_manage_config`
    The manage config class for the related document.

: `related_field`
    The field against related documents that relates them to the document.

: `form_cls`
    The form class used for the listing.

: `projection`
    The projection used when requesting results from the database (defaults to
    None which means the detault projection for the frame class will be used).

: `search_fields`
    A list of fields searched when matching the related documents (defaults to
    None which means no results are searched).

: `orphans`
    The maximum number of orphan that can be merged into the last page of
    results (the orphans will form the last page) (defaults to 2).

: `per_page`
    The number of results that will appear per page (defaults to 30).
"""

import re
from urllib.parse import urlencode

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import fields
from manhattan.formatters.text import remove_accents, upper_first
from manhattan.nav import Nav, NavItem
from mongoframes import ASC, DESC, And, In, InvalidPage, Or, Paginator, Q
from werkzeug.datastructures import MultiDict
from wtforms.widgets import ListWidget

from manhattan.manage.views import factories, utils
from manhattan.manage.views.list import list_chains


__all__ = ['related_list_chains']


# Define the chains
related_list_chains = ChainMgr()

# GET
related_list_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'init_form',
    'validate',
    'search',
    'filter',
    'related_filter',
    'sort',
    'paginate',
    'form_info',
    'decorate',
    'render_template'
])


# Define the links
related_list_chains.set_link(factories.config(
    related_manage_config=None,
    related_field=None,
    related_projection=None,
    form_cls=None,
    projection=None,
    search_fields=None,
    orphans=2,
    per_page=20
))
related_list_chains.set_link(factories.authenticate())
related_list_chains.set_link(factories.get_document())
related_list_chains.set_link(list_chains['get'].get_link('validate'))
related_list_chains.set_link(list_chains['get'].get_link('filter'))
related_list_chains.set_link(list_chains['get'].get_link('search'))
related_list_chains.set_link(list_chains['get'].get_link('sort'))
related_list_chains.set_link(list_chains['get'].get_link('form_info'))
related_list_chains.set_link(factories.render_template('related.html'))


def results_action(config):
    """
    Return a function that will generate a link for a result in the listing
    (e.g if someone clicks on a result).
    """

    def results_action(document):

        # See if there's a view link...
        if Nav.exists(config.get_endpoint('view')):
            return Nav.query(
                config.get_endpoint('view'),
                **{config.var_name: document._id}
            )

        # ...else see if there's an update link...
        elif Nav.exists(config.get_endpoint('update')):
            return Nav.query(
                config.get_endpoint('update'),
                **{config.var_name: document._id}
            )

    return results_action

@related_list_chains.link
def decorate(state):
    """
    Add decor information to the state (see `utils.base_decor` for further
    details on what information the `decor` dictionary consists of).

    This link adds a `decor` key to the state.
    """
    document = state[state.manage_config.var_name]
    state.decor = utils.base_decor(
        state.manage_config,
        state.view_type,
        document
    )

    # Title
    state.decor['title'] = state.manage_config.titleize(document)

    # Breadcrumbs
    if Nav.exists(state.manage_config.get_endpoint('list')):
        state.decor['breadcrumbs'].add(
            utils.create_breadcrumb(state.manage_config, 'list')
        )
    if Nav.exists(state.manage_config.get_endpoint('view')):
        state.decor['breadcrumbs'].add(
            utils.create_breadcrumb(state.manage_config, 'view', document)
        )
    state.decor['breadcrumbs'].add(
        NavItem(upper_first(state.related_manage_config.name_plural))
    )

    # Results action
    assert state.related_manage_config, 'No related manage config defined'
    state.decor['results_action'] = results_action(state.related_manage_config)

@related_list_chains.link
def init_form(state):
    """
    Initialize the form for the view.

    This link adds a `form` key to the the state containing the initialized
    form.
    """

    assert state.form_cls, 'No form class defined'

    # Get the document
    document = state[state.manage_config.var_name]

    # Defaults
    defaults = {k: v for k, v in state.form_cls().data.items() if v is not None}

    if 'filters' in defaults and isinstance(defaults['filters'], dict):
        filters_data = defaults.pop('filters')
        for name, value in filters_data.items():
            if value is not None:
                defaults['filters-' + name] = value

    # Build the form data
    form_data = flask.request.args.copy()
    form_data.update(defaults)
    form_data = MultiDict(form_data)

    # Create and populate Base form
    state.form = state.form_cls(form_data)

    # Set the reset URL
    state.form.reset_url = '{0}?{1}={2}'.format(
        flask.request.base_url,
        state.related_field,
        document._id
    )

    # Check for advanced filters form
    if hasattr(state.form, 'filters'):
        if isinstance(state.form.filters, fields.FormField):

            # Create a dictionary of data intended for the filters form
            filters_kwargs = {}
            for k, v in form_data.to_dict().items():
                if k.startswith('filters-'):
                    widget = getattr(state.form.filters, k[8:]).widget
                    if isinstance(widget, ListWidget):
                        filters_kwargs[k[8:]] = form_data.getlist(k)
                    else:
                        filters_kwargs[k[8:]] = v

            # Populate the filters form
            state.form.filters.process(form_data, filters_kwargs)


@related_list_chains.link
def related_filter(state):
    """
    Apply a query that filters the results to just those related to the
    document.
    """
    assert state.related_field, 'No related manage field defined'

    # Get the document
    document = state[state.manage_config.var_name]

    # Apply the query
    if state.query:
        state.query = And(state.query, Q[state.related_field] == document._id)
    else:
        state.query = Q[state.related_field] == document._id

@related_list_chains.link
def paginate(state):
    """
    Select a paginated list of documents from the database.

    This link adds `page` and `paginator` keys to the state containing the
    the paged results and the document paginator.
    """

    # Get the document
    document = state[state.manage_config.var_name]

    # Select the documents in paginated form
    paginator_kw = {
        'per_page': state.per_page,
        'orphans': state.orphans
    }

    if state.related_projection :
        paginator_kw['projection'] = state.related_projection

    if state.sort_by:
        paginator_kw['sort'] = state.sort_by

    if state.collation:
        paginator_kw['collation'] = state.collation

    if state.hint:
        paginator_kw['hint'] = state.hint

    state.paginator = Paginator(
        state.related_manage_config.frame_cls,
        state.query,
        **paginator_kw
        )

    # Select the requested page
    try:
        state.page = state.paginator[state.form.data.get('page', 1)]
    except InvalidPage as e:
        args = {}
        args[state.manage_config.var_name] = str(document._id)
        return flask.redirect(
            flask.url_for(
                flask.request.url_rule.endpoint,
                **args
            )
        )