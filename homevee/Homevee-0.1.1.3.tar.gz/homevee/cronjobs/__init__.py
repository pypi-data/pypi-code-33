#!/usr/bin/python
# -*- coding: utf-8 -*-
from thread import start_new_thread

import run_automations
import save_sensor_data
import save_energy_data
import user_ping
import video_surveillance
import zwave_value_loader
import philips_hue_value_loader
import weather_updater
import overview_notification
import calendar_reminder
import heating_scheme

def start_cronjobs():
    print "starting cronjobs..."

    # Load Z-Wave values
    start_new_thread(zwave_value_loader.init_thread, ())

    # Load Philips Hue values
    start_new_thread(philips_hue_value_loader.init_thread, ())

    # Save values to database
    start_new_thread(save_sensor_data.init_thread, ())

    # Save values to database
    start_new_thread(save_energy_data.init_thread, ())

    # Update weather cache
    start_new_thread(weather_updater.init_thread, ())

    # User anpingen
    # start_new_thread(cronjobs.user_ping.init_thread, ())

    # Benachrichtigung mit Infos für den Tag senden
    start_new_thread(overview_notification.init_thread, ())

    # Benachrichtigung mit Termin-Erinnerungen
    start_new_thread(calendar_reminder.init_thread, ())

    # Zeitgesteuerte Automatisierungen ausführen
    start_new_thread(run_automations.init_thread, ())

    # Heizplan ausführen
    start_new_thread(heating_scheme.init_thread, ())