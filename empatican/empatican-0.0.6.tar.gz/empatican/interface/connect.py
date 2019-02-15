#!/usr/bin/env python
# Simple E4 Downloader
from getpass import getpass
import json
import logging
import os
import pandas as pd
from random import uniform
import re
import requests
import sys
import time
from tqdm import tqdm
import zipfile

BASE_URL = 'https://www.empatica.com/connect/'
AUTH_URL = BASE_URL + 'authenticate.php'
DOWNLOAD_URL = BASE_URL + 'download.php'
SESSIONS_URL = BASE_URL + 'connect.php/users/{}/sessions'
STUDIES_URL = BASE_URL + 'connect.php/studies'
STUDY_SESSIONS_URL = (BASE_URL + 'connect.php/studies/{study_id}/sessions?' +
                      'from={from}&to={to}')

logger = logging.getLogger(__name__)


def search_or_download(options):
    '''Simple wrapper to open and use a request session

    Parameters
    -----------
        options : dict
            Dictionary with options from :class:`empatican.cli` list or
            download parser (e.g. participant_id, device_id,
            device_assignment). See the :ref:`commandline-reference` for more
            information.
    '''
    if options['participant_id'] and not options['device_assignment']:
        msg = ('Error: A --device-assignment csv table is required if '
               'specifying --participant-id')
        raise ValueError(msg)

    with requests.Session() as req_session:
        _search_or_download(req_session, options)


def _search_or_download(req_session, options):
    '''Main handler for searching and downloading E4 sessions'''
    # Logs in to the E4 connect site and updates req_session in place
    login(req_session)

    # Get a list of all sessions by querying the econnect site (or cache)
    session_list = get_sessions(req_session, json_cache=None, **options)
    session_df = pd.DataFrame(session_list)

    if options['device_assignment']:
        # If device assignment was provided, add a participant_id column inline
        merge_device_assignment(session_df, options['device_assignment'])

    filtered_df = filter_sessions(session_df, options)

    if options['action'] == 'list':
        if options['table_fmt'] == 'tab':
            table_string = filtered_df[options['display_cols']].to_string(
                index=False) + '\n'
        elif options['table_fmt'] == 'csv':
            table_string = filtered_df[options['display_cols']].to_csv(
                index=False)
        else:
            raise ValueError('Format must be either "tab" or "csv"')

        sys.stdout.write(table_string)

    elif options['action'] == 'download':
        for _, row in filtered_df.iterrows():
            try:
                if options['template']:
                    local_filename = build_fname(row, options)
                else:  # Use default within download_session
                    local_filename = default_filename(row)

                if os.path.exists(local_filename):
                    logger.info(
                        'Already downloaded {}.'.format(local_filename))
                else:
                    download_session(
                        row, req_session, local_filename=local_filename)
                    logger.info(
                        'Successfully downloaded {}'.format(local_filename))
                    time.sleep(uniform(.1, 3))
            except OSError as e:
                if os.path.exists(local_filename
                                  ) and not os.path.getsize(local_filename):
                    os.remove(local_filename)
                msg = (
                    'Problem downloading {}:\n\n\t{}\n\n'.format(
                        local_filename, e) +
                    'This usually occurs because your username is in use '
                    'in more than one place. Wait a little while and please '
                    'try again.\n')

                logger.error(msg)
                sys.exit(1)


def filter_sessions(session_df, options):
    '''Create a set of filters to restrict sessions'''

    # Set all option keys as local variables (required by pd.DataFrame.query())
    lcl = locals()
    lcl.update(options)

    full_query = []
    if options.get('device_id'):
        full_query.append("device_id == @device_id")
    if options.get('empatica_id'):
        full_query.append("id == @empatica_id")
    if options.get('participant_id'):
        full_query.append("participant_id == @participant_id")
    if options.get('start_date'):
        full_query.append("start_datetime >= @start_date")
    if options.get('end_date'):
        full_query.append("start_datetime <= @end_date")

    if options.get('n_recent'):
        n_recent = options['n_recent']
    else:
        n_recent = session_df.shape[0]  # (don't tail any)

    # Add in arbirary query string - don't do any checking now
    # Also, don't worry about "@" variable substitution - assume values
    # are included in the query, like: "duration > 60"
    if options.get('query'):
        full_query.append(' & '.join(options['query']))

    # Take the filters and apply them once
    if len(full_query):
        session_df.query(' & '.join(full_query), inplace=True)

    # Filter n recent sessions in place
    session_df = session_df.iloc[-n_recent:]
    return session_df


