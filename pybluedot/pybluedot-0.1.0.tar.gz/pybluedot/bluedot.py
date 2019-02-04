import requests as rs
from loguru import logger
import config
log =logger

# TODO: Code cleanup && document
class Bluedot(object):

# TODO: THreads threads threads, pools pools pools
    def __init__(self, username="SuperCode", password="IDK", sender="PyBluedot"):
        # TEMP: get sloppy  and refactor later
        # TODO: Cleanup
        config.password = self.password = password
        config.username = self.username = username# TEMP: refactor


        config.sender = self.sender = sender

        self.flash =0# TODO: Refactor later
        log = logger
        self.content = "No requests yet"
        self.status=False
        self.response = ""

    def balance(self):
        resp = rs.get(f"http://www.bluedotsms.com/api/mt/GetBalance?User={self.username}&Password={self.password}")
        if resp.status_code==200:
            bal = eval(resp.content)
            bal=bal['Balance'].split(":")
            fbal = {"credits" : bal[1]}
            log.info(f"Your balance is {fbal['credits']}")
            return fbal
            # TEMP: Very clumsy of me



    def __getitem__(self,item):
        # TODO: Refactor here , too messy
        if item=="username":
            return self.username
        elif item=="status":
            return self.status
        elif item=="response":
            return self.response
        else:
            #just get balance
            return self.balance()
        return item# TEMP: just  user cred
    @classmethod
    def send(*dec_args, **dec_kwargs):

        class Decorator(object):
            def __init__(self, func):
                self.func = func
                log = logger

            def __call__(self, *args, **kwargs):
                cls = dec_args[0]
                print(f"Sender Name using {dec_args[1]} ")
                config.sender=dec_args[1]
                pkg = args[0] #string pkg

                # TODO: Send here in thread$
                return self.func(cls._send_sms(msg=pkg['msg'] ,phone=pkg['recipients']))

        return Decorator

    @classmethod
    def _send_sms(self, msg, phone):
        recipients=set() #no duplicates
        if type(phone) is list:
            for rec in phone:
                recipients.add(rec)
            log.info(f"Sending SMS to {len(recipients)} recipients")
        else:
            recipients.add(phone)
            log.warning(f"Pending to {phone}")

        #send it
        rc=",".join(recipients)
        resp  =rs.get(f"http://www.bluedotsms.com/api/mt/SendSMS?user={config.username}&password={config.password}&senderid={config.sender}&channel=Normal&DCS=0&flashsms=0&number={rc}&text={msg}")
        self.response=resp.content
        self.status = resp.status_code
        if resp.status_code != 200:
            log.warning(f"Failed to send SMS to {phone}")
            log.error(f"Got {resp.status_code} as Response")
            return self
        log.debug(f"SMS to {phone}")
        #RETURN client with (balance, contentRQ, pkg)
        return self



client = Bluedot(username="lololo", password="9g00isho")
