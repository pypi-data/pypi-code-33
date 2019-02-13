#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import colorama
import termcolor
import requests
import json
import re
import subprocess
import os

__author__ = "Khomp"
__license__ = "MIT"
__version__ = '0.2.4'


class CIHelper(object):
    """ Run Gitlab routine to update remine
    """

    def __init__(self, redmine):
        """ Command arguments
        """
        self._redmine = redmine
        self._git_helper = Git()

    def run(self, token, dry_run):
        self._git_helper = Git()

        title = self._git_helper.get_commit_title()
        if not title:
            raise Exception("Could not retrieve commit title")

        issue = self._git_helper.get_issue_number(title)
        if not issue:
            raise Exception(
                "Could not find issue number on title: {}".format(title))

        address = self._get_redmine_address(issue, token)
        if not address:
            raise Exception(
                "Could not find issue number on Redmine: {}".format(issue))

        assigned = self._is_issue_assigned(issue, token)
        if not assigned:
            assigned = self._update_issue_user(issue, token, dry_run)
            if not assigned:
                raise Exception(
                    "Could not find user to be assigned to issue {}".format(
                        issue))

        status = self._get_current_issue_status(issue, token)
        new_status = self._update_redmine_issue(status, issue, token, dry_run)

        print(termcolor.colored("COMMIT TITLE: {}".format(title), 'blue'))
        print(termcolor.colored("ISSUE NUMBER: {}".format(issue), 'blue'))
        print(termcolor.colored("REDMINE URL: {}".format(address), 'blue'))
        print(termcolor.colored("ASSIGNED TO: {}".format(assigned), 'blue'))
        print(
            termcolor.colored("CURRENT ISSUE STATUS: {}".format(status),
                              'blue'))
        if new_status != status:
            print(
                termcolor.colored("NEW ISSUE STATUS: {}".format(new_status),
                                  'blue'))

    def _get_redmine_address(self, issue, token):
        try:
            self._redmine.get_issue_info(issue, token)
            return "{}/issues/{}.json".format(self._redmine.server, issue)
        except Exception:
            return False

    def _is_issue_assigned(self, issue, token):
        info = self._redmine.get_issue_info(issue, token)
        issue = info.get('issue')
        assigned_to = issue.get('assigned_to')
        if not assigned_to:
            return None
        return assigned_to.get('name')

    def _get_current_issue_status(self, issue, token):
        info = self._redmine.get_issue_info(issue, token)
        issue = info.get('issue')
        status = issue.get('status')
        return status.get('name')

    def _update_redmine_issue(self, current_status, issue, token, dry_run):
        stable = self._git_helper.is_stable_branch()
        new_status = current_status

        if current_status.lower() == 'not started' and not stable:
            new_status = 'Working'
        elif current_status.lower() in ['not started', 'working'] and stable:
            new_status = 'Implemented'

        if new_status != current_status:
            self._redmine.update_issue_status(issue, new_status, token,
                                              dry_run)

        return new_status

    def _update_issue_user(self, issue, token, dry_run):
        username = self._git_helper.get_username()
        if username:
            self._redmine.update_issue_user(issue, username, token, dry_run)
        return username


