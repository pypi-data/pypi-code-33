#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import calendar
import os
import random
import sys
from datetime import datetime
from os.path import expanduser

import click
import dateparser as parser
import yaml
from colorclass import Color
from dateutil.relativedelta import relativedelta
from terminaltables import SingleTable

click.disable_unicode_literals_warning = True

__VERSION__ = '0.3.0'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
DAYS = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche",
}
home = expanduser("~")
home = os.path.join(home, '.dyvz')

TODO_FILE = os.path.join(home, 'todo.yml')
SIGN_FILE = os.path.join(home, 'sign.yml')

try:
    os.makedirs(home)
except:
    pass

if not os.path.exists(TODO_FILE):
    with open(TODO_FILE, 'w+') as config_file:
        pass

if not os.path.exists(SIGN_FILE):
    with open(SIGN_FILE, 'w+') as config_file:
        pass


class Tools:
    def set_color(self, txt, obj, level=2):
        if obj and isinstance(obj, Todo):
            level = obj.priority
            if obj.due and datetime.today().date() >= obj.due and not obj.done:
                level = 1
        if not level or level > 2:
            c = 'autoblue'
        elif level == 2:
            return txt
        else:
            c = 'autored'
        return Color('{%s}%s{/%s}' % (c, txt, c))


class Collection(object):
    def __init__(self, yml_file, tools):
        self.current_id = 0
        self.todos = []
        self.tools = tools
        self.yml_file = yml_file
        self.load()

    def load(self):
        with open(self.yml_file) as yd:
            data = yaml.load(yd.read())
        if data:
            self.current_id = data.get('current_id', 1)
            for item in data.get('data', []):
                todo = Todo()
                todo.load(item)
                self.todos.append(todo)

    def dump(self):
        data = {'data': [], 'current_id': self.current_id}
        for todo in self.todos:
            data['data'].append(todo.dump())
        with open(self.yml_file, 'w+') as yd:
            yd.write(yaml.dump(data))

    def add(self, todo):
        self.current_id += 1
        todo.id = self.current_id
        self.todos.append(todo)

    def show(self, todos=None, priority=None, done=None, new=None, due=None):
        if due:
            due = parser.parse(due).date() if parser.parse(due) else None
        tbl_data = [["ID", "CREATE DATE", "PRIORITY", "NAME", "DUE DATE", "DAY", "DONE"]]
        for todo in sorted(todos or self.todos, key=lambda todo: todo.due or datetime(2030, 1, 1).date()):
            if not todos:
                if priority is not None and todo.priority != priority: continue
                if not (done and new):
                    if done and todo.done == False: continue
                    if new and todo.done == True: continue
                if due and todo.due != due: continue
            tbl_data.append([
                self.tools.set_color(todo.id, todo),
                self.tools.set_color(todo.create, todo),
                self.tools.set_color(todo.priority, todo),
                self.tools.set_color(todo.name, todo),
                self.tools.set_color(todo.due or '', todo),
                self.tools.set_color(DAYS[todo.due.weekday()] if todo.due else '', todo),
                self.tools.set_color(todo.done and 'x' or '', todo),
            ])
        table_instance = SingleTable(tbl_data)
        table_instance.inner_heading_row_border = True
        table_instance.inner_column_border = False
        table_instance.outer_border = True
        click.echo(table_instance.table)
        click.echo('Total: %s' % (len(tbl_data) - 1))

    def find(self, param):
        found = []
        for item in param:
            for todo in self.todos:
                if str(item).isdigit():
                    item = int(item)
                if item in [todo.id, todo.name]:
                    found.append(todo)
        return found

    def apply(self, todos, delete=None, done=None, due=None, priority=None, name=None):
        for todo in todos:
            if todo in self.todos:
                if priority is not None:
                    todo.set_priority(priority)
                if done == True:
                    todo.set_done()
                if done == False:
                    todo.set_new()
                if due:
                    todo.set_due(due)
                if name:
                    todo.set_name(name)
                if delete:
                    self.todos.remove(todo)

    def reset(self):
        self.todos = []
        self.current_id = 0


class Todo(object):
    def __init__(self, name=None, priority=2):
        self.name = name
        self.priority = priority
        self.id = None
        self.done = False
        self.due = None
        self.create = datetime.today().date()

    def load(self, data):
        self.name = data.get('name', None)
        self.priority = data.get('priority', 2)
        self.id = data.get('id', 1)
        self.done = data.get('done', False)
        self.due = data.get('due', None)
        self.create = data.get('create', datetime.today().date())

    def set_name(self, name):
        self.name = name

    def set_new(self):
        self.done = False

    def set_done(self):
        self.done = True

    def set_priority(self, priority):
        self.priority = priority

    def set_due(self, due):
        if due:
            self.due = parser.parse(due).date() if parser.parse(due) else None
        else:
            self.due = None

    def dump(self):
        return {
            'name': self.name,
            'priority': self.priority,
            'id': self.id,
            'done': self.done,
            'due': self.due,
            'create': self.create,
        }


