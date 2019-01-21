#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import netifaces


def get_local_ips():
    """Get the ips of the current machine."""
    inet_addrs = [netifaces.ifaddresses(iface).get(netifaces.AF_INET)
                  for iface in netifaces.interfaces()]
    ips = []
    for addr in inet_addrs:
        if addr is not None:
            for add in addr:
                ips.append(add['addr'])
    return ips


def gen_dict_extract(var, key):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield v
            if hasattr(v, 'items'):
                for result in gen_dict_extract(v, key):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(d, key):
                        yield result


def gen_dict_contains(var, key):
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                yield var
            if hasattr(v, 'items'):
                for result in gen_dict_contains(v, key):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_contains(d, key):
                        yield result


def translate_dict_value(var, key, callback):
    newvar = var.copy()
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                newvar[key] = callback(k, v)
            elif hasattr(v, 'items'):
                newvar[k] = translate_dict_value(v, key, callback)
            elif isinstance(v, list):
                newvar[k] = [translate_dict_value(d, key, callback) for d in v]
        return newvar
    else:
        return var


def translate_dict_item(var, key, callback):
    newvar = var.copy()
    if hasattr(var, 'items'):
        for k, v in var.items():
            if k == key:
                newvar = callback(var, k)
            elif hasattr(v, 'items'):
                newvar[k] = translate_dict_item(v, key, callback)
            elif isinstance(v, list):
                newvar[k] = [translate_dict_item(d, key, callback) for d in v]
        return newvar
    else:
        return var


def translate_dict(var, keys, callback):
    newvar = var.copy()
    if hasattr(var, 'items'):
        if set(var.keys()) & set(keys):
            newvar = callback(var)
        for k, v in newvar.items():
            if hasattr(v, 'items'):
                newvar[k] = translate_dict(v, keys, callback)
            elif isinstance(v, list):
                newvar[k] = [translate_dict(d, keys, callback) for d in v]
        return newvar
    else:
        return var
