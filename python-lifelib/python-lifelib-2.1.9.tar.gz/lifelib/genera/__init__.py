
import os
import re
from importlib import import_module
from .genuslist import genus_list
from .exceptions import NonCanonicalError
from .rulefiles import rule2files

def obtain_genus(rulestring):

    for g in genus_list:
        m = re.match(g['regex'] + '$', rulestring)
        if m is not None:
            return g['name']

    raise ValueError('Rule "%s" does not belong to any genus' % rulestring)

def genus_to_module(genus):

    m = import_module('.' + genus, __name__)

    return m

def rule_property(rulestring, attribute):

    m = genus_to_module(obtain_genus(rulestring))
    attr = getattr(m, attribute)
    if callable(attr):
        attr = attr(rulestring)
    return attr

def create_rule(rulestring):

    rule_property(rulestring, 'create_rule')

def sanirule(rulestring):

    if '.' in rulestring:
        rulestring = rule2files(rulestring)
        if (rulestring[0] != 'x'):
            raise ValueError("Rules specified by table/tree/code files must begin with a capital letter.")

    rulestring = rulestring.lower()

    if (len(rulestring) > 7) and (rulestring[-7:] == 'history'):
        return sanirule(rulestring[:-7]) + 'History'

    if '/' in rulestring:
        rparts = rulestring.split('/')
        if (len(rparts) <= 3):
            p = ['s', 'b', 'g'] # default parsing order == survivals/births/generations
            d = {}
            for r in rparts:
                if (len(r) > 0) and (r[0] in p):
                    d[r[0]] = r[1:]
                    p = [x for x in p if (x != r[0])]
                else:
                    d[p[0]] = r
                    p = p[1:]
            if ('g' in d) and (int(d['g']) >= 3):
                rulestring = 'g%sb%ss%s' % (d['g'], d['b'], d['s'])
            else:
                rulestring = 'b%ss%s' % (d['b'], d['s'])
        else:
            rulestring = rulestring.replace('/', '')

    return rulestring