@click.command()
@click.argument('tasks', nargs=-1)
@click.option('--select', '-s', type=click.STRING, multiple=True, help="Select todos")
@click.option('--add', '-a', type=click.STRING, multiple=True, help="Add todos")
@click.option('--delete', is_flag=True, default=False, help="delete todos")
@click.option('--delete-all', is_flag=True, default=False, help="delete all todos")
@click.option('--set-done', is_flag=True, default=False, help="Set todos as done")
@click.option('--set-new', is_flag=True, default=False, help="Set todos as new")
@click.option('--set-name', type=click.STRING, help="Rename a todo")
@click.option('--set-due', type=click.STRING, help="Set a due date for todos")
@click.option('--set-priority', type=click.INT, help="Set a priority for todos")
@click.option('--list', '-l', 'r_list', is_flag=True, default=False, help="List todos")
@click.option('--new', is_flag=True, default=None, help="Filter todos by state=new")
@click.option('--done', is_flag=True, default=None, help="Filter todos by state=done")
@click.option('--due', type=click.STRING, help="filter by due date")
@click.option('--priority', type=click.INT, help="filter by the priority")
@click.pass_context
def todocli(
        ctx,
        tasks,
        select,
        add,
        delete,
        delete_all,
        set_done,
        set_new,
        set_name,
        set_due,
        set_priority,
        r_list,
        new,
        done,
        due,
        priority):
    add = list(add) + list(tasks)
    new = new or (not done and not new)
    collection = Collection(TODO_FILE, Tools())
    todos = collection.find(select)
    if delete_all:
        collection.reset()
    for todo_name in add:
        todo = Todo(name=todo_name)
        todos.append(todo)
        collection.add(todo)
    if set_done:
        collection.apply(todos, done=True)
    if set_new:
        collection.apply(todos, done=False)
    if set_due:
        collection.apply(todos, due=set_due)
    if set_name:
        collection.apply(todos, name=set_name)
    if set_priority:
        collection.apply(todos, priority=set_priority)
    if delete:
        collection.apply(todos, delete=True)
        old_todos = todos[:]
        for todo in todos:
            old_todos.remove(todo)
        todos = old_todos
    r_list = r_list or select or add or (priority or done or new or due)
    r_list = r_list or (not select and not add)
    if r_list:
        collection.show(todos=todos, priority=priority, done=done, new=new, due=due)
    collection.dump()


