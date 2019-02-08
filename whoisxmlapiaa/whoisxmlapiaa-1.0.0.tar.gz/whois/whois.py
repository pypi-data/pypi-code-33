import argparse
import requests
import pprint
import json
import functions


arg = argparse.ArgumentParser(description='App that print info about website from whoisxmlapi.')
arg.add_argument("-d", "--domain", required=False,
                help="Domin address")
arg.add_argument("-c", "--contact", action='store_true', required=False,
                help="Contact info")
arg.add_argument("-o", "--organization", action='store_true', required=False,
                help="Organization info")
arg.add_argument("-hn", "--hostNames", action='store_true', required=False,
                help="Host server names")
arg.add_argument("-a", "--all", action='store_true', required=False,
                help="Print everything, except raw json")
arg.add_argument("-rj", "--rawJson", action='store_true', required=False,
                help="Print only raw json")
arg.add_argument("-rjr", "--rawJsonReadable", action='store_true', required=False,
                help="Print only raw json in readable form")
arg.add_argument("-sak", "--setApiKey", required=False,
                help="Set your own API key")
arg.add_argument("-sdk", "--setDefaultKey", action='store_true', required=False,
                help="Set default API key")
arg.add_argument("-uk", "--useKey", required=False,
                help="Use your own API key")
args = vars(arg.parse_args())

if (args["all"] == True):
    args["hostNames"] = True
    args["contact"] = True
    args["organization"] = True

if(args['setApiKey'] != None):
    print(functions.save_api_key(args['setApiKey']))
elif(args['setDefaultKey'] == True):
    print(functions.set_default_api_key())
elif(args['domain'] == None and args['setApiKey'] == None):
    print("Add atleast one argument. For more information type: python3 whois.py --help")
else:
    if (functions.internet_on() == True):
        if (args['useKey'] != None):
            api_key = args['useKey']
        else:
            api_key = functions.readApiKey()

        request = functions.getRequest(args,api_key)
        rawdata = request.json()

        if (functions.domainErrorTest(args,api_key) == True):
            print("Error massage:       domain name \"" + args["domain"] + "\" or API key is invalid")
        elif (args['rawJson'] == True):
            print(rawdata)
        elif (args['rawJsonReadable'] == True):
            pprint.pprint(rawdata)
        else:
            data = rawdata['WhoisRecord']
            print(functions.basicInfo(data))
            if (args['hostNames'] == True):
                print(functions.hostNames(data))
            if (args['organization'] == True):
                print(functions.organizationInfo(data))
            if (args['contact'] == True):
                print(functions.contactInfo(data))
    else:
        print("Error massage:           No internet connection!")
