import pendulum

from reposit.auth import RPConnection
from reposit import Controller, Account

user = RPConnection('repositdemo', 'repositdemo')
account = Account(user)

user_keys = account.get_user_keys()

controller = Controller(user, user_key=user_keys[0])

print(controller.get_remaining_charge(pendulum.now().int_timestamp - 10000))
# print(controller.get_solar_generation_data)