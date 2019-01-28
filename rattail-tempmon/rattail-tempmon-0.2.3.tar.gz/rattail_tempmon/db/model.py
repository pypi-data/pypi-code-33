# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Data models for tempmon
"""

from __future__ import unicode_literals, absolute_import

import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

from rattail import enum
from rattail.db.model import uuid_column
from rattail.db.model.core import ModelBase


Base = declarative_base(cls=ModelBase)


@six.python_2_unicode_compatible
class Appliance(Base):
    """
    Represents an appliance which is monitored by tempmon.
    """
    __tablename__ = 'appliance'
    __table_args__ = (
        sa.UniqueConstraint('name', name='appliance_uq_name'),
    )

    uuid = uuid_column()

    name = sa.Column(sa.String(length=255), nullable=False, doc="""
    Human-friendly (and unique) name for the appliance.
    """)

    appliance_type = sa.Column(sa.Integer(), nullable=True, doc="""
    Code indicating which "type" of appliance this is.
    """)

    location = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description of the appliance's physical location.
    """)

    image_raw = sa.Column(sa.LargeBinary(), nullable=True, doc="""
    Byte sequence of the raw image, as uploaded.
    """)

    image_normal = sa.Column(sa.LargeBinary(), nullable=True, doc="""
    Byte sequence of the normalized image, i.e. "reasonable" size.
    """)

    image_thumbnail = sa.Column(sa.LargeBinary(), nullable=True, doc="""
    Byte sequence of the thumbnail image.
    """)

    def __str__(self):
        return self.name


