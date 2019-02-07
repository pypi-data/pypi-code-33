#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Testable utilities for ingest."""
from __future__ import print_function
import json
import requests
from .config import get_config


def create_state_response(record):
    """Create the state response body from a record."""
    return {
        'job_id': record.job_id,
        'state': record.state,
        'task': record.task,
        'task_percent': str(record.task_percent),
        'updated': str(record.updated),
        'created': str(record.created),
        'exception': str(record.exception)
    }


def get_unique_id(id_range, mode):
    """Return a unique job id from the id server."""
    uniqueid_url = get_config().get('uniqueid', 'url')
    url = '{0}/getid?range={1}&mode={2}'.format(
        uniqueid_url, id_range, mode)

    req = requests.get(url)
    body = req.text
    info = json.loads(body)
    unique_id = info['startIndex']

    return unique_id
