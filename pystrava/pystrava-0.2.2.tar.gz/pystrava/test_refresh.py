from pystrava import Strava
import os
import logging

logging.basicConfig(level=logging.DEBUG)

old = {'token_type': 'Bearer', 'expires_at': 1549666389, 'expires_in': 21095, 'refresh_token':
    'e101a11aa862eb818d47efada639dc0cef3eb894', 'access_token': 'b27e6e3929fe6b444326d7d83c0dad3d715ba5e8',
       'athlete': {'id': 11286629, 'username': None, 'resource_state': 2, 'firstname': 'Oriol', 'lastname': 'Fabregas', 'city': 'Amsterdam',
                   'state': 'Noord-Holland', 'country': 'Netherlands', 'sex': 'M', 'premium': False, 'summit': False,
                   'created_at': '2015-09-10T21:40:07Z', 'updated_at': '2019-02-08T16:58:23Z', 'badge_type_id': 0,
                   'profile_medium': 'https://dgalywyr863hv.cloudfront.net/pictures/athletes/11286629/3456261/4/medium.jpg',
                   'profile': 'https://dgalywyr863hv.cloudfront.net/pictures/athletes/11286629/3456261/4/large.jpg',
                   'friend': None, 'follower': None}}

expired_token = 'b27e6e3929fe6b444326d7d83c0dad3d715ba5e8'

strava = Strava(client_id=os.environ['CLIENT_ID'],
                client_secret=os.environ['SECRET'],
                callback=os.environ['CALLBACK_URL'],
                scope=os.environ['SCOPE'],
                email=os.environ['EMAIL'],
                password=os.environ['PASSWORD'])
# print(strava.access_token)
# print(dir(strava))
athlete = strava.get_athlete()
print(athlete)
activities = strava.get_activities()
long_activities = []
for activity in activities:
    if any(activity.distance > act.distance for act in long_activities):
        long_activities.append(activity)
# type_activities = {'activities': []}
# for activity in activities:
#     if activity.type == 'ride'.capitalize():
#         type_activities['activities'].append(activity.name)
# print(type_activities)

# strava.deauthorize()
