from datetime import datetime

from pymongo.collection import Collection

from tmlib.tm_db import open_db

database = open_db()
contacts_collection: Collection = database.contacts
customers: Collection = database.customers

cursor = contacts_collection.find()
for contact in cursor:
    _licences = []
    licences = contact.get('licenses', {})
    if isinstance(licences, dict):
        for licence in licences.values():
            if isinstance(licence, dict):
                if isinstance(licence.get('support_expires'), str):
                    licence['support_expires'] = datetime.strptime(
                        licence['support_expires'], '%m/%d/%Y %H:%M:%S'
                    ).strftime('%Y.%m.%d')
                _licences.append(licence)
                account_registrations = licence.get('account_registrations', {})
                _account_registrations = []
                checkins = licence.get('checkins', [])
                licence.pop('checkins', None)
                if isinstance(account_registrations, dict):
                    for account_registration in account_registrations.values():
                        if checkins and not account_registration.get('checkins'):
                            account_registration['checkins'] = []
                        for checkin in checkins:
                            if isinstance(checkin.get('last_checkin'), str):
                                checkin['last_checkin'] = datetime.strptime(
                                    checkin['last_checkin'], '%m/%d/%Y %H:%M:%S'
                                )
                            if checkin.get('account_number') == account_registration.get('account_number'):
                                checkin.pop('account_number')
                                account_registration['checkins'].append(checkin)
                        _account_registrations.append(account_registration)
                licence['account_registrations'] = _account_registrations
    contact['licenses'] = _licences
    customers.delete_one({'_id': contact['_id']})
    customers.insert_one(contact)
