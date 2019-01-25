from __future__ import absolute_import, division, print_function

import click
import requests
import os.path
import base64
import urllib
import re
from functools import partial

## Couple of exceptions

class LHError(Exception):
    def __init__(self, message, errors):
        super(Exception, self).__init__(message)
        self.errors = errors

class AuthenticationError(LHError):
    pass

class InvalidEventTypeName(LHError):
    pass

## A little utility to handle directories and regular files

def run_on_directory_or_file(path, action):
    if os.path.isfile(path):
        action(path)
    else:
        for filename in os.listdir(path):
            if filename.endswith('.json') or filename.endswith('.py') or filename.endswith('.sh') or filename.endswith('.csv'):
                try:
                    action(path+'/'+filename)
                except Exception as err:
                    click.echo('Exception caught while processing {}, we keep going: {}'.format(filename, err))
            else:
                click.echo('Skipping {}'.format(filename))
 
@click.group()
def cli(name='import'):
    pass

@click.group(name="import")
def import_group():
    """Import a resource to a deployment"""
    pass

cli.add_command(import_group)


@click.group(name="create")
def create_group():
    """Create a resource"""
    pass

cli.add_command(create_group)


@click.group(name="event-type")
def create_event_type_group():
    """Create a Event Type"""
    pass

create_group.add_command(create_event_type_group)

## The import flow command
 
@import_group.command(name='flow')
@click.option('--origin', prompt='origin', default='http://localhost:9000', help='protocol://hostname:port')
@click.option('--username', prompt='username', help='Username')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.argument('filename')

def import_flow(origin, username, password, filename):
    """Import a flow"""
    client = LhClient(origin)
    client.login(username, password)
    run_on_directory_or_file(filename, client.import_flow)

import_group.add_command(import_flow)


@import_group.command(name='flow-interactively')
@click.option('--origin', prompt='origin', default='http://localhost:9000', help='protocol://hostname:port')
@click.option('--username', prompt='username', help='Username')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.argument('filename')

def import_flow_interactively(origin, username, password, filename):
    """Import a flow, interactively"""
    client = LhClient(origin)
    client.login(username, password)
    run_on_directory_or_file(filename, client.import_flow_interactively)

import_group.add_command(import_flow_interactively)


## The import module command

@import_group.command(name='module')
@click.option('--origin', prompt='origin', default='http://localhost:9000', help='protocol://hostname:port')
@click.option('--username', prompt='username', help='Username')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.argument('filename')

def import_module(origin, username, password, filename):
    """Import a module"""
    client = LhClient(origin)
    client.login(username, password)
    run_on_directory_or_file(filename, client.import_module)

import_group.add_command(import_module)


## The import script command

@import_group.command(name='script')
@click.option('--origin', prompt='origin', default='http://localhost:9000', help='protocol://hostname:port')
@click.option('--username', prompt='username', help='Username')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.argument('filename')

def import_script(origin, username, password, filename):
    """Import a script"""
    client = LhClient(origin)
    client.login(username, password)
    run_on_directory_or_file(filename, client.import_script)

import_group.add_command(import_script)

## The upload CSV

@create_event_type_group.command(name='from-csv')
@click.option('--origin', prompt='origin', default='http://localhost:9000', help='protocol://hostname:port')
@click.option('--username', prompt='username', help='Username')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=False)
@click.option('--name', default='', help="Name to use for the FileConnection and the EventType")
@click.argument('filename')

def create_event_type_from_csv(origin, username, password, name, filename):
    """Create an Event Type from a CSV file"""
    client = LhClient(origin)
    client.login(username, password)
    run_on_directory_or_file(filename, partial(client.create_event_type_from_csv, name))

create_event_type_group.add_command(create_event_type_from_csv)
 
