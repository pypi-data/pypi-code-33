"""
Generic update SEO meta chain.

: `form_cls`
    The form that will be used to capture and validate the updated details of
    the document (required).

: `projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).
"""

import flask
from manhattan.assets import Asset, transforms
from manhattan.assets.fields import AssetField
from manhattan.assets.validators import AssetType
from manhattan.assets.transforms.base import BaseTransform
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm, fields, validators
from manhattan.nav import Nav, NavItem
from manhattan.manage.views import factories, utils

__all__ = [
    'update_chains',
    'UpdateForm'
]


# Forms

class UpdateForm(BaseForm):

    # Head
    title = fields.StringField(
        'Title',
        render_kw={
            'data-mh-character-count': '',
            'data-mh-character-count--max-characters': 60
        }
    )
    full_title = fields.BooleanField('Full title')
    meta_description = fields.TextAreaField(
        'Meta description',
        render_kw={
            'data-mh-character-count': '',
            'data-mh-character-count--max-characters': 160
        }
    )
    meta_robots = fields.CheckboxField(
        'Meta robots',
        choices=[
            ('Noindex', 'Noindex'),
            ('Index', 'Index'),
            ('Follow', 'Follow'),
            ('Nofollow', 'Nofollow'),
            ('Noimageindex', 'Noimageindex'),
            ('None', 'None'),
            ('Noarchive', 'Noarchive'),
            ('Nocache', 'Nocache'),
            ('Nosnippet', 'Nosnippet')
        ]
    )

    # Sitemap
    exclude_from_sitemap = fields.BooleanField(
        'Exclude from sitemap'
    )
    sitemap_frequency = fields.SelectField(
        'Frequency',
        choices=[
            ('', 'Select...'),
            ('always', 'Always'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
            ('never', 'Never'),
        ]
    )
    sitemap_priority = fields.FloatField(
        'Priority',
        validators=[validators.Optional()]
    )

    # Open graph
    og_title = fields.StringField(
        'Title',
        render_kw={
            'data-mh-character-count': '',
            'data-mh-character-count--max-characters': 90
        }
    )
    og_description = fields.TextAreaField(
        'Description',
        render_kw={
            'data-mh-character-count': '',
            'data-mh-character-count--max-characters': 200
        }
    )
    og_image =  AssetField(
        'Image',
        validators=[AssetType('image')],
        render_kw={
            'data-mh-file-field--file-type': 'image'
        }
    )
    og_audio = fields.StringField(
        'Audio (URL)',
        validators=[validators.Optional(), validators.URL()]
    )
    og_video = fields.StringField(
        'Video (URL)',
        validators=[validators.Optional(), validators.URL()]
    )


# Define the chains
update_chains = ChainMgr()

# GET
update_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'init_form',
    'decorate',
    'render_template'
])

# POST
update_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'init_form',
    'validate',
    [
        [
            'build_form_data',
            'update_document',
            'store_assets',
            'redirect'
        ],
        [
            'decorate',
            'render_template'
        ]
    ]
])

# Define the links
update_chains.set_link(
    factories.config(
        form_cls=UpdateForm,
        og_image_variations={
            'socialcard': [
                transforms.images.Fit(1200, 1200),
                transforms.images.Output('jpg', 75)
            ]
        },
        projection=None
    )
)
update_chains.set_link(factories.authenticate())
update_chains.set_link(factories.get_document())
update_chains.set_link(factories.validate())
update_chains.set_link(factories.store_assets())
update_chains.set_link(factories.render_template('update_seo_meta.html'))
update_chains.set_link(factories.redirect('update_seo_meta', include_id=True))

@update_chains.link
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
    state.decor['breadcrumbs'].add(NavItem('SEO meta'))

@update_chains.link
def init_form(state):
    # Initialize the form
    form_data = None
    if flask.request.method == 'POST':
        form_data = flask.request.form

    # If a document is assign to the state then this is sent as the first
    # argument when initializing the form.
    obj = None
    if state.manage_config.var_name in state:
        obj = state[state.manage_config.var_name].seo_meta

    # Initialize the form
    state.form = state.form_cls(form_data, obj=obj)

@update_chains.link
def build_form_data(state):
    """
    Generate the form data that will be used to update the document.

    This link adds a `form_data` key to the the state containing the initialized
    form.
    """
    state.form_data = state.form.data

@update_chains.link
def update_document(state):
    """Update a document"""

    # Get the initialized document
    document = state[state.manage_config.var_name]
    seo_meta = document.seo_meta

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Get a copy of the frames comparable data before the update
    original = seo_meta.comparable

    # Doesn't support `logged_update`
    for k, v in state.form_data.items():

        # Set empty values to None
        if not v and type(v) not in (float, int):
            v = None

        setattr(seo_meta, k, v)

    seo_meta.update()

    # And comparable difference is stored against the parent document not the
    # SEO meta.
    entry = document.__class__._change_log_cls({
        'type': 'UPDATED',
        'documents': [document],
        'user': state.manage_user
        })
    entry.add_diff(original, seo_meta.comparable)

    # Check there's a change to apply/log
    if entry.is_diff:
        entry.insert()

    # Flash message that the document was updated
    flask.flash('SEO meta updated.'.format(document=document))

@update_chains.link
def store_assets(state):

    # Check that the app supports an asset manager, if not then there's
    # nothing to do.
    if not hasattr(flask.current_app, 'asset_mgr'):
        return
    asset_mgr = flask.current_app.asset_mgr

    # Get the document being added or updated
    document = state[state.manage_config.var_name]
    seo_meta = document.seo_meta

    # Look for asset fields against the document, convert temporary assets to
    # permenant assets and check to changes to the base transform which
    # require any existing variations for the asset to be re-generated.

    new_assets = []
    updated_assets = []

    for field in seo_meta.get_fields():
        value = seo_meta.get(field)

        # We're only interested in fields that hold assets
        if not isinstance(value, Asset):
            continue

        # Check if the asset is new
        if value.temporary:

            # Store the asset permenantly
            flask.current_app.asset_mgr.store(value)

            # Log that we need to
            new_assets.append(field)

            continue

        # Check if the base transforms for the asset have been modified
        if state.form[field].base_transform_modified:
            updated_assets.append(field)

    # Generate variations for new and updated assets
    for field in (new_assets + updated_assets):
        value = seo_meta.get(field)

        variations = {}

        # Check for variations defined against the manage config
        if hasattr(state, field + '_variations'):
            variations = getattr(state, field + '_variations')

        # Check for existing variations (which overide any variation set
        # against the manage config.
        if value.variations:
            for name, variation_asset in value.variations.items():
                variations[name] = [BaseTransform.from_json_type(t)
                    for t in variation_asset.local_transforms]

        # Ensure the draft variation is never updated
        if '--draft--' in variations:
            variations.pop('--draft--')

        if variations:

            # Get the list of base transforms for the asset
            base_transforms = [BaseTransform.from_json_type(t)
                    for t in value.base_transforms]

            # Store variations for the asset
            asset_mgr.generate_variations(
                value,
                variations,
                base_transforms
            )

    # Save any changes to the database
    if new_assets or updated_assets:
        seo_meta.update(*(new_assets + updated_assets))