class Git(object):
    """ Git command helper
    """

    def get_commit_title(self):
        """ Filter commit title
        """
        title = os.getenv("CI_COMMIT_TITLE")
        if not title:
            output = subprocess.check_output(
                "git log --pretty=format:%s HEAD~1..HEAD .", shell=True)
            title = output.decode()
        return title

    def get_issue_number(self, title):
        """ Extract issue number from commit title
        """
        regex = r'(.*#)(\d+)(.*)'
        proc = re.compile(regex)
        match = proc.match(title)
        if not match:
            return None
        return match.group(2)

    def is_stable_branch(self):
        """ Check if current branch is stable: master or release
        """
        if os.getenv('CI_COMMIT_TAG'):
            return True

        branch = os.getenv('CI_COMMIT_REF_SLUG')
        if not branch:
            branch = subprocess.check_output(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode()
        regex = r'(master|release.*)'
        proc = re.compile(regex)
        return proc.match(branch)

    def get_username(self):
        """ Retrieve user name from gitlab or commit
        """
        username = os.getenv("GITLAB_USER_LOGIN")
        if not username:
            result = subprocess.check_output(
                ["git", "log", r"--format=%ae", r"HEAD^!"]).decode()
            regex = r'(.*)@.*'
            proc = re.compile(regex)
            match = proc.match(result)
            if match:
                username = match.group(1)
        return username


class Redmine(object):
    """ Redmine helper
    """

    def __init__(self, server):
        """ Fill redmine server address
        """
        self.server = server

    def update_issue_status(self, issue, status, token, dry_run):
        """ Change current issue status to new one.
        """
        address = "{}/issues/{}.json".format(self.server, issue)
        data = json.dumps({"issue": {"status_id": self.to_status_id(status)}})
        headers = {
            'X-Redmine-API-Key': token,
            'Content-Type': 'application/json'
        }

        if dry_run:
            return

        response = requests.put(address, headers=headers, data=data)
        response.raise_for_status()

    def update_issue_user(self, issue, user, token, dry_run):
        """ Assigne the issue to a new user
        """
        users = self.get_user_list()
        if user not in users:
            raise Exception(
                "User {} could not be found on user list".format(user))

        address = "{}/issues/{}.json".format(self.server, issue)
        data = json.dumps({"issue": {"assigned_to_id": users[user]}})
        headers = {
            'X-Redmine-API-Key': str(token),
            'Content-Type': 'application/json'
        }

        if dry_run:
            return

        response = requests.put(address, headers=headers, data=data)
        response.raise_for_status()

    def to_status_id(self, status_name):
        """ Retrieve issue status id by it name
        """
        address = "{}/issue_statuses.json".format(self.server)
        response = requests.get(address)
        response.raise_for_status()
        json_data = response.json()
        json_data = json_data["issue_statuses"]
        for status in json_data:
            if str(status["name"]).lower() == status_name.lower():
                return status["id"]
        raise Exception("Invalid status name: {}".format(status_name))

    def get_issue_info(self, issue, token):
        """ Retrieve issue information
        """
        address = "{}/issues/{}.json".format(self.server, issue)
        headers = {
            'X-Redmine-API-Key': token,
            'Content-Type': 'application/json'
        }
        response = requests.get(address, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user_list(self):
        """ Retrieve user list from redmine
        """
        users = {}
        regex = r'(.*)@.*'
        proc = re.compile(regex)
        for i in range(1, 400):
            address = "{}/users/{}.json".format(self.server, i)
            response = requests.get(address)
            # id not used
            if response.status_code == 404:
                continue
            json_response = response.json()
            user = json_response['user']
            if not user.get('mail'):
                continue
            match = proc.match(user.get('mail'))
            if match:
                users[match.group(1)] = json_response['user']['id']
        return users

    def show_issue_info(self):
        """ Show issue info using JSON format
        """
        print(self.get_issue_info())

    def show_remine_users(self):
        """ Show registered users on Redmine
        """
        print(self.get_user_list())

    def get_supported_status(self):
        """ Get available issue status names
        """
        address = "{}/issue_statuses.json".format(self.server)
        response = requests.get(address)
        response.raise_for_status()
        json_data = response.json()
        return json_data['issue_statuses']

    def show_supported_status(self):
        """ Display issue status names using JSON format
        """
        status_list = self.get_supported_status()
        print([status['name'] for status in status_list])


class Command(object):
    """ Execute Redmine issue update
    """

    def _parse_arguments(self, *args):
        """ Add program arguments

        :param args: User arguments
        """

        parser = argparse.ArgumentParser(description="Update issue on Redmine")
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--issue', '-i', type=int, help='Issue ID on Redmine')
        parser.add_argument(
            '--status', '-s', type=str, help='New issue status')
        parser.add_argument(
            '--user', '-u', type=str, help='User to be assigned')
        parser.add_argument(
            '--server',
            '-r',
            default='https://redmine.in.khomp.com',
            help='Redmine server address')
        parser.add_argument('--token', '-t', help='Redmine auth Token')
        parser.add_argument(
            '--dry-run',
            '-d',
            action='store_true',
            help='Do not push any change')
        parser.add_argument(
            '--version',
            '-v',
            action='version',
            version='%(prog)s {}'.format(__version__),
            help="Show application version")
        group.add_argument(
            '--status-list',
            '-l',
            action='store_true',
            help='List supported status')
        group.add_argument(
            '--user-list',
            '-ul',
            action='store_true',
            help='List Redmine users')

        group.add_argument(
            '--ci-run',
            '-cr',
            action='store_true',
            help='Run validation on CI')
        args = parser.parse_args(*args)
        return args

    def run(self, *args):
        """ Process file update

        :param args: User arguments
        """
        arguments = self._parse_arguments(*args)

        redmine = Redmine(arguments.server)

        if arguments.status_list:
            redmine.show_supported_status()
        elif arguments.user_list:
            redmine.show_remine_users()
        elif arguments.issue:
            if not arguments.token and \
               not arguments.user and \
               not arguments.status:
                redmine.show_issue_info(arguments.issue)
                return

            if not arguments.token and not arguments.dry_run:
                raise Exception("Authentication token must be defined.")
            if arguments.user:
                redmine.update_issue_user(arguments.issue, arguments.user,
                                          arguments.token, arguments.dry_run)
            if arguments.status:
                redmine.update_issue_status(arguments.issue, arguments.user,
                                            arguments.token, arguments.dry_run)
        elif arguments.ci_run:
            if not arguments.token and not arguments.dry_run:
                raise Exception("Authentication token must be defined.")
            ci_helper = CIHelper(redmine)
            ci_helper.run(arguments.token, arguments.dry_run)
        else:
            raise Exception("Command is empty. Run -h to get help.")


def main(args):
    """ Execute command update

    :param args: User arguments
    """
    try:
        colorama.init()
        command = Command()
        command.run(args)
    except Exception as error:
        print(termcolor.colored("ERROR: {}".format(error), 'red'))
        sys.exit(1)
