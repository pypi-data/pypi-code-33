"""
Generic related documents chain.

: `collation`
    The collation to use when querying for results.

: `form_cls`
    The form class used for the listing.

: `hint`
    A hint to use when querying for results.

: `parent_config`
    The manage config class for the related document.

: `parent_field`
    The field against related documents that relates them to the document.

: `parent_projection`
    The projection used when fetching the parent document.

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
from manhattan.formatters.text import upper_first
from manhattan.nav import Nav, NavItem
from mongoframes import ASC, DESC, And, In, InvalidPage, Or, Paginator, Q
from werkzeug.datastructures import MultiDict
from wtforms.widgets import ListWidget

from manhattan.manage.views import factories, utils
from manhattan.manage.views.related import factories as related_factories
from manhattan.manage.views.list import list_chains


__all__ = ['related_list_chains']


# Define the chains
list_chains = list_chains.copy()

# GET
list_chains['get'].links = [
    'config',
    'authenticate',
    'get_parent_document',
    'init_form',
    'validate',
    'search',
    'parent_filter',
    'filter',
    'sort',
    'paginate',
    'form_info',
    'decorate',
    'render_template'
]

# Factory overrides
list_chains.set_link(
    factories.config(
        parent_config=None,
        parent_field=None,
        parent_projection=None,
        form_cls=None,
        projection=None,
        search_fields=None,
        orphans=2,
        per_page=20
    )
)
list_chains.set_link(related_factories.get_parent_document())

# Custom overrides

@list_chains.link
def parent_filter(state):
    """
    Ensure the results are filtered to only display those relating to the
    parent document.
    """
    parent_document = state[state.parent_config.var_name]
    parent_field = state.parent_field or state.parent_config.var_name

    # Apply the query
    if state.query:
        state.query = And(state.query, Q[parent_field] == parent_document)
    else:
        state.query = Q[parent_field] == parent_document

@list_chains.link
def init_form(state):

    # Initialize the form
    form_data = MultiDict(flask.request.args)

    # Remove the parent field value from the request arguments
    parent_field = state.parent_field or state.parent_config.var_name
    parent_value = form_data.pop(parent_field)

    # Initialize the form
    state.form = state.form_cls(
        form_data or None,
        **{parent_field: parent_value}
    )

@list_chains.link
def decorate(state):
    """
    Add decor information to the state (see `utils.base_decor` for further
    details on what information the `decor` dictionary consists of).

    This link adds a `decor` key to the state.
    """
    parent_field = state.parent_field or state.parent_config.var_name
    parent_document = state[state.parent_config.var_name]

    state.decor = utils.base_decor(
        state.parent_config,
        state.manage_config.var_name_plural,
        parent_document
    )

    # Title
    state.decor['title'] = state.parent_config.titleize(parent_document)

    # Breadcrumbs
    if Nav.exists(state.parent_config.get_endpoint('list')):
        state.decor['breadcrumbs'].add(
            utils.create_breadcrumb(state.parent_config, 'list')
        )

    if Nav.exists(state.parent_config.get_endpoint('view')):
        state.decor['breadcrumbs'].add(
            utils.create_breadcrumb(
                state.parent_config,
                'view',
                parent_document
            )
        )

    state.decor['breadcrumbs'].add(
        NavItem(upper_first(state.manage_config.name_plural))
    )

    # Actions
    if Nav.exists(state.manage_config.get_endpoint('add')):
        state.decor['actions'].add(
            NavItem(
                'Add',
                state.manage_config.get_endpoint('add'),
                view_args={parent_field: parent_document._id}
            )
        )

    if Nav.exists(state.manage_config.get_endpoint('order')):
        state.decor['actions'].add(
            NavItem(
                'Order',
                state.manage_config.get_endpoint('order'),
                view_args={parent_field: parent_document._id}
            )
        )

    # Results action
    state.decor['results_action'] = results_action(state.manage_config)


# Utils

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