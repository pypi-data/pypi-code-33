#!/usr/bin/python
# -*- coding: utf-8 -*-

def get_shopping_list(username, db):
    items = []

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SHOPPING_LIST")

        for item in cur.fetchall():
            if item['AMOUNT'] is None:
                amount = -1
            else:
                amount = int(item['AMOUNT'])

            items.append({'id': item['ID'], 'amount': amount, 'item': item['ITEM']})

        cur.close()

        return {'items': items}

def add_edit_shopping_list_item(username, id, amount, name, db):
    #Bearbeiten oder Hinzufügen?

    with db:

        cur = db.cursor()

        if id is not "" and id is not None:
            #Add to list
            cur.execute("UPDATE OR IGNORE SHOPPING_LIST SET AMOUNT = :amount, ITEM = :name WHERE ID = :id",
                        {'amount': amount, 'name': name, 'id': id})
        else:
            #Edit list entry

            #Check if entry with same name exists and notify user(???)

            cur.execute("INSERT OR IGNORE INTO SHOPPING_LIST (AMOUNT, ITEM) VALUES (:amount, :name);",
                        {'amount': amount, 'name': name})

    #Existiert bereits? Menge addieren?

    return {'result': 'ok'}

def delete_shopping_list_item(username, id, db):
    with db:
        cur = db.cursor()
        cur.execute("DELETE FROM SHOPPING_LIST WHERE ID == :id",
            {'id': id})

        #Abfrage erfolgreich?
        if True:
            return {'result': 'ok'}
        else:
            return {'result': 'noadmin'}