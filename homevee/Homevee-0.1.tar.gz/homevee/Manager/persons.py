#!/usr/bin/python
# -*- coding: utf-8 -*-

def add_edit_person(username, id, name, nickname, address, latitude, longitude, phonenumber, birthdate, db):
    id = int(id)

    with db:
        cur = db.cursor()

        params = {'name': name, 'nickname': nickname, 'address': address, 'lat': latitude, 'lng': longitude,
                  'birthdate': birthdate, 'number': phonenumber}

        if id is None or id == -1:
            cur.execute("INSERT INTO PEOPLE_DATA (NAME, NICKNAME, ADDRESS, LATITUDE, LONGITUDE, BIRTHDATE, PHONE_NUMBER) VALUES (:name, :nickname, :address, :lat, :lng, :birthdate, :number)",
                        params)
        else:
            params['id'] = id

            cur.execute('UPDATE PEOPLE_DATA SET NAME = :name, NICKNAME = :nickname, ADDRESS = :address, LATITUDE = :lat, LONGITUDE = :lng, BIRTHDATE = :birthdate, PHONE_NUMBER = :number WHERE ID = :id',
                        params)

    return {'result': 'ok'}

def get_persons(db):
    persons = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM PEOPLE_DATA")

        for person in cur.fetchall():
            item = {'id': person['ID'], 'name': person['NAME'], 'nickname': person['NICKNAME'], 'address': person['ADDRESS'],
                    'latitude': person['LATITUDE'], 'longitude': person['LONGITUDE'], 'phonenumber': person['PHONE_NUMBER'],
                    'birthdate': person['BIRTHDATE']}
            persons.append(item)

    return {'persons': persons}