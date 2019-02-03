#!/usr/bin/python
# -*- coding: utf-8 -*-

def get_calendar_item_dates(username, year, db):
    calendar_item_dates = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT DISTINCT DATE FROM CALENDAR WHERE strftime('%Y', DATE) = :year",
                    {'year': year})

        for calendar_entry in cur.fetchall():
            calendar_item_dates.append(calendar_entry['DATE'])

    return {'dates': calendar_item_dates}

def get_calendar_day_items(username, date, db):
    calendar_items = []

    with db:
        cur = db.cursor()

        params = {'date': date}

        cur.execute("SELECT * FROM CALENDAR WHERE DATE = :date ORDER BY START ASC", params)

        for calendar_entry in cur.fetchall():
            item = {'name': calendar_entry['NAME'], 'id': calendar_entry['ID'], 'start': calendar_entry['START'],
                    'end': calendar_entry['END'], 'note': calendar_entry['NOTE'], 'address': calendar_entry['ADDRESS']}
            calendar_items.append(item)

    return {'calendar_entries': calendar_items}

def delete_entry(username, id, db):
    return {'result': 'ok'}

def add_edit_entry(username, entry_id, name, date, start, end, note, address, db):
    entry_id = int(entry_id)

    with db:
        cur = db.cursor()

        params = {'name': name, 'date': date, 'start': start, 'end': end, 'note': note, 'address': address}

        if entry_id is None or entry_id == -1:
            #Create new
            print("insert")
            cur.execute("INSERT INTO CALENDAR (NAME, START, END, NOTE, DATE, ADDRESS) VALUES (:name, :start, :end, :note, :date, :address)",
                        params)
        else:
            #Edit existing
            print("update")

            params['id'] = entry_id

            cur.execute("UPDATE CALENDAR SET NAME = :name, START = :start, END = :end, NOTE = :note, DATE = :date, ADDRESS = :address WHERE ID = :id",
                        params)

    return {'result': 'ok'}