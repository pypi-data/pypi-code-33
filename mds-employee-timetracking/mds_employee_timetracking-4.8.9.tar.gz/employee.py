# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, Check
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval


__all__ = ['Employee']
__metaclass__ = PoolMeta


class Employee(ModelSQL, ModelView):
    'Employee'
    __name__ = 'company.employee'

    tariff = fields.Many2One(model_name='employee_timetracking.tariffmodel', 
                string=u'Tariff model', ondelete='RESTRICT', depends=['company'],
                select=True, domain=[('company', '=', Eval('company'))])
    worktime = fields.Many2One(model_name='employee_timetracking.worktimemodel', 
                string=u'Working time model', ondelete='RESTRICT', depends=['company'],
                select=True, domain=[('company', '=', Eval('company'))])
    holidays = fields.Integer(string=u'Holidays', required=True, 
                help=u'Number of holidays per year')
    specleave = fields.Integer(string=u'Special leave', required=True, 
                help=u'Number of special leave days per year')

    @classmethod
    def __setup__(cls):
        super(Employee, cls).__setup__()
        tab_empl = cls.__table__()
        cls._sql_constraints.extend([
            ('holidays_not_neg', 
            Check(tab_empl, tab_empl.holidays >= 0), 
            u"'Holidays' must be positive"),
            ('specleave_not_neg', 
            Check(tab_empl, tab_empl.specleave >= 0), 
            u"'Special leave' must be positive"),
            ])

    @classmethod
    def default_holidays(cls):
        """ default: 0
        """
        return 0
        
    @classmethod
    def default_specleave(cls):
        """ default: 0
        """
        return 0

    @classmethod
    def write(cls, *args):
        """ write item
        """
        actions = iter(args)
        to_check1 = []
        to_check2 = []
        for items, values in zip(actions, actions):
            if 'worktime' in values.keys():
                to_check1.append(values['worktime'])
            if 'tariff' in values.keys():
                to_check2.append(values['tariff'])
        super(Employee, cls).write(*args)

        # update local work time models
        Evaluation = Pool().get('employee_timetracking.evaluation')
        Evaluation.updt_worktime_model(to_check1)
        Evaluation.updt_tariff_model(to_check2)
        
# end Employee
