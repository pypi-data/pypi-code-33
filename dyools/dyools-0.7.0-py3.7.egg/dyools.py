#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

import calendar
import inspect
import os
import re
import shutil
import sys
from contextlib import contextmanager
from datetime import datetime, date
from pprint import pprint

import click
from dateutil.parser import parse as dtparse
from dateutil.relativedelta import relativedelta

try:
    basestring
except NameError:
    basestring = str

try:
    from odoo.tools import human_size
except:
    human_size = lambda r: r

__VERSION__ = '0.7.0'
__AUTHOR__ = ''
__WEBSITE__ = ''
__DATE__ = ''

DATE_FORMAT, DATETIME_FORMAT = "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"
DATE_FR_FORMAT, DATETIME_FR_FORMAT = "%d/%m/%Y", "%d/%m/%Y %H:%M:%S"
DATE_TYPE, DATETIME_TYPE = "date", "datetime"


def signature(callable):
    if getattr(inspect, 'signature'):
        pprint(inspect.signature(callable))
    if getattr(inspect, 'getargspec'):
        pprint(inspect.getargspec(callable))
    if getattr(inspect, 'getfullargspec'):
        pprint(inspect.getfullargspec(callable))


def date_range(dt_start, dt_stop=False, **kwargs):
    dt = Date(dt_start)
    stop = dt_stop
    if stop:
        dt_stop = Date(dt_stop)
    if not kwargs:
        kwargs = {'days': 1}
    while True:
        yield dt.to_str()
        dt = dt.apply(**kwargs)
        if stop and dt_stop.to_str() < dt.to_str():
            break


class Date(object):
    def __init__(self, *args, **kwargs):
        assert args or kwargs, "arguments should be a date or parameters for datetime"
        ttype = dt = False
        if len(args) == 1:
            item = args[0]
            if isinstance(item, basestring):
                if len(item) == 10:
                    dt = datetime.strptime(item, DATE_FORMAT)
                    ttype = DATE_TYPE
                elif len(item) == 19:
                    dt = datetime.strptime(item, DATETIME_FORMAT)
                    ttype = DATETIME_TYPE
                else:
                    dt = dtparse(item)
                    if ':' in item:
                        ttype = DATETIME_TYPE
                    else:
                        ttype = DATE_TYPE
            elif isinstance(item, datetime):
                dt = item
                ttype = DATETIME_TYPE
            elif isinstance(item, date):
                dt = datetime(item.year, item.month, item.day)
                ttype = DATE_TYPE
            elif isinstance(item, Date):
                dt = item.dt
                ttype = item.ttype
        else:
            dt = datetime(*args, **kwargs)
            if len(args) + len(kwargs) == 3:
                ttype = DATE_TYPE
            else:
                ttype = DATETIME_FORMAT
        assert ttype and dt, "The format of date [%s] is not valid" % item
        self.dt = dt
        self.ttype = ttype

    def relativedelta(self, **kwargs):
        self.apply(**kwargs)
        if self.ttype == DATE_TYPE:
            return self.dt.strftime(DATE_FORMAT)
        else:
            return self.dt.strftime(DATETIME_FORMAT)

    def apply(self, **kwargs):
        sub = kwargs.get('sub', False) == True
        if 'sub' in kwargs: del kwargs['sub']
        if sub:
            self.dt = self.dt - relativedelta(**kwargs)
        else:
            self.dt = self.dt + relativedelta(**kwargs)
        return self

    def first_day(self):
        dt = self.dt + relativedelta(day=1)
        if self.ttype == DATE_TYPE:
            return dt.strftime(DATE_FORMAT)
        else:
            return dt.strftime(DATETIME_FORMAT)

    def last_day(self):
        dt = self.dt + relativedelta(day=calendar.monthrange(self.dt.year, self.dt.month)[1])
        if self.ttype == DATE_TYPE:
            return dt.strftime(DATE_FORMAT)
        else:
            return dt.strftime(DATETIME_FORMAT)

    def to_datetime(self):
        return self.dt

    def to_date(self):
        return self.dt.date()

    def to_str(self):
        if self.ttype == DATE_TYPE:
            return self.dt.strftime(DATE_FORMAT)
        else:
            return self.dt.strftime(DATETIME_FORMAT)

    def to_fr(self):
        if self.ttype == DATE_TYPE:
            return self.dt.strftime(DATE_FR_FORMAT)
        else:
            return self.dt.strftime(DATETIME_FR_FORMAT)

    def is_between(self, dt_start, dt_stop):
        dt_start = Date(dt_start) if dt_start else False
        dt_stop = Date(dt_stop) if dt_stop else False
        dt = self
        if dt_start and dt_stop:
            if dt_stop < dt_start:
                dt_start, dt_stop = dt_stop, dt_start
            return dt >= dt_start and dt <= dt_stop
        elif dt_start:
            return dt >= dt_start
        elif dt_stop:
            return dt <= dt_stop
        else:
            return True

    def _apply_add_sub(self, other, sub=False):
        kwargs = {}
        mapping = {
            'y': 'years',
            'm': 'months',
            'd': 'days',
            'H': 'hours',
            'M': 'minutes',
            'S': 'seconds',
        }
        assert isinstance(other, (basestring, int)), "format of [%s] is invalid" % other
        if isinstance(other, basestring):
            coef = 1
            if other and other[0] in ['+', '-']:
                coef, other = other[0], other[1:]
                coef = -1 if coef == '-' else 1
            assert len(other) > 1 and other[-1] in mapping.keys(), "format of [%s] is invalid" % other
            assert other[:-1].isdigit(), "format of [%s] is invalid" % other
            kwargs[mapping[other[-1]]] = coef * int(other[:-1])
        elif isinstance(other, int):
            kwargs['days'] = other
        if sub: kwargs['sub'] = True
        return self.relativedelta(**kwargs)

    def __sub__(self, other):
        return self._apply_add_sub(other, sub=True)

    def __add__(self, other):
        return self._apply_add_sub(other)

    def __str__(self):
        if self.ttype == DATE_TYPE:
            return self.dt.strftime(DATE_FORMAT)
        else:
            return self.dt.strftime(DATETIME_FORMAT)

    def __repr__(self):
        if self.ttype == DATE_TYPE:
            return self.dt.strftime(DATE_FORMAT)
        else:
            return self.dt.strftime(DATETIME_FORMAT)

    def __lt__(self, other):
        return self.to_str() < Date(other).to_str()

    def __le__(self, other):
        return self.to_str() <= Date(other).to_str()

    def __eq__(self, other):
        return self.to_str() == Date(other).to_str()

    def __ne__(self, other):
        return self.to_str() != Date(other).to_str()

    def __gt__(self, other):
        return self.to_str() > Date(other).to_str()

    def __ge__(self, other):
        return self.to_str() >= Date(other).to_str()