def merge_device_assignment(session_df, device_assignment_sheet):
    """Add participant_id from device assignment table

    Expects a sheet with columns *participant_id*, *start_date*, *end_date* and
    *device_serial*

    Dates must be fully-valid dates (e.g. including year), Day-Month aren't
    sufficient."""
    csv_df = pd.read_csv(
        device_assignment_sheet, parse_dates=['start_date', 'end_date'])

    # Initialize 'participant_id' column
    session_df.loc[:, 'participant_id'] = None

    # Add participant_id in session from matching assignment rows.
    for row_idx, row in session_df.iterrows():
        search = ((csv_df['device_name'] == row['device_name']) &
                  (csv_df['start_date'] <= row['start_datetime'])
                  & (csv_df['end_date'] >= row['start_datetime']))
        device_assignment_rows = csv_df.loc[search]
        if device_assignment_rows.shape[0] > 0:
            cur_participant_id = '_or_'.join(
                device_assignment_rows['participant_id'].astype(str).values)
            session_df.loc[row_idx, 'participant_id'] = cur_participant_id
        else:
            continue


def build_fname(row, options):
    '''Build an output file from a format.'''
    # TODO Add sanity check format, handle errors
    if not options['template'].endswith('.zip'):
        options['template'] += '.zip'

    try:
        fname = options['template'].format(**row)
    except KeyError as e:
        logger.warning(e)
        raise FormatError(
            "Problem with your template string. "
            "Be sure to use only the following special values: {}".format(
                row.keys()))
    return fname


def login(req_session, login_info=None):
    if not login_info:
        login_info = get_credentials()

    # Login with the session
    response = req_session.post(AUTH_URL, data=login_info)
    if 'dashboard' not in response.url:
        msg = "Couldn't log in {}. Check username/pass and try again.".format(
            login_info['username'])
        raise ValueError(msg)


def get_credentials():
    '''Load username and password from env vars or prompt from terminal'''
    # Check environment variables
    if 'EMPATICA_USER' in os.environ and len(os.environ['EMPATICA_USER']):
        username = os.environ['EMPATICA_USER']
        password = os.environ['EMPATICA_PASS']
    else:  # Prompt from Terminal
        username = input('Empatica Username: ')
        password = getpass('Empatica Password: ')
    return dict(username=username, password=password)


def get_userid(req_session):
    recent_sessions = req_session.get(BASE_URL + 'sessions.php')
    match = re.search('var userId = (\d+)', recent_sessions.text)
    userid = match.groups()[0]
    return userid


def get_sessions(req_session, json_cache='sessions_list.json', **options):
    '''Download or load from cache a list of session dictionaries.
    To avoid any caching, use json_cache=None'''

    logger.info("'Retrieving list of sessions'")

    # Determine the userid if not provided explicitly
    # (one fewer REST call if pre-determined)
    if 'userid' not in options.keys() or not options['userid']:
        userid = get_userid(req_session)
        options['userid'] = userid
        logger.debug('Found user as {}'.format(userid))

    sessions_list_url = SESSIONS_URL.format(options['userid'])
    sessions_list = download_or_load_sessions(req_session, sessions_list_url,
                                              json_cache)

    logger.info('Retrieved {} sessions from "All Sessions" list.'.format(
        len(sessions_list)))

    studies_list = get_study_list(req_session)

    for study in studies_list:
        study_sessions_url = STUDY_SESSIONS_URL.format(
            **{
                'study_id': study['id'],
                'from': 0,
                'to': 999999999999
            })
        if json_cache:
            # Write a separate cache for each study to avoid overwriting
            cache_path = 'study_{}_{}'.format(study['id'], json_cache)
        else:
            cache_path = json_cache  # False
        study_sessions_list = download_or_load_sessions(
            req_session, study_sessions_url, cache_path)
        for study_session in study_sessions_list:
            study_session['study_id'] = study['id']
            study_session['study_name'] = study['name']

        logger.info('Retrieved {} sessions from study list: {}: "{}"'.format(
            len(study_sessions_list), study['id'], study['name']))

        sessions_list.extend(study_sessions_list)

    # Build a frame from all the combined sessions and process it
    # (convert dates), convert label -> device_name... etc.
    session_df = pd.DataFrame(sessions_list)
    clean_sessions(session_df)

    return session_df


def get_study_list(req_session):
    studies_response = req_session.get(STUDIES_URL)
    studies_list = studies_response.json()
    logger.debug('Available studies:')
    logger.debug(['{id}: {name}'.format(**study) for study in studies_list])
    return studies_list


def download_or_load_sessions(req_session, sessions_list_url,
                              json_cache=False):
    '''Grab the full list of sessions from url or cache

    If cache does not exist but is a string, the list of sessions will be
    retrieved and written as json to the cache path.'''

    if json_cache:
        if os.path.exists(json_cache):
            with open(json_cache, 'r') as f:
                sessions_list = json.load(f)
        else:
            sessions_list_response = req_session.get(sessions_list_url)
            sessions_list = sessions_list_response.json()
            with open(json_cache, 'w') as f:
                indent = None
                json.dump(sessions_list, f, indent=indent)

    else:
        sessions_list_response = req_session.get(sessions_list_url)
        sessions_list = sessions_list_response.json()

    return sessions_list


