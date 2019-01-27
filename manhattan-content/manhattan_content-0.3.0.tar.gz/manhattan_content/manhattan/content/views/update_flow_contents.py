"""
Generic update contents chain for content flows.

: `content_flows_field`
    The field within the document that contains the content flows (defaults to
    'flows').

"""

import logging
from copy import deepcopy
import json
import re

from bs4 import BeautifulSoup
import cssutils
import flask
from manhattan.assets import Asset
from manhattan.assets.transforms.base import BaseTransform
from manhattan.assets.transforms.images import Fit, Output
from manhattan.chains import Chain, ChainMgr
from manhattan.content.snippets import Snippet
from manhattan.content.views import factories
from manhattan.manage.views import utils as manage_utils
from manhattan.manage.views import factories as manage_factories

cssutils.log.setLevel(logging.CRITICAL)


__all__ = ['update_flow_contents_chains']


# Define the chains
update_flow_contents_chains = ChainMgr()

update_flow_contents_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_flows',
    'get_contents',
    'sync_images',
    'update_contents',
    'update_flows',
    'render_json'
])


# Define the links

update_flow_contents_chains.set_link(
    manage_factories.config(content_flows_field='flows')
)
update_flow_contents_chains.set_link(manage_factories.authenticate())
update_flow_contents_chains.set_link(manage_factories.get_document())
update_flow_contents_chains.set_link(factories.get_contents())

@update_flow_contents_chains.link
def get_flows(state):
    """
    Get the flows that we're applying updates to.

    This link adds `flows` and `original_flows` keys to the state containing the
    flows that are to be updated.
    """

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Get the flows we'll be updating
    state.flows = deepcopy(document.get(state.content_flows_field) or {})
    state.original_flows = deepcopy(state.flows)

    # Ensure all snippets in all flows are `Snippet` instances
    for flow_id, flow in state.flows.items():
        for i, snippet in enumerate(flow):
            if not isinstance(snippet, Snippet):
                flow[i] = Snippet(snippet)

@update_flow_contents_chains.link
def sync_images(state):
    """
    Temporary and permenant images inserted into the contents must be
    synchronized, by which we mean that temporary assets are converted to
    permenant assets and the content variation of the image is resized to
    match the width/height.
    """

    asset_mgr = flask.current_app.asset_mgr
    config = flask.current_app.config
    variation_name = config.get('CONTENT_VARIATION_NAME', 'image')

    # Build a lookup table of all snippets with the page flows
    snippet_lookup = {}
    for flow_id, flow in state.flows.items():
        for snippet in flow:
            snippet_lookup[snippet.id] = snippet

    # Update the images
    for snippet_id, contents in state.contents.items():
        for region, content in contents.items():

            # Parse the content of the region
            soup = BeautifulSoup(content, 'lxml')

            # Find any element within the content that relates to an asset
            asset_tags = soup.find_all(**{'data-mh-asset-key': True})
            sync_asset_tags(snippet_lookup[snippet_id], asset_tags)

            # Save the content of the region back to the snippet
            soup.html.unwrap()
            soup.body.unwrap()
            contents[region] = str(soup)

@update_flow_contents_chains.link
def update_contents(state):
    """Update the contents of snippets with the flows"""

    # Apply the changes
    for flow_id, flow in state.flows.items():
        for snippet in flow:
            if snippet.id not in state.contents:
                continue

            if snippet.scope == 'local':
                # Apply changes to this snippet
                snippet.local_contents.update(state.contents[snippet.id])

            elif snippet.scope == 'global':
                # Apply changes to the global snippet this snippet references
                global_snippet = snippet.global_snippet

                # Update the contents
                global_contents = global_snippet.contents.copy()
                global_contents.update(state.contents[snippet.id])

                # Update the global snippet
                global_snippet.logged_update(
                    state.manage_user,
                    {'contents': global_contents}
                )

                # Clear global snippet cache from the snippet
                snippet._global_snippet_cache = None

@update_flow_contents_chains.link
def update_flows(state):
    """Perform a logged or straight update of flows within the document"""

    # Get the document we're add the snippet to
    document = state[state.manage_config.var_name]

    # Check to see if the frame class supports `logged_update`s
    if hasattr(state.manage_config.frame_cls, 'logged_update'):

        # Logged update
        document.logged_update(
            state.manage_user,
            {state.content_flows_field: state.flows}
        )

    else:
        # Straight update (no logging)
        setattr(document, state.content_flows_field, state.flows)
        document.update(state.content_flows_field)