def create_file(path, content):
    def _erase_data(_path, _content):
        with open(_path, 'w+') as f:
            f.write(_content)

    if not os.path.isfile(path):
        ddir = os.path.dirname(path)
        create_dir(ddir)
        _erase_data(path, content)
    else:
        with open(path, 'r') as f:
            c = f.read()
        if c != content:
            _erase_data(path, content)


def create_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def clean_dir(path):
    if os.path.exists(path):
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            elif os.path.isfile(full_path):
                os.remove(full_path)


def delete_path(path):
    if os.path.exists(path):
        shutil.rmtree(path)


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
            if op == "==": op = '='
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
        self.odoo = odoo
        self.dbname = dbname
        self.verbose = verbose
        self.cr = False
        self.conf = self.odoo.tools.config
        self.list_db = self.odoo.tools.config['list_db']
        self.list_db_disabled = self.odoo.tools.config['list_db'] == False
        self.version = odoo.release.version_info[0]
        if env:
            self.env = env
            self.dbname = self.env.cr.dbname
            self.cr = self.env.cr
        else:
            self.reset()

    def _require_env(self):
        assert self.env, "An environment is required for this method"

    def reset(self):
        if self.cr and not self.cr.closed:
            print('closing the cursor')
            self.cr.close()
        try:
            registry = self.odoo.modules.registry.Registry.new(self.dbname)
            cr = registry.cursor()
            self.env = self.odoo.api.Environment(cr, self.odoo.SUPERUSER_ID, {})
        except Exception as e:
            self.env = False
        if self.env:
            self.dbname = self.env.cr.dbname
            self.cr = self.env.cr
        else:
            self.cr = False

    def close(self):
        self._require_env()
        if not self.cr.closed:
            self.cr.close()

    def get_addons(self, enterprise=False, core=False, extra=True, addons_path=False):
        self._require_env()
        installed, uninstalled = [], []
        addons_path = addons_path or self.conf['addons_path'].split(',')
        for path in addons_path:
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

    def check_uninstalled_modules(self, enterprise=False, core=False, extra=True, addons_path=False):
        self._require_env()
        installed, uninstalled = self.get_addons(enterprise=enterprise, core=core, extra=extra, addons_path=addons_path)
        pprint('Installed modules   : %s' % installed)
        pprint('Uninstalled modules : %s' % uninstalled)
        if uninstalled:
            sys.exit(-1)
        else:
            sys.exit(0)

    def show(self, records, fields=[], types=[]):
        self._require_env()
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
        self._require_env()
        records = model
        if isinstance(domain, tuple):
            domain = [domain]
        if isinstance(domain, basestring):
            domain = contruct_domain_from_str(domain)
        if isinstance(records, self.odoo.models.Model):
            domain = ['&', ('id', 'in', records.ids)] + domain
            model = records._name
        kwargs = {}
        if limit: kwargs['limit'] = limit
        if order: kwargs['order'] = order
        return self.env[model].search(domain, **kwargs)

    def dump_db(self, dest=False, zip=True):
        self._require_env()
        data_dir = os.path.join(self.odoo.tools.config["data_dir"], "backups", self.dbname)
        dest = dest or data_dir
        try:
            os.makedirs(dest)
        except:
            pass
        assert os.path.isdir(dest), "The directory [%s] should exists" % dest
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'zip' if zip else 'dump'
        filename = "{}_{}.{}".format(self.dbname, now, ext)
        path = os.path.join(dest, filename)
        if self.list_db_disabled:
            self.list_db = True
        with open(path, 'wb+') as destination:
            kwargs = {}
            if not zip: kwargs['backup_format'] = 'custom'
            self.odoo.service.db.dump_db(self.dbname, destination, **kwargs)
        if self.list_db_disabled:
            self.list_db = False
        pprint('End: %s' % path)
        size = human_size(os.path.getsize(path))
        pprint('Size: %s' % size)
        return path

    def drop_db(self):
        try:
            self.odoo.service.db.exp_drop(self.dbname)
        except Exception as e:
            pass
        pprint('End: dbname=%s is dropped' % self.dbname)
        return self.dbname

    def restore_db(self, path, drop=False):
        assert os.path.isfile(path), 'The path [%s] sould be a file' % path
        if drop:
            self.drop_db()
        size = human_size(os.path.getsize(path))
        pprint('Size: %s' % size)
        self.odoo.service.db.restore_db(self.dbname, path)
        pprint('End: %s dbname=%s' % (path, self.dbname))
        return path


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
