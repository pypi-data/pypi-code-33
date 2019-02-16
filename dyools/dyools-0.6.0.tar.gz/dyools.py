#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import inspect
import os
import re
import sys
from contextlib import contextmanager
from pprint import pprint

import click

try:
    basestring
except NameError:
    basestring = str

__VERSION__ = '0.6.0'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''


def signature(callable):
    if getattr(inspect, 'signature'):
        pprint(inspect.signature(callable))
    if getattr(inspect, 'getargspec'):
        pprint(inspect.getargspec(callable))
    if getattr(inspect, 'getfullargspec'):
        pprint(inspect.getfullargspec(callable))


def contruct_domain_from_str(domain):
    AND, OR = ' and ', ' or '
    assert '(' not in domain, "can not process parenthese in string domain"
    if AND in domain:
        assert OR not in domain, "domain should not have or and and operators"
    if OR in domain:
        assert AND not in domain, "domain should not have or and and operators"
    and_or = '|' if OR in domain else '&'
    tuples = []
    tuples1 = domain.split(AND)
    [tuples.extend(t.split(OR)) for t in tuples1 if t]
    domain = [tuple(t.split()) for t in tuples if t]
    if not domain:
        res = []
    else:
        for ttuple in domain:
            assert len(ttuple) == 3, 'a condition should have 3 parts [%s]' % ttuple
        i = 0
        for key, op, value in domain:
            float_parts = value.split('.')
            isfloat = len(float_parts) == 2
            if value == 'False':
                value = False
            elif value == 'True':
                value = True
            elif value.isdigit():
                value = int(value)
            elif isfloat and float_parts[0].isdigit() and float_parts[1].isdigit():
                value = float(value)
            domain[i] = (key, op, value)
            i += 1
        if len(domain) > 1:
            domain = [and_or] * (len(domain) - 1) + domain
        res = domain
    return res


class ENV(object):
    def __init__(self, env=False, odoo=False, dbname=False, verbose=True):
        assert (env and odoo) or (
                odoo and dbname), "give an existing environnement or specify odoo and dbname for creating a new one"
        if env:
            self.env = env
        else:
            registry = odoo.modules.registry.Registry.new(dbname)
            cr = registry.cursor()
            self.env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        self.odoo = odoo
        self.dbname = self.env.cr.dbname
        self.cr = self.env.cr
        self.conf = odoo.tools.config
        self.verbose = verbose

    def get_env(self):
        return self.env

    def get_self(self):
        return self.env

    def close(self):
        if not self.cr.closed:
            self.cr.close()

    def show_env(self):
        print(self.env, self.odoo, self.dbname, self.cr)

    def get_addons_list(self, enterprise=False, core=False, extra=True):
        installed, uninstalled = [], []
        for path in self.conf['addons_path'].split(','):
            dirs = [ddir for ddir in os.listdir(path) if os.path.isdir(os.path.join(path, ddir))]
            addons = [ddir for ddir in dirs if
                      len({'__manifest__.py', '__init__.py'} & set(os.listdir(os.path.join(path, ddir)))) == 2]
            modules = self.env['ir.module.module'].search([('name', 'in', addons)])
            addons = modules.mapped('name')
            if not addons:
                continue
            if not core and {'base', 'sale', 'account'} & set(addons):
                continue
            if not enterprise and {'account_reports'} & set(addons):
                continue
            if not extra and not ({'base', 'sale', 'account_reports'} & set(addons)):
                continue
            installed.extend(modules.filtered(lambda a: a.state == 'installed').mapped('name'))
            uninstalled.extend(modules.filtered(lambda a: a.state == 'uninstalled').mapped('name'))
        return installed, uninstalled

    def check_uninstalled_modules(self, enterprise=False, core=False, extra=True):
        installed, uninstalled = self.get_addons_list(enterprise=enterprise, core=core, extra=extra)
        pprint('Installed modules   : %s' % installed)
        pprint('Uninstalled modules : %s' % uninstalled)
        if uninstalled:
            sys.exit(-1)
        else:
            sys.exit(0)

    def show(self, records, fields=[], types=[]):
        assert isinstance(fields, list), 'fields should be a list'
        print('Show %s record(s)' % len(records))
        if not fields:
            fields = records.fields_get().keys()
        if types:
            fields = filter(lambda f: '.' not in f and records.fields_get()[f]['type'] in types, fields)
            fields = [f for f in fields]
        if not fields:
            print('Not field is given')
            return False
        for record in records:
            print('%s Record [ID=%s][Name=%s]' % ('#' * 40, record.id, getattr(record, 'display_name', '')))
            for field in fields:
                print("{:_<40}<{}>".format(field, record.mapped(field) if '.' in field else record[field]))

    def get(self, model, domain, limit=False, order=False):
        records = model
        if isinstance(domain, tuple):
            domain = [domain]
        if isinstance(domain, basestring):
            domain = contruct_domain_from_str(domain)
        if isinstance(records, self.odoo.models.Model):
            domain = ['&', ('id', 'in', records.ids)] + domain
            model = records._name
        return self.env[model].search(domain)


