#!/usr/bin/python
# -*- coding: utf-8 -*-

def get_place(id, db):
    if(id is None or id == "" or id is -1):
        return None

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM PLACES WHERE ID = :id",
                    {'id': id})

        place = cur.fetchone()

        return place

def get_my_places(username, db):
    with db:
        cur = db.cursor()

        places = []

        cur.execute("SELECT * FROM PLACES")

        for place in cur.fetchall():
            places.append({'id': place['ID'], 'name': place['NAME'], 'address': place['ADDRESS'], 'latitude': place['LATITUDE'], 'longitude': place['LONGITUDE']})

        return {'places': places}

def add_edit_place(username, id, name, address, latitude, longitude, db):
    add_new = (id == None or id == "" or id == "-1")

    with db:
        cur = db.cursor()

        if (add_new):
            cur.execute("INSERT INTO PLACES (NAME, ADDRESS, LATITUDE, LONGITUDE) VALUES (:name, :address, :latitude, :longitude)",
                        {'name': name, 'address': address, 'latitude': latitude, 'longitude': longitude})

            return {'result': 'ok'}

        else:
            cur.execute("UPDATE SCENES SET NAME = :name, ADDRESS = :address, LATITUDE = :latitude, LONGITUDE = :longitude WHERE ID = :id",
                        {'name': name, 'address': address, 'latitude': latitude, 'longitude': longitude, 'id': id})

            return {'result': 'ok'}

def delete_place(username, id, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM PLACES WHERE ID = :id", {'id': id})

    return {'result': 'ok'}