@update_flow_contents_chains.link
def render_json(state):
    """Render a JSON response for the successful saving of content"""
    return manage_utils.json_success()


# Utils

def sync_asset_tags(snippet, tags):
    """
    Inspect a list of asset (image based) tags for changes and update them as
    required.
    """

    asset_mgr = flask.current_app.asset_mgr
    config = flask.current_app.config
    variation_name = config.get('CONTENT_VARIATION_NAME', 'image')

    # Build a look up table of all assets within the snippet
    contents = snippet.local_contents
    if snippet.scope == 'global':
        contents = snippet.global_snippet.contents
    asset_lookup = {a[0]: a[1] for a in contents.get('__assets__', [])}

    for tag in tags:
        base_transforms = []
        local_transforms = []

        # Cater for the scenario where the element is an image fixture
        img = tag
        if tag.name != 'img':
            img = tag.find('img')

        # Make sure the key has a value
        key = tag['data-mh-asset-key'].strip()
        if not key:
            continue

        # Look for base transforms
        if tag.get('data-mh-base-transforms'):
            base_transforms = json.loads(tag['data-mh-base-transforms'])
            del tag['data-mh-base-transforms']

        # Check for the width of the image, if this has changed it will form
        # part of the local transforms.
        new_width = None
        if img.get('width', '').isdigit() and int(img['width']) > 0:
            new_width = int(img['width'])

        # Look for local transforms
        if tag.get('data-mh-local-transforms'):
            local_transforms = json.loads(tag['data-mh-local-transforms'])
            del tag['data-mh-local-transforms']

        # Find the asset
        if asset_mgr.get_temporary_by_key(key):

            # New asset (store it)
            asset = asset_mgr.get_temporary_by_key(key)
            flask.current_app.asset_mgr.store(asset)

        elif key in asset_lookup:

            # Existing asset
            asset = Asset(asset_lookup[key])

            if base_transforms:

                # If the base transforms are the same as the existing
                # transforms then set the transforms to an empty list.
                new = json.dumps(base_transforms)
                old = json.dumps(asset.base_transforms)
                if new == old:
                    base_transforms = []

            if new_width and not base_transforms:

                # If the new width is the same as the existing width then set
                # width to None.
                variation = asset.variations.get(variation_name)
                if new_width == variation['core_meta']['image']['size'][0]:
                    new_width = None

        else:
            # Asset not found for the given key (ignore the tag)
            continue

        # If the image has a new width then create a local transform for it
        if new_width:
            local_transforms.append(Fit(new_width, 99999).to_json_type())

        # If there are base or local transforms required for the image then
        # generate the require variation.
        if base_transforms or local_transforms:

            # If there are no base transforms check if there are transforms
            # against the asset.
            if not base_transforms:
                base_transforms = asset.base_transforms

            # Add the standard output quality for images to the local
            # transforms if not output quality is set.
            has_output = False
            for local_transform in local_transforms:
                if local_transform['id'] == 'image.output':
                    has_output = True

            if not has_output:
                local_transforms.append(
                    Output(
                        config.get('CONTENT_IMAGE_FORMAT', 'jpg'),
                        config.get('CONTENT_IMAGE_QUALITY', 85)
                    ).to_json_type()
                )

            asset_mgr.generate_variations(
                asset,
                {
                    variation_name: [BaseTransform.from_json_type(t)
                            for t in local_transforms]
                },
                [BaseTransform.from_json_type(t) for t in base_transforms]
            )

        # Update the image URL
        if not isinstance(asset.variations[variation_name], Asset):
            asset.variations[variation_name] = Asset(
                asset.variations[variation_name]
            )

        img['src'] = asset.variations[variation_name].url
        if tag != img:

            # Against image fixtures the URL also needs to be set against the
            # tags background image style.
            style = cssutils.parseStyle(tag['style'])
            del style['background-image']
            style['background-image'] = "url('{0}')".format(img['src'])
            tag['style'] = style.cssText

        # Update the draft URL
        if not isinstance(asset.variations['--draft--'], Asset):
            asset.variations['--draft--'] = Asset(
                asset.variations['--draft--']
            )
        tag['data-mh-draft'] = asset.variations['--draft--'].url

        # Store the updated asset information back in the look up table and
        # snippet.
        asset_lookup[key] = asset.to_json_type()
        contents['__assets__'] = [[k, v] for k, v in asset_lookup.items()]
