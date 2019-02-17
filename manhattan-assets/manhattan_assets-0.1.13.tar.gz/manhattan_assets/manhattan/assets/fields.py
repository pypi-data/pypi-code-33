import json

import flask
from manhattan.forms import fields
from wtforms import widgets

__all__ = (
    'AssetField'
    )


class AssetField(fields.Field):
    """
    A field that supports a file being uploaded.
    """

    widget = widgets.HiddenInput()

    def __init__(self, label=None, validators=None, render_kw=None, **kwargs):

        # Ensure the field is flagged as an asset field
        if not render_kw:
            render_kw = {}

        render_kw['data-mh-file-field'] = True

        # Flag indicating if the asset's base transforms have changed (which
        # would indicate that the asset's variations need to be regenerated).
        self.base_transform_modified = False

        super().__init__(label, validators, render_kw=render_kw, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        elif self.data is not None:
            return json.dumps(self.data.to_json_type())
        return ''

    def process_data(self, value):
        """Process the the fields initial or default value"""
        self.data = value

    def process_formdata(self, values):
        """Process a value(s) submitted to the form"""
        if not values or not values[0]:
            self.data = None
            return

        # Convert the serialized asset JSON to an asset
        asset_data = json.loads(values[0])
        key = asset_data['key']
        base_transforms = asset_data.get('base_transforms')
        user_meta = asset_data.get('user_meta')

        # Check if the asset is a new temporary asset or is the asset initial set
        # for the field.
        if self.data and self.data.key == key:
            asset = self.data

        # If the asset is a temporary asset then attempt to retrieve it's details
        # from the temporary cache.
        else:
            asset = flask.current_app.asset_mgr.get_temporary_by_key(key)

        if not asset:
            self.data = None
            return

        # Set any user defined meta data against the asset
        asset.user_meta = user_meta

        # For the base transforms we perform a comparison to flag that they
        # have been modified and therefore we need to regenerate existing
        # assets.
        old = json.dumps(asset.base_transforms)
        new = json.dumps(base_transforms)
        self.base_transform_modified = old != new

        asset.base_transforms = base_transforms

        # Cater for a preview URI provided client-side (required to provide
        # a preview after the field validates but the form fails to).
        if asset_data.get('preview_uri'):
            asset.preview_uri = asset_data['preview_uri']

        self.data = asset