class Operator(object):
    @classmethod
    def flat(cls, *lists):
        result = []

        def put_in(item):
            if IF.is_iterable(item):
                for x in item:
                    put_in(x)
            else:
                result.append(item)

        for item in lists:
            put_in(item)
        return result

    @classmethod
    def unique(cls, sequence):
        result = []
        if IF.is_iterable(sequence):
            for item in sequence:
                found = False
                for res in result:
                    if res is item:
                        found = True
                        break
                if not found:
                    result.append(item)
        else:
            return sequence
        return result

    @classmethod
    def split_and_flat(cls, sep=',', *lists):
        result = cls.flat(lists)
        for i, item in enumerate(result):
            if IF.is_str(item):
                result[i] = item.split(sep)
        return cls.flat(result)

        def put_in(item):
            if IF.is_iterable(item):
                for x in item:
                    put_in(x)
            else:
                result.append(item)

        for item in lists:
            put_in(item)
        return result


class IF(object):
    @classmethod
    def is_xmlid(cls, text):
        if not cls.is_str(text) or cls.is_empty(text):
            return False
        else:
            text = text.strip()
            if re.match("^[a-z0-9_]+\.[a-z0-9_]+$", text):
                return True
            else:
                return False

    @classmethod
    def is_str(cls, text):
        if isinstance(text, basestring):
            return True
        else:
            return False

    @classmethod
    def is_empty(cls, text):
        if cls.is_str(text):
            text = text.strip()
        if text:
            return False
        else:
            return True

    @classmethod
    def is_iterable(cls, text):
        if cls.is_str(text):
            return False
        if hasattr(text, '__iter__'):
            return True
        else:
            return False


class Eval(object):
    def __init__(self, data, context):
        self.data = data
        self.context = context or {}

    def eval(self, eval_result=True):
        def parse(value, ctx):
            if isinstance(value, list):
                return [parse(item, ctx) for item in value]
            elif isinstance(value, dict):
                _d = {}
                for _k, _v in value.items():
                    _d[_k] = parse(_v, ctx)
                return _d
            elif isinstance(value, basestring):
                origin = value
                res = value.format(**ctx)
                if origin != res and eval_result:
                    try:
                        res = eval(res, ctx)
                    except Exception as e:
                        pass
                return res
            else:
                return value

        return parse(self.data, self.context)


class SFTP(object):
    def __init__(self, sftp):
        self.sftp = sftp

    @contextmanager
    def chdir(self, path):
        try:
            origin = self.sftp.getcwd()
            self.sftp.chdir(path)
            yield
        except Exception as e:
            raise e
        finally:
            self.sftp.chdir(origin)


class Path(object):
    @classmethod
    @contextmanager
    def chdir(cls, path):
        try:
            origin = os.getcwd()
            os.chdir(path)
            yield
        except Exception as e:
            raise e
        finally:
            os.chdir(origin)

    @classmethod
    def subpaths(self, path, isfile=False):
        elements = []
        sep = os.path.sep if path.startswith(os.path.sep) else ''
        res = [x for x in path.split(os.path.sep) if x]
        res.reverse()
        while res:
            item = res.pop()
            if elements:
                elements.append(os.path.join(sep, elements[-1], item))
            else:
                elements = [os.path.join(sep, item)]
        return elements if not isfile else elements[:-1]


class Logger(object):
    def _clean_msg(self, msg):
        if not isinstance(msg, basestring):
            try:
                msg = unicode(msg)
            except:
                try:
                    msg = str(msg)
                except:
                    pass
        return msg

    def info(self, msg, exit=False):
        click.echo(self._clean_msg(msg))
        if exit:
            sys.exit(-1)

    def warn(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='yellow')
        if exit:
            sys.exit(-1)

    def debug(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='blue')
        if exit:
            sys.exit(-1)

    def success(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='green')
        if exit:
            sys.exit(-1)

    def code(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='cyan')
        if exit:
            sys.exit(-1)

    def error(self, msg, exit=True):
        click.secho(self._clean_msg(msg), fg='red')
        if exit:
            sys.exit(-1)

    def title(self, msg, exit=False):
        click.secho(self._clean_msg(msg), fg='white', bold=True)
        if exit:
            sys.exit(-1)


class File(object):
    @classmethod
    def get_size_str(cls, path, unit='mb'):
        size, u = cls._get_size(path, unit=unit)
        return "%s %s" % (size, u)

    @classmethod
    def get_size(cls, path, unit='mb'):
        size, u = cls._get_size(path, unit=unit)
        return size

    @classmethod
    def _get_size(cls, path, unit='mb'):
        size = os.path.getsize(path)
        if unit == 'mb':
            return round(size / (1024. * 1024.), 2), 'MB'
        else:
            return round(size, 2), 'B'