class LhClient():

    def __init__(self, hostname):
        self.hostname = hostname

    def _handle_error(self, response):
        try:
            json_error = response.json()
            if 'errors' in json_error:
                errors = json_error['errors']
                if 'message' in errors[0]:
                    raise LHError(errors[0]['message'], errors)
                elif 'description' in errors[0]:
                    raise LHError(errors[0]['description'], errors)
                else:
                    raise LHError('Error', errors)
            else:
                raise Exception('Unknown error')
        except:
            raise Exception(response.text)

    def _handle_response(self, response):
        if (response.status_code == 200):
            click.echo('Success')
        else:
            self._handle_error(response)

    def _raise_or_pass(self, response):
        if (response.status_code == 200):
            pass
        else:
            self._handle_error(response)

    def login(self, username, password):
        url = self.hostname + '/login'
        data = { 'email': username, 'password': password }
        headers = { 'Content-type': 'application/json' }
        r = requests.post(url, json=data, headers=headers)
        if (r.status_code == 200):
            self.cookie = r.headers['Set-Cookie']
            return 
        else:
            self._handle_error(r)
            
    def import_flow(self, filename):
        with open(filename) as f:
            data = f.read().encode('utf-8')
            url = self.hostname + '/flow/import'
            headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
            response = requests.post(url, data=data, headers=headers)
            self._handle_response(response)


    def _update_flow_session(self, sessionId, resourceId, resolution):
        url = self.hostname + '/flow/import/' + sessionId + '/resource/' + resourceId + '/update'
        headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
        response = requests.post(url, json=resolution, headers=headers)
        self._raise_or_pass(response)

    def _close_flow_session(self, sessionId, resourceId):
        url = self.hostname + '/flow/import/' + sessionId + '/complete'
        headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
        response = requests.post(url, json={}, headers=headers)
        self._raise_or_pass(response)

    def import_flow_interactively(self, filename):
        raise Exception('Not supported')
        with open(filename) as f:
            data = f.read()
            url = self.hostname + '/flow/import/create-session'
            headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
            response = requests.post(url, data=data, headers=headers)
            self._raise_or_pass(response)
            session = response.json()['result']
            sessionId = session['sessionId']
            # first let's check if there are errors about that flow
            flow = session['flowState']['flow']
            resource = flow['resource']
            resourceId = resource['id']
            for error in flow['errors']:
                click.echo('Error: {}'.format(error['message']))
                click.echo('Allowed resolutions: {}'.format(error['allowedResolutions']))
                resolution = click.prompt('Please enter your choice')
                self._update_flow_session(sessionId, resourceId, { 'type': resolution })
            # finally we close the session
            self._close_flow_session(sessionId, resourceId)
            click.echo('Success')

    def import_module(self, filename):
        with open(filename) as f:
            data = f.read().encode('utf-8')
            url = self.hostname + '/module'
            headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
            response = requests.put(url, data=data, headers=headers)
            self._handle_response(response)
                        
    def import_script(self, filename):
        with open(filename, 'rb') as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            content = 'data:logichub/content;base64,{}'.format(encoded) # The backend disregards the mime type
            url = self.hostname + '/demo/hub'
            basename = os.path.basename(filename)
            headers = { 'Cookie': self.cookie, 'Content-type': 'application/json' }
            request = {
                'method': 'addScript',
                'parameters': {
                    'name': basename,
                    'content': content
                }
            }
            response = requests.post(url, json=request, headers=headers)
            self._handle_response(response)
                       
    def create_event_type_from_csv(self, name, filename):
        with open(filename, 'rb') as f:
            basename = os.path.basename(filename)
            (fname, ext) = os.path.splitext(basename)
            if (name == ''):
                name = fname
            # let's make sure that the name has a chance of being valid
            if (ext != '.csv'):
                raise InvalidEventTypeName('file {} doesn\'t have the proper .csv extension'.format(filename), [])
            if (re.search('[^A-Za-z0-9_]', name) is not None):
                raise InvalidEventTypeName('name {} has characters that aren\'t either alphanumerical or _'.format(name), [])
        
            data = f.read().encode('utf-8')
            params = { 'name': name, 'filename': basename }
            url = self.hostname + '/importer/csvfile'
            headers = { 'Cookie': self.cookie }
            response = requests.post(url, data=data, headers=headers, params=params)
            self._handle_response(response)
   
if __name__ == '__main__':
    cli()
