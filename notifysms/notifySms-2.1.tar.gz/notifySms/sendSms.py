'''
    This program helps to send sms notification to specified mobile.

    usage :
    1. Using Program to send sms
        python sendSms.py [<Message needs to be sent>]
    2. Using module in other script to nofiy via sms
       from sendSms import send_sms
       send_sms(<msg>,[<To Number>])
'''
import sys
import json
import logging
import base64
import platform
import os
from requests.exceptions import ConnectionError
import requests
import json

logging.basicConfig(level=logging.ERROR, format=" [%(asctime)s][%(levelname)s] %(message)s")

# get request
def send_way2sms(phoneNo, textMessage):
  reqUrl = 'http://www.way2sms.com/api/v1/sendCampaign'
  try:
    req_params = {
    'apikey':os.environ['apikey'],
    'secret':os.environ['secret'],
    'usetype': "stage",
    'phone': phoneNo,
    'message':textMessage,
    'senderid':phoneNo
    }
  except KeyError:
      logging.error("Unable to find API key / Secret token in environment variable \
                    Please set 'apikey' and 'secret' environment variables")
      return None
  except:
        logging.error("Something unexpected happend! Way2Sms Check error \n{}".format(sys.exc_info()))
  return requests.post(reqUrl, req_params).text

CFGFILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
logging.debug("Loading configuration file {} ".format(CFGFILE))

try:
    CONFIG = json.loads(open(CFGFILE).read())
    logging.debug(CONFIG)
except IOError:
    logging.critical("Configuration file not found! \
    Please make sure config.json file is in same directory")
    sys.exit(1)

def send_twilio(to,body):
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    from twilio.http.http_client import TwilioHttpClient
    client = "" #Client(base64.b64decode(CONFIG['account']), base64.b64decode(CONFIG['token']))
    try:
        proxy_client = TwilioHttpClient()
        # assuming your proxy is available via the standard env var https_proxy:
        ## (this is the case on pythonanywhere)
        proxy_client.session.proxies = {'https': os.environ['https_proxy']}
        client = Client(base64.b64decode(CONFIG['account']), base64.b64decode(CONFIG['token']), http_client=proxy_client)
    except KeyError:
        try:
            client = Client(base64.b64decode(CONFIG['account']), base64.b64decode(CONFIG['token']))
            return client.messages.create(to=to, from_=CONFIG['from'], body=body)
        except TypeError:
            logging.error("Please check your config file as properly base64 encoded content")
        except ConnectionError:
            logging.error("Opps !! Check you Internet connection. \n{}".format(sys.exc_info()))
        except TwilioRestException:
            logging.error("Opps!! Check your credentials in config file : \
            {} or server issue \n{}".format(CFGFILE, sys.exc_info()))
        except TypeError:
            logging.error("Please check your config file as properly base64 encoded content")


def send_sms(msg_body, to_num=base64.b64decode(CONFIG['to_default'])):
    '''
    This function is used to send message with give mobile number and message
    '''
    way2sms = False
    try:
        logging.info("Checking way2sms environment variable : " + os.environ['way2sms'])
        way2sms = True
    except KeyError:
        logging.info("Way2SMS not set, Fall back to twilio..")
    try:
        logging.debug("To : {}, From : {}, Message is : {}".format(to_num, CONFIG['from'], msg_body))
        if way2sms == True:
            response = send_way2sms(to_num[3:],msg_body)
        else:
            response = send_twilio(to_num,msg_body)
        logging.info("Response: " + str(response))
        if response == None :
            logging.error("Error while sending message, check error.")
        else:
            logging.info("Message has been sent sucessfully")
    except:
        logging.error("Something unexpected happend! Check error \n{}".format(sys.exc_info()))

def usage():
    ''' This is the help function to print usage

    This program helps to send sms notification to specified mobile.

    usage :
    1. Using Program to send sms
        python sendSms.py [<Message needs to be sent>]
    2. Using module in other script to nofiy via sms
       from sendSms import send_sms
       send_sms(<msg>,[<To Number>])
    '''

if __name__ == '__main__':
    logging.debug("Inside main function")
    msg = "Default msg : " + str(platform.uname())
    if len(sys.argv) > 1:
        msg = ' '.join(sys.argv[1:])
    else:
        usage()
    send_sms(msg)