#
# Manage signs
#
class Signs(object):
    def __init__(self, yml_file, tools, test=False):
        self.current_id = 0
        self.signs = []
        self.tools = tools
        self.test = test
        self.yml_file = yml_file
        self.load()

    def load(self):
        if self.test:
            dt = datetime(2017, 12, 15).date()
            self.current_id = 1
            for day in range(self.test):
                dt = dt + relativedelta(days=1)
                for s in [0.25, 0.5, 0.75, 1]:
                    project = random.choice(["Dev", "Design", "Extra"])
                    sign = Sign(s, project, dt)
                    sign.id = self.current_id
                    self.current_id += 1
                    self.signs.append(sign)
            return
        with open(self.yml_file) as yd:
            data = yaml.load(yd.read())
        if data:
            self.current_id = data.get('current_id', 1)
            for item in data.get('data', []):
                sign = Sign()
                sign.load(item)
                self.signs.append(sign)

    def dump(self):
        data = {'data': [], 'current_id': self.current_id}
        for sign in self.signs:
            data['data'].append(sign.dump())
        with open(self.yml_file, 'w+') as yd:
            yd.write(yaml.dump(data))

    def add(self, sign):
        self.current_id += 1
        sign.id = self.current_id
        self.signs.append(sign)

    def show(self, signs, calendar, r_from, r_to):
        tbl_data = []
        for sign in signs or self.signs:
            if not signs:
                if r_from and sign.date < r_from: continue
                if r_to and sign.date > r_to: continue
            tbl_data.append([
                sign.id,
                sign.date,
                sign.project,
                sign.time
            ])
        len_tbl_data = len(tbl_data)
        if calendar:
            self.show_calendar(tbl_data)
        else:
            tbl_data = [["ID", "DATE", "PROJECT", "TIME"]] + tbl_data
            tbl_data.append([
                "TOTAL",
                "",
                "",
                sum(map(lambda x: x[3], tbl_data[1:]))
            ])
            table_instance = SingleTable(tbl_data)
            table_instance.inner_heading_row_border = True
            table_instance.inner_column_border = False
            table_instance.outer_border = True
            click.echo(table_instance.table)
        click.echo('Total: %s' % len_tbl_data)

    def find(self, param, r_from, r_to):
        found = []
        for sign in self.signs:
            if param:
                for item in param:
                    if str(item).isdigit():
                        item = int(item)
                    if item in [sign.id]:
                        found.append(sign)
            else:
                if r_from and r_to:
                    if sign.date >= r_from and sign.date <= r_to:
                        found.append(sign)
                elif r_from and sign.date >= r_from:
                    found.append(sign)
                elif r_to and sign.date <= r_to:
                    found.append(sign)
        return list(set(found))

    def apply(self, signs, delete=None, time=None, date=None, project=None):
        for sign in signs:
            if sign in self.signs:
                if time is not None:
                    sign.set_time(time)
                if date:
                    sign.set_date(date)
                if project:
                    sign.set_project(project)
                if delete:
                    self.signs.remove(sign)

    def reset(self):
        self.signs = []
        self.current_id = 0

    def show_calendar(self, data):
        projects = sorted(list(set(map(lambda x: x[2], data))))
        dates = sorted(list(set(map(lambda x: x[1], data))))
        tbl_data = [['DATE', "DAY"] + [self.tools.set_color(p, None, 3) for p in projects] + [
            self.tools.set_color("TOTAL", None, 1)]]
        totals = [0 for x in projects] + [0]
        for date in dates:
            gathered_data = self.get_lines(data, date, projects)
            for i in range(0, len(gathered_data)):
                totals[i] += gathered_data[i]
            tbl_data.append([
                                date,
                                DAYS[date.weekday()]
                            ] + [
                                self.tools.set_color(x or "", None, 3) for x in gathered_data[:-1]
                            ] + [
                                self.tools.set_color(gathered_data[-1], None, 1)
                            ])
        tbl_data += [[self.tools.set_color(x, None, 1) for x in (['TOTAL', ""] + totals)]]
        table_instance = SingleTable(tbl_data)
        table_instance.inner_heading_row_border = True
        table_instance.inner_column_border = True
        table_instance.outer_border = True
        click.echo(table_instance.table)

    def get_lines(self, data, date, projects):
        tbl_data = []
        total = 0
        for project in projects:
            time = 0
            for x_id, x_date, x_project, x_time in data:
                if x_project == project and x_date == date:
                    time += x_time
            tbl_data.append(time)
            total += time
        return tbl_data + [total]


class Sign(object):
    def __init__(self, time=0, project=None, date=datetime.today().date()):
        self.time = time
        self.project = project
        if not date:
            date = datetime.today().date()
        self.date = date
        self.id = None

    def load(self, data):
        self.time = data.get('time', 0)
        self.project = data.get('project', None)
        self.id = data.get('id', 1)
        self.date = data.get('date', None)

    def set_time(self, time):
        self.time = time

    def set_project(self, project):
        self.project = project

    def set_date(self, date):
        self.date = date

    def dump(self):
        return {
            'time': self.time,
            'project': self.project,
            'id': self.id,
            'date': self.date,
        }


def __get_from_to(date, r_from, r_to, today, yesterday, tomorrow, this_week, next_week, last_week, this_month,
                  next_month, last_month):
    _today = datetime.today().date()
    weekday = _today.weekday()
    if date:
        _date = parser.parse(date).date()
        r_from = _date + relativedelta(days=0)
        r_to = _date + relativedelta(days=0)
    if today:
        r_from = _today + relativedelta(days=0)
        r_to = _today + relativedelta(days=0)
    if tomorrow:
        r_from = _today + relativedelta(days=1)
        r_to = _today + relativedelta(days=1)
    if yesterday:
        r_from = _today + relativedelta(days=-1)
        r_to = _today + relativedelta(days=-1)
    if this_week:
        r_from = _today + relativedelta(days=-weekday)
        r_to = _today + relativedelta(days=-weekday + 6)
    if next_week:
        x_today = _today + relativedelta(days=7)
        r_from = x_today + relativedelta(days=-weekday)
        r_to = x_today + relativedelta(days=-weekday + 6)
    if last_week:
        x_today = _today + relativedelta(days=-7)
        r_from = x_today + relativedelta(days=-weekday)
        r_to = x_today + relativedelta(days=-weekday + 6)
    if this_month:
        r_from = _today + relativedelta(day=1)
        r_to = _today + relativedelta(day=calendar.monthrange(_today.year, _today.month)[1])
    if next_month:
        x_today = _today + relativedelta(months=1)
        r_from = x_today + relativedelta(day=1)
        r_to = x_today + relativedelta(day=calendar.monthrange(x_today.year, x_today.month)[1])
    if last_month:
        x_today = _today + relativedelta(months=-1)
        r_from = x_today + relativedelta(day=1)
        r_to = x_today + relativedelta(day=calendar.monthrange(x_today.year, x_today.month)[1])
    if r_from and not isinstance(r_from, type(datetime.today().date())):
        r_from = parser.parse(r_from).date()
    if r_to and not isinstance(r_to, type(datetime.today().date())):
        r_to = parser.parse(r_to).date()
    if not r_from:
        r_from = _today + relativedelta(days=0)
    if not r_to:
        r_to = _today + relativedelta(days=0)
    click.secho('From: %s To: %s' % (r_from, r_to), fg="green")
    return r_from, r_to


