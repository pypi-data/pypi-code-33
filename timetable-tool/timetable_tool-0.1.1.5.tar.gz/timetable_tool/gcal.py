#!/usr/bin/env python
"""Functions for working with Google Calendar's API.

The functions with in offer the ability to grant permission to a google account
using the web browser, create calendars and publish events to that calendar or
any other calendar provided the id is known.

It contains the following public usable classes/functions: (See the function
docstring for further information)

def get_credentials()

def create_calendar(cal_name)

def add_event(event, cal_id)

"""
import datetime
import os
import logging

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

logger = logging.getLogger(__name__)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)

# Scope to authorize
SCOPE = 'https://www.googleapis.com/auth/calendar'
# Path to the client secret (it's located at the same level as this file)
CLIENT_SECRET_FILENAME = os.path.join(__location__, 'client_secret.json')
# Credentials file
CREDENTIALS_FILE = os.path.join(__location__, '.credentials')
# Google API app name
APPLICATION_NAME = 'My Project'
# Prompt for consent
PROMPT = 'consent'


def get_credentials():
    """Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.

    """
    # Load the credentials file from storage ( if it exists )
    store = Storage(CREDENTIALS_FILE)
    # Retrieve the credentials from the file
    credentials = store.get()
    # If they're not there or invlaid then create new ones
    if not credentials or credentials.invalid:
        flow = flow_from_clientsecrets(
            CLIENT_SECRET_FILENAME, SCOPE, prompt=PROMPT
        )
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        # Needed only for compatibility with Python 2.6
        else:
            credentials = tools.run(flow, store)
        logger.debug('Storing credentials to ' + CLIENT_SECRET_FILENAME)

    return credentials


def create_calendar(cal_name):
    """Create a new calendar.

    Create a new calendar of the specified name

    Keyword arguments:
        cal_name -- the name of the calendar to be created

    Returns:
        The id of the newly created calendar

    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # Create a new calendar in Google Calendar
    calendar = {'summary': cal_name, 'timeZone': 'Australia/Perth'}
    created_calendar = service.calendars().insert(body=calendar).execute()
    logger.info('Created calendar: {}'.format(created_calendar['id']))

    return (created_calendar['id'])


def add_event(event, cal_id):
    """Add an event using the Google Calendar API.

    Creates a Google Calendar API service object
    and creates a new event on the user's calendar.

    Keyword arguments:
        event -- compatible event containing information
        cal_id -- id of the calendar to be posted to

    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    event = service.events().insert(calendarId=cal_id, body=event).execute()
    logger.info('Event created: %s' % (event.get('htmlLink')))