def clean_sessions(session_df):
    '''Perform inplace basic preproc of session frame.'''
    session_df['start_datetime'] = pd.to_datetime(
        session_df['start_time'], unit='s')
    session_df['_duration'] = session_df['duration'].astype(int).apply(
        _pretty_relative_time)

    # Empatica stores hex device names as ints in their site. For all E4
    # devices, convert the "label" into a 5-padded hex string plus "A" prefix
    session_df['device_name'] = session_df['label'].dropna().astype(int).apply(
        "A{0:05x}".format).str.upper()

    session_df.drop(
        columns=['status', 'exit_code'], inplace=True, errors='ignore')

    intcols = ['duration', 'id', 'label', 'start_time']
    for col in intcols:
        session_df[col] = pd.to_numeric(session_df[col], errors='coerce')
    session_df.sort_values(by='start_time', inplace=True)

    # Out of paranoia, check that sessions weren't found multiple times (in
    # multiple study session lists, for example. Not tested yet.)
    duplicated_ids = session_df.loc[session_df['id'].
                                    duplicated(), 'id'].unique()
    if duplicated_ids.any():
        logger.WARN(
            'Session(s) found multiple times: {}'.format(duplicated_ids))


def download_session(physio_session, requests_session, local_filename=None):
    """Download a single session from Empatica Connect

    Parameters
    -----------
    physio_session : Dictlike, pandas row is acceptable
        Session details with metadata keys from empatica connect site. **id**
        is the only required key, but other information may be provided as
        well to automatically create a `empatica connect`-style zip filename,
        e.g. keys 'start_time' and 'device_id'.

    requests_session : :class:requests.Session
        An open and logged-in ``Session``

    local_filename : str, optional
        An optional filename may be provided. If dirname does not exist, it
        will be created recursively. Leave as ``None`` to infer a standard
        filename from ``options`` as ``{start_time}_{device_id}.zip``.

    Returns
    --------

    local_filename : str, default None
        The filename of the zipfile created, regardless of whether the filename
        was inferred or passed in explicitly.

    """
    if not local_filename:
        local_filename = default_filename(physio_session)

    # Recursively create output directory if needed
    local_dirname = os.path.abspath(os.path.dirname(local_filename))
    if not os.path.exists(local_dirname):
        os.makedirs(local_dirname)

    params = dict(id=physio_session['id'])

    if not (os.path.exists(local_filename)
            and os.path.getsize(local_filename)):
        logger.info('Begin downloading {}'.format(local_filename))
        with requests_session.get(
                DOWNLOAD_URL, params=params, stream=True) as stream:
            written_size = 0
            with open(local_filename, 'wb') as f:
                for chunk in tqdm(stream.iter_content(chunk_size=512)):
                    if chunk:
                        try:
                            chunkstr = chunk.decode('utf-8')
                            lost_login = re.search('DOCTYPE html', chunkstr)
                        except UnicodeDecodeError:
                            lost_login = False
                        if lost_login:
                            raise IOError(
                                "Problem reading data from Empatica Connect - "
                                "Please try again later.")

                        written_size += len(chunk)
                        f.write(chunk)

        write_metadata(physio_session, local_filename)
    else:
        logger.debug('{} - already exists'.format(local_filename))
    return local_filename


def default_filename(info):
    return '{start_time}_{device_name}.zip'.format(**info)


def write_metadata(physio_session, local_filename):
    """Append metadata from download to zip"""
    if isinstance(physio_session, pd.Series):
        meta = physio_session.to_dict()
    else:
        meta = physio_session

    if not os.path.getsize(local_filename):
        raise IOError("Attempting to write metadata to an empty zip archive")

    with zipfile.ZipFile(local_filename, 'a') as zh:
        zh.writestr(
            'metadata.json',
            json.dumps(meta, indent=4, sort_keys=True, default=str),
        )


def download(req_session, **options):
    payload = get_credentials()

    # Login with the session
    req_session.post(AUTH_URL, data=payload)

    sessions_list = get_sessions(req_session, options)

    if 'n_recent' in options.keys():
        n_recent = sessions_list.shape[0]

    for _, physio_info in sessions_list.tail(n_recent).iterrows():
        download_session(physio_info, req_session)


def _pretty_relative_time(time_diff_secs):
    '''Originally from: https://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
    Each tuple in the sequence gives the name of a unit, and the number of
    previous units which go into it.
    '''
    weeks_per_month = 365.242 / 12 / 7
    intervals = [('minute', 60), ('hour', 60), ('day', 24), ('week', 7),
                 ('month', weeks_per_month), ('year', 12)]

    unit, number = 'second', abs(time_diff_secs)
    for new_unit, ratio in intervals:
        new_number = float(number) / ratio
        # If the new number is too small, don't go to the next unit.
        if new_number < 2:
            break
        unit, number = new_unit, new_number
    shown_num = int(number)
    return '{} {}'.format(shown_num, unit + ('' if shown_num == 1 else 's'))


class FormatError(Exception):
    pass