def _explode(inputs):
    res = []
    for item in inputs:
        for input in item.split():
            input = input.replace(',', '.')
            count = ''
            for i, c in enumerate(input):
                if c.isdigit() or c == '.':
                    count += c
                else:
                    break
            project = input[i:]
            res.append((count, project))
    return res


@click.command()
@click.argument('inputs', nargs=-1)
@click.option('--select', '-s', type=click.STRING, multiple=True, help="Select lines")
@click.option('--add', '-a', type=click.STRING, multiple=True, nargs=2, help="Add lines")
@click.option('--delete', is_flag=True, default=False, help="Delete lines")
@click.option('--delete-all', is_flag=True, default=False, help="Delete all lines")
@click.option('--set-time', type=click.FLOAT, help="set a time for lines")
@click.option('--set-project', type=click.STRING, help="Set a project for lines")
@click.option('--set-date', type=click.STRING, help="Set a date for lines")
@click.option('--list', '-l', 'r_list', is_flag=True, default=False, help="List lines")
@click.option('--calendar', is_flag=True, default=False, help="Show calendar")
@click.option('--date', type=click.STRING, help="filter by date")
@click.option('--from', 'r_from', type=click.STRING, help="filter by date start")
@click.option('--to', 'r_to', type=click.STRING, help="filter by date end")
@click.option('--this-week', is_flag=True, default=False, help="filter by this week")
@click.option('--today', is_flag=True, default=False, help="filter by today")
@click.option('--yesterday', is_flag=True, default=False, help="filter by yesterday")
@click.option('--tomorrow', is_flag=True, default=False, help="filter by tomorrow")
@click.option('--last-week', is_flag=True, default=False, help="filter by last week")
@click.option('--next-week', is_flag=True, default=False, help="filter by next week")
@click.option('--this-month', is_flag=True, default=False, help="filter by this month")
@click.option('--last-month', is_flag=True, default=False, help="filter by last month")
@click.option('--next-month', is_flag=True, default=False, help="filter by next month")
@click.option('--test', type=click.INT, default=0, help="Play some tests")
@click.pass_context
def signcli(ctx,
            inputs,
            select,
            add,
            delete,
            delete_all,
            set_time,
            set_project,
            set_date,
            r_list,
            calendar,
            date,
            r_from,
            r_to,
            this_week,
            next_week,
            last_week,
            this_month,
            next_month,
            last_month,
            today,
            yesterday,
            tomorrow,
            test):
    add = list(add) + _explode(inputs)
    r_from, r_to = __get_from_to(date, r_from, r_to, today, yesterday, tomorrow, this_week, next_week, last_week,
                                 this_month, next_month, last_month)
    if set_date:
        set_date = parser.parse(set_date).date()
    if date:
        date = parser.parse(date).date()
    collection = Signs(SIGN_FILE, Tools(), test)
    signs = collection.find(select, r_from, r_to)
    if delete_all:
        collection.reset()
    for time, project in add:
        try:
            time = float(time)
        except Exception as e:
            click.secho("Time %s is not float" % time, fg="red")
            sys.exit(-1)
        sign = Sign(time=time, project=project)
        signs.append(sign)
        collection.add(sign)
    if set_time:
        collection.apply(signs, time=set_time)
    if set_project:
        collection.apply(signs, project=set_project)
    if set_date:
        collection.apply(signs, date=set_date)
    if delete:
        collection.apply(signs, delete=True)
        old_signs = signs[:]
        for sign in signs:
            old_signs.remove(sign)
        signs = old_signs
    r_list = r_list or select or add or (
        date, r_from, r_to, this_week, next_week, last_week, this_month, next_month, last_month)
    r_list = r_list or (not select and not add)
    if r_list:
        collection.show(signs=signs, calendar=calendar, r_from=r_from, r_to=r_to)
    collection.dump()


if __name__ == '__main__':
    signcli(obj={})
    # todocli(obj={})


def maintodo():
    return todocli(obj={})


def mainsign():
    return signcli(obj={})
