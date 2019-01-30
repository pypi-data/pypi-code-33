# -*- coding: utf-8 -*-

from trytond.pool import Pool
from .presence import PresenceType
from .breaktime import BreakTime
from .accountrule import AccountRule
from .tariffmodel import TariffModel, PresenceRel
from .employee import Employee
from .period import Period
from .timeaccount import TimeAccount, TimeAccountItem
from .evaluation import Evaluation, EvaluationItem, RecalcEvaluation, EvaluationWorktime,\
    EvaluationBreakTime
from .dayofevaluation import DaysOfEvaluation
from .user import User
from .evaluation_report import EvaluationMonthOdt
from .period_wizard import PeriodAttendanceWizard, PeriodAttendanceWizardStart
from .employee_wizard import EmployeeCreateWizard, EmployeeCreateWizardStart
from .worktimemodel import WorkTimeModel, WorkTimeRule
from .holiday import Holiday

def register():
    Pool.register(
        User,
        PresenceType,
        BreakTime,
        AccountRule,
        TariffModel,
        PresenceRel,
        Employee,
        Period,
        TimeAccount,
        TimeAccountItem,
        Evaluation,
        EvaluationItem,
        EvaluationWorktime,
        EvaluationBreakTime,
        DaysOfEvaluation,
        WorkTimeModel,
        WorkTimeRule,
        Holiday,
        PeriodAttendanceWizardStart,
        EmployeeCreateWizardStart,
        module='employee_timetracking', type_='model')
    Pool.register(
        EvaluationMonthOdt,
        module='employee_timetracking', type_='report')
    Pool.register(
        PeriodAttendanceWizard,
        EmployeeCreateWizard,
        RecalcEvaluation,
        module='employee_timetracking', type_='wizard')
