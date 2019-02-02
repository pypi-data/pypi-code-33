from homevee.Functions.room_data import get_room_name
from homevee.Helper.helper_functions import has_permission


def get_smart_speakers(username, db):
    speakers =[]

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM SMART_SPEAKER ORDER BY LOCATION ASC")

        for speaker in cur.fetchall():
            if has_permission(username, speaker['LOCATION'], db):
                item = {'name': speaker['NAME'], 'id': speaker['ID'], 'key': speaker['KEY'],
                        'location': speaker['LOCATION'], 'location_name': get_room_name(speaker['LOCATION'], db)}

                speakers.append(item)

    return {'speakers': speakers}

def add_edit_smart_speaker(username, db):
    return