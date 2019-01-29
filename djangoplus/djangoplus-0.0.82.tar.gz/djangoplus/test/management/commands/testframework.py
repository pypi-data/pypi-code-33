# -*- coding: utf-8 -*-

import os
from django.core.management import BaseCommand
from fabric.api import *


class Command(BaseCommand):

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument('--project', action='store_true', dest='project', default=False,
                            help='Test project creation')
        parser.add_argument('--admin', action='store_true', dest='admin', default=False,
                            help='Test admin application')
        parser.add_argument('--installation', action='store_true', dest='installation', default=False,
                            help='Test framework installation in debian/ubuntu')
        parser.add_argument('--implementation', action='store_true', dest='implementation', default=False,
                            help='Test framework implementation with several projects')

    def handle(self, *args, **options):
        execute_tasks = []
        if options.get('project'):
            execute_tasks.append(_test_startpoject)
        elif options.get('admin'):
            execute_tasks.append(_test_admin)
        elif options.get('installation'):
            execute_tasks.append(_test_so_installation)
        elif options.get('implementation'):
            execute_tasks.append(_test_projects)
        if not execute_tasks:
            execute_tasks = [_test_startpoject, _test_admin, _test_so_installation, _test_projects]
        for execute_task in execute_tasks:
            execute(execute_task)


EMPTY_TEST_FILE_CONTENT = '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangoplus._test_admin.models import User
from djangoplus.test import TestCase
from django.conf import settings


class AppTestCase(TestCase):

    def test_app(self):

        User.objects.create_superuser('_test_admin', None, settings.DEFAULT_PASSWORD)

        self.login('_test_admin', settings.DEFAULT_PASSWORD)
'''


DOCKER_FILE_CONTENT = '''FROM {}
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y install python3 python3-pip build-essential python3-dev libfreetype6-dev python3-cffi libtiff5-dev liblcms2-dev libwebp-dev tk8.6-dev libjpeg-dev ssh openssh-server dnsutils curl vim git
RUN apt-get -y install chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev wget
RUN apt-get -y install libgtk-3-dev

RUN curl https://ftp.mozilla.org/pub/firefox/releases/60.0b3/linux-x86_64/en-US/firefox-60.0b3.tar.bz2 --output firefox.tar.bz2
RUN tar xvjf firefox.tar.bz2 --directory /usr/lib/
RUN ln -s /usr/lib/firefox/firefox /usr/local/bin/firefox
RUN rm firefox.tar.bz2

RUN curl http://djangoplus.net/geckodriver-v0.21.0-linux64.tar.gz --output geckodriver.tar.gz
RUN gunzip geckodriver.tar.gz
RUN tar -xvf geckodriver.tar
RUN mv geckodriver /usr/local/bin/
RUN rm geckodriver.tar

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN export LANG=C.UTF-8

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -sfn /usr/bin/python3 /usr/bin/python

RUN pip install --upgrade pip
'''

PROJECTS = [
    ('companies', 'git@djangoplus.net:companies.git'),
    ('blackpoint', 'git@bitbucket.org:brenokcc/blackpoint.git'),
    ('emprestimos', 'git@djangoplus.net:emprestimos.git'),
    ('financeiro', 'git@bitbucket.org:brenokcc/financeiro.git'),
    ('formulacao', 'git@bitbucket.org:brenokcc/formulacao.git'),
    ('gouveia', 'git@bitbucket.org:brenokcc/gouveia.git'),
    ('petshop', 'git@bitbucket.org/brenokcc/petshop.git'),
    ('loja', 'git@bitbucket.org/brenokcc/loja.git'),
    ('biblioteca', 'git@bitbucket.org/brenokcc/biblioteca.git'),
    ('gerifes', 'git@bitbucket.org/brenokcc/gerifes.git'),
    ('simop', 'git@bitbucket.org/brenokcc/simop.git'),
    ('fabrica', 'git@bitbucket.org:brenokcc/fabrica.git'),
    ('abstract', 'git@bitbucket.org:brenokcc/abstract.git'),
]


def _test_startpoject():
    django_settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    os.environ['DJANGO_SETTINGS_MODULE'] = 'xxx.settings'
    if os.path.exists('/tmp/xxx'):
        local('rm -r /tmp/xxx')
    with lcd('/tmp/'):
        local('startproject xxx')
        with lcd('/tmp/xxx'):
            local('python manage.py test')
        with lcd('/tmp'):
            local('rm -r /tmp/xxx')
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module


def _test_admin():
    local('python manage.py test djangoplus.admin.tests.AdminTestCase')


def _test_projects():
    paths = []
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    for project_name, project_url in PROJECTS:
        if os.path.exists('/Users/breno'):
            base_path = '/Users/breno/Documents/Workspace'
            if project_name in ('petshop', 'loja', 'biblioteca'):
                base_path = os.path.join(base_path, 'djangoplus/djangoplus-demos')
            project_path = os.path.join(base_path, project_name)
        else:
            project_path = os.path.join('/tmp', project_name)
            if not os.path.exists(project_path):
                local('git clone {} {}'.format(project_url, project_path))
            with lcd(project_path):
                local('git pull origin master')
        paths.append(project_path)

    django_settings_module = os.environ['DJANGO_SETTINGS_MODULE']
    for project_path in paths:
        project_name = project_path.split('/')[-1]
        print('Testing {}'.format(project_name))
        with lcd(project_path):
            os.environ['DJANGO_SETTINGS_MODULE'] = '{}.settings'.format(project_name)
            local('python manage.py test')
    os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module


def _test_testcases_generation():
    test_file_path = '{}/emprestimos/emprestimos/tests.py'.format('/Users/breno/Documents/Workspace')
    test_file_content = open(test_file_path).read()
    open(test_file_path, 'w').write(EMPTY_TEST_FILE_CONTENT)
    with lcd('{}/emprestimos'.format('/Users/breno/Documents/Workspace')):
        local('python manage.py test --add')
    print(open(test_file_path).read())
    open(test_file_path, 'w').write(test_file_content)


def _test_so_installation():
    for so in ('debian', ):  # ubuntu
        docker_file = open('/tmp/Dockerfile', 'w')
        docker_file.write(DOCKER_FILE_CONTENT.format(so))
        docker_file.close()
        local('docker build -t djangoplus-{} /tmp'.format(so))
        django_settings_module = os.environ['DJANGO_SETTINGS_MODULE']
        os.environ['DJANGO_SETTINGS_MODULE'] = 'xyz.settings'
        local('docker run djangoplus-{} pip install djangoplus && startproject xyz && cd xyz && python manage.py test djangoplus.admin.tests.AdminTestCase'.format(so))
        os.environ['DJANGO_SETTINGS_MODULE'] = django_settings_module


def _test_deploy():
    pass
