from __future__ import absolute_import, division, print_function

# RGBNotes Python bindings
# API docs at https://rgbnotes.com/help?section=api
# Authors:
# Marin Petrov <marin@rgbnotes.com>

# Configuration variables
client_id = None
client_key = None
api_url = 'https://rgbnotes.com/api/v1'
api_version = None
timeout = 30
client_token = None

# Set to either 'debug' or None, controls console logging
log = None

# API resources
from rgbnotes.api_resources import *  # noqa
