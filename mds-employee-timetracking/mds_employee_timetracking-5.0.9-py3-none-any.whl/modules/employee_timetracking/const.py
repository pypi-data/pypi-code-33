# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# timeaccount.py
WF_ACCOUNT_CREATED = 'c'
WF_ACCOUNT_EXAMINE = 'e'
WF_ACCOUNT_LOCK = 'l'
WF_ACCOUNT_EVALUATED = 'v'

# period.py
WF_PERIOD_CREATED = 'c'
WF_PERIOD_EXAMINE = 'e'
WF_PERIOD_LOCK = 'l'


# evaluation
WF_EVALUATION_CREATED = 'c'
WF_EVALUATION_ACTIVE = 'a'
WF_EVALUATION_LOCK = 'l'


sel_weekday = [
        ('0', u'Mon'),
        ('1', u'Tue'),
        ('2', u'Wed'),
        ('3', u'Thu'),
        ('4', u'Fri'),
        ('5', u'Sat'),
        ('6', u'Sun'),
    ]

sel_weekday2 = [
        ('0', u'Sun'),
        ('1', u'Mon'),
        ('2', u'Tue'),
        ('3', u'Wed'),
        ('4', u'Thu'),
        ('5', u'Fri'),
        ('6', u'Sat'),
    ]