@six.python_2_unicode_compatible
class Client(Base):
    """
    Represents a tempmon client.
    """
    __tablename__ = 'client'
    __table_args__ = (
        sa.UniqueConstraint('config_key', name='client_uq_config_key'),
    )

    uuid = uuid_column()
    config_key = sa.Column(sa.String(length=50), nullable=False)
    hostname = sa.Column(sa.String(length=255), nullable=False)
    location = sa.Column(sa.String(length=255), nullable=True)

    disk_type = sa.Column(sa.Integer(), nullable=True, doc="""
    Integer code representing the type of hard disk used, if known.  The
    original motivation for this was to keep track of whether each client
    (aka. Raspberry Pi) was using a SD card or USB drive for the root disk.
    """)

    delay = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of seconds to delay between reading / recording temperatures.  If
    not set, a default of 60 seconds will be assumed.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Any arbitrary notes for the client.
    """)

    enabled = sa.Column(sa.DateTime(), nullable=True, doc="""
    This will either be the date/time when the client was most recently
    enabled, or null if it is not currently enabled.  If set, the client will
    be expected to take readings (but only for "enabled" probes) and the server
    will monitor them to ensure they are within the expected range etc.
    """)

    online = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Whether the client is known to be online currently.  When a client takes
    readings, it will mark itself as online.  If the server notices that the
    readings have stopped, it will mark the client as *not* online.
    """)

    archived = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating this client is "archived".  This typically means that the
    client itself no longer exists but that the configuration for it should be
    retained, to be used as a reference later etc.  Note that "archiving" a
    client is different from "disabling" it; i.e. disabling is temporary and
    archiving is more for the long term.
    """)

    def __str__(self):
        return '{} ({})'.format(self.config_key, self.hostname)

    def enabled_probes(self):
        return [probe for probe in self.probes if probe.enabled]


@six.python_2_unicode_compatible
class Probe(Base):
    """
    Represents a probe connected to a tempmon client.
    """
    __tablename__ = 'probe'
    __table_args__ = (
        sa.ForeignKeyConstraint(['client_uuid'], ['client.uuid'], name='probe_fk_client'),
        sa.ForeignKeyConstraint(['appliance_uuid'], ['appliance.uuid'], name='probe_fk_appliance'),
        sa.UniqueConstraint('config_key', name='probe_uq_config_key'),
    )

    uuid = uuid_column()
    client_uuid = sa.Column(sa.String(length=32), nullable=False)

    client = orm.relationship(
        Client,
        doc="""
        Reference to the tempmon client to which this probe is connected.
        """,
        backref=orm.backref(
            'probes',
            cascade='all, delete-orphan',
            doc="""
            List of probes connected to this client.
            """))

    config_key = sa.Column(sa.String(length=50), nullable=False)

    appliance_type = sa.Column(sa.Integer(), nullable=False)

    appliance_uuid = sa.Column(sa.String(length=32), nullable=True)
    appliance = orm.relationship(
        Appliance,
        doc="""
        Reference to the appliance which this probe monitors.
        """,
        backref=orm.backref(
            'probes',
            doc="""
            List of probes which monitor this appliance.
            """))

    description = sa.Column(sa.String(length=255), nullable=False, doc="""
    General human-friendly description for the probe.
    """)

    location = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description of the probe's physical location, relative to the appliance.
    """)

    device_path = sa.Column(sa.String(length=255), nullable=True)

    enabled = sa.Column(sa.DateTime(), nullable=True, doc="""
    This will either be the date/time when the probe was most recently enabled,
    or null if it is not currently enabled.  If set, the client will be
    expected to take readings for this probe, and the server will monitor them
    to ensure they are within the expected range etc.
    """)

    critical_temp_max = sa.Column(sa.Integer(), nullable=False, doc="""
    Maximum high temperature; when a reading is greater than or equal to this
    value, the probe's status becomes "critical high temp".
    """)

    critical_max_started = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the probe readings started to indicate "critical high temp"
    status.  This should be null unless the probe currently has that status.
    """)

    critical_max_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of minutes the probe is allowed to have "critical high temp" status,
    before the first email alert is sent for that.  If empty, there will be no
    delay and the first email will go out as soon as that status is reached.
    If set, should probably be a *low* number.
    """)

    good_temp_max = sa.Column(sa.Integer(), nullable=False, doc="""
    Maximum good temperature; when a reading is greater than or equal to this
    value, the probe's status becomes "high temp" (unless the reading also
    breaches the :attr:`critical_temp_max` threshold).
    """)

    good_max_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of minutes the probe is allowed to have "high temp" status, before
    the first email alert is sent for that.  This is typically meant to account
    for the length of the defrost cycle, so may be a rather large number.
    """)

    good_max_started = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the probe readings started to indicate "high temp" status.
    This should be null unless the probe currently has either "high temp" or
    "critical high temp" status.
    """)

    good_temp_min = sa.Column(sa.Integer(), nullable=False, doc="""
    Minimum good temperature; when a reading is less than or equal to this
    value, the probe's status becomes "low temp" (unless the reading also
    breaches the :attr:`critical_temp_min` threshold).
    """)

    good_min_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of minutes the probe is allowed to have "low temp" status, before
    the first email alert is sent for that.
    """)

    good_min_started = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the probe readings started to indicate "low temp" status.
    This should be null unless the probe currently has either "low temp" or
    "critical low temp" status.
    """)

    critical_temp_min = sa.Column(sa.Integer(), nullable=False, doc="""
    Minimum low temperature; when a reading is less than or equal to this
    value, the probe's status becomes "critical low temp".  If empty, there
    will be no delay and the first email will go out as soon as that status is
    reached.
    """)

    critical_min_started = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the probe readings started to indicate "critical low temp"
    status.  This should be null unless the probe currently has that status.
    """)

    critical_min_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of minutes the probe is allowed to have "critical low temp" status,
    before the first email alert is sent for that.  If empty, there will be no
    delay and the first email will go out as soon as that status is reached.
    """)

    error_started = sa.Column(sa.DateTime(), nullable=True, doc="""
    Timestamp when the probe readings started to indicate "error" status.  This
    should be null unless the probe currently has that status.
    """)

    error_timeout = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of minutes the probe is allowed to have "error" status, before the
    first email alert is sent for that.  If empty, there will be no delay and
    the first email will go out as soon as that status is reached.
    """)

    # TODO: deprecate / remove this
    therm_status_timeout = sa.Column(sa.Integer(), nullable=False, doc="""
    NOTE: This field is deprecated; please set the value for High Timeout instead.
    """)

    status_alert_timeout = sa.Column(sa.Integer(), nullable=False, doc="""
    Number of minutes between successive status alert emails.  These alerts
    will continue to be sent until the status changes.  Note that the *first*
    alert for a given status will be delayed according to the timeout for that
    status.
    """)

    notes = sa.Column(sa.Text(), nullable=True, doc="""
    Any arbitrary notes for the probe.
    """)

    status = sa.Column(sa.Integer(), nullable=True)
    status_changed = sa.Column(sa.DateTime(), nullable=True)
    status_alert_sent = sa.Column(sa.DateTime(), nullable=True)

    def __str__(self):
        return self.description

    def last_reading(self):
        """
        Returns the reading which was taken most recently for this probe.
        """
        session = orm.object_session(self)
        return session.query(Reading)\
                      .filter(Reading.probe == self)\
                      .order_by(Reading.taken.desc())\
                      .first()

    def start_status(self, status, time):
        """
        Update the "started" timestamp field for the given status.  This is
        used to track e.g. when we cross the "high temp" threshold, as a
        separate event from when the "critical high temp" threshold is reached.

        Note that in addition to setting the appropriate timestamp field, this
        also will clear out other timestamp fields, according to the specific
        (new) status.
        """
        if status in (enum.TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP,
                      enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP):
            self.critical_max_started = time
            # note, we don't clear out "high temp" time
            self.good_min_started = None
            self.critical_min_started = None
            self.error_started = None

        elif status == enum.TEMPMON_PROBE_STATUS_HIGH_TEMP:
            self.critical_max_started = None
            self.good_max_started = time
            self.good_min_started = None
            self.critical_min_started = None
            self.error_started = None

        elif status == enum.TEMPMON_PROBE_STATUS_LOW_TEMP:
            self.critical_max_started = None
            self.good_max_started = None
            self.good_min_started = time
            self.critical_min_started = None
            self.error_started = None

        elif status == enum.TEMPMON_PROBE_STATUS_CRITICAL_LOW_TEMP:
            self.critical_max_started = None
            self.good_max_started = None
            # note, we don't clear out "low temp" time
            self.critical_min_started = time
            self.error_started = None

        elif status == enum.TEMPMON_PROBE_STATUS_ERROR:
            # note, we don't clear out any other status times
            self.error_started = time

    def status_started(self, status):
        """
        Return the timestamp indicating when the given status started.
        """
        if status in (enum.TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP,
                      enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP):
            return self.critical_max_started

        elif status == enum.TEMPMON_PROBE_STATUS_HIGH_TEMP:
            return self.good_max_started

        elif status == enum.TEMPMON_PROBE_STATUS_LOW_TEMP:
            return self.good_min_started

        elif status == enum.TEMPMON_PROBE_STATUS_CRITICAL_LOW_TEMP:
            return self.critical_min_started

        elif status == enum.TEMPMON_PROBE_STATUS_ERROR:
            return self.error_started

    def timeout_for_status(self, status):
        """
        Returns the timeout value for the given status.  This is be the number
        of minutes by which we should delay the initial email for the status.
        """
        if status in (enum.TEMPMON_PROBE_STATUS_CRITICAL_HIGH_TEMP,
                      enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP):
            return self.critical_max_timeout

        elif status == enum.TEMPMON_PROBE_STATUS_HIGH_TEMP:
            return self.good_max_timeout or self.therm_status_timeout

        elif status == enum.TEMPMON_PROBE_STATUS_LOW_TEMP:
            return self.good_min_timeout or self.therm_status_timeout

        elif status == enum.TEMPMON_PROBE_STATUS_CRITICAL_LOW_TEMP:
            return self.critical_min_timeout

        elif status == enum.TEMPMON_PROBE_STATUS_ERROR:
            return self.error_timeout


@six.python_2_unicode_compatible
class Reading(Base):
    """
    Represents a single temperature reading from a tempmon probe.
    """
    __tablename__ = 'reading'
    __table_args__ = (
        sa.ForeignKeyConstraint(['client_uuid'], ['client.uuid'], name='reading_fk_client'),
        sa.ForeignKeyConstraint(['probe_uuid'], ['probe.uuid'], name='reading_fk_probe'),
    )

    uuid = uuid_column()

    client_uuid = sa.Column(sa.String(length=32), nullable=False)
    client = orm.relationship(
        Client,
        doc="""
        Reference to the tempmon client which took this reading.
        """,
        backref=orm.backref(
            'readings',
            cascade='all, delete-orphan'))

    probe_uuid = sa.Column(sa.String(length=32), nullable=False)
    probe = orm.relationship(
        Probe,
        doc="""
        Reference to the tempmon probe which took this reading.
        """,
        backref=orm.backref(
            'readings',
            order_by='Reading.taken',
            cascade='all, delete-orphan'))

    taken = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow)
    degrees_f = sa.Column(sa.Numeric(precision=8, scale=4), nullable=False)

    def __str__(self):
        return str(self.degrees_f)
