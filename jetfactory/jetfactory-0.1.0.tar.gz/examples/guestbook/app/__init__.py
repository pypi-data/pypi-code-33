# -*- coding: utf-8 -*-

from .visitor import svc_visitor, VisitorModel
from .visit import svc_visit, VisitModel
from .controller import Controller

controller = Controller
models = [VisitorModel, VisitModel]
services = [svc_visitor, svc_visit]
