#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .constants import *
import sense_core as sd
from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.mysql import INTEGER


class EmailSendLog(sd.Base, sd.BaseModel):
    __label__ = MONITOR_DATABASE_LABEL
    __tablename__ = 'email_send_log'

    id = Column(INTEGER(11), primary_key=True)
    module = Column(String(64), nullable=False)
    content = Column(String(512))
    uids = Column(String(64))
    email = Column(String(512))
    status = Column(String(16))
    time = Column(DateTime)


class ErrorLog(sd.Base, sd.BaseModel):
    __label__ = MONITOR_DATABASE_LABEL
    __tablename__ = 'error_logs'

    id = Column(INTEGER(11), primary_key=True)
    module_name = Column(String(150))
    title = Column(String(256))
    content = Column(String(4096))
    create_time = Column(DateTime)
    
    
class MsgSendLog(sd.Base, sd.BaseModel):
    __label__ = MONITOR_DATABASE_LABEL
    __tablename__ = 'msg_send_log'

    id = Column(INTEGER(11), primary_key=True)
    module = Column(String(64), nullable=False)
    content = Column(String(512))
    uids = Column(String(64))
    phone = Column(String(512))
    status = Column(String(16))
    time = Column(DateTime)


class ServiceConfig(sd.Base, sd.BaseModel):
    __label__ = MONITOR_DATABASE_LABEL
    __tablename__ = 'service_config'

    id = Column(INTEGER(8), primary_key=True)
    service_name = Column(String(128), nullable=False, unique=True)
    uids = Column(String(256), nullable=False)
    time = Column(DateTime)
    status = Column(INTEGER(1), server_default=text("'0'"))


class Supervisor(sd.Base, sd.BaseModel):
    __label__ = MONITOR_DATABASE_LABEL
    __tablename__ = 'supervisor'

    id = Column(INTEGER(4), primary_key=True)
    username = Column(String(150), nullable=False)
    auth_user_id = Column(INTEGER(11))
    wechat = Column(String(150))
    token = Column(String(64))
    email = Column(String(254))
    phone = Column(String(64))
