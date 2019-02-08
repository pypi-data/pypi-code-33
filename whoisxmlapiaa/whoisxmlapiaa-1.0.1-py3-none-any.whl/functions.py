import requests
import urllib
from colorama import init
init()
from colorama import Fore, Back, Style
import json
import os


def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

def readApiKey():
    api_key = "at_9b2YXdzZYYsJprO7i4fT1DN9KIwip"
    with open('api_key.txt') as my_file:
        my_file.seek(0)
        first_char = my_file.read(1)
        if not first_char:
            print("INFO: Using default api key")
            remainingBalance = requests.get(
                "https://www.whoisxmlapi.com/accountServices.php?servicetype=accountbalance&apiKey=" + api_key + "&output_format=JSON")
            remainingBalanceData = remainingBalance.json()
            print("Remaining balance: " + str(remainingBalanceData["balance"] - 2) + "/500")
        else:
            my_file.seek(0)
            api_key = my_file.readline()
    return api_key

def save_api_key(api_key):
    try:
        f = open("api_key.txt", "w")
        f.write(str(api_key))
        f.close()
        message = "Api key was written into api_key.txt and will be used"
    except IOError as e:
        message = "Error: Couldn't write api key in api_key.txt"
    return message

def set_default_api_key():
    try:
        f = open("api_key.txt", "w")
        f.close()
        message = "Api key was set to default"
    except IOError as e:
        message = "Error: Couldn't set default api key"
    return message

def internet_on():
    try:
        urllib.request.urlopen('http://google.com', timeout=1)
        return True
    except urllib.error.URLError as e:
        return False

def getRequest(args,api_key):
    return requests.get('https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey='+api_key+'&domainName=' + args['domain'] + '&outputFormat=JSON')

def basicInfo(data):
    basic = '' + Fore.RED + '------------------\n' \
            'Basic information:\n' \
            '------------------' + Style.RESET_ALL + '\n' \
            'Domain name:                   ' + data['domainName'] + '\n' \
            'Domain name extension:         ' + data['domainNameExt'] + '\n' \
            'Created date:                  ' + data['registryData']['createdDateNormalized'] + '\n' \
            'Updated date:                  ' + data['registryData']['updatedDateNormalized'] + '\n' \
            'Expires date:                  ' + data['registryData']['expiresDateNormalized'] + '\n' \
            'Estimated domain age:          ' + str(data['estimatedDomainAge']) + ' days' + '\n' \
            'Domain EEP status:             ' + data['registryData']['status'] + '\n' \
            'Registrar name:                ' + data['registrarName'] + '\n' \
            'Registrar Assigned ID:         ' + data['registrarIANAID'] + '\n' \
            'Whois server:                  ' + data['registryData']['whoisServer']
    return basic


def hostNames(data):
    i = 0
    hostNames = data['registryData']['nameServers']['hostNames']
    host = '' + Fore.MAGENTA + '-----------\n' \
           'Host names:\n' \
           '-----------' + Style.RESET_ALL + '\n'
    for hostName in hostNames:
        host = host + 'Host name {i}:                   '.format(i=i) + hostName + '\n'
        i += 1
    host = remove_last_line_from_string(host)
    return host


def organizationInfo(data):
    found = False
    organization = '' + Fore.GREEN + '-------------------------\n' \
                   'Organization information:\n' \
                   '-------------------------' + Style.RESET_ALL + '\n'
    if ('registrant' in data):
        found = True
        if ('organization' in data['registrant']):
            organization = organization + 'Organization name:             ' + data['registrant']['organization'] + '\n'
        if ('name' in data['registrant']):
            organization = organization + 'Name:                          ' + data['registrant']['name'] + '\n' \
                            'Country:                       ' + data['registrant']['country'] + '\n' \
                            'Country code:                  ' + data['registrant']['countryCode'] + "\n"
        if ('city' in data['registrant']):
            organization = organization + 'City:                          ' + data['registrant']['city'] + '\n'
        if ('street1' in data['registrant']):
            organization = organization + 'Street:                        ' + data['registrant']['street1'] + '\n'
        organization = remove_last_line_from_string(organization)
        return organization
    if ('registrant' in data['registryData'] and found == False):
        if ('organization' in data['registryData']['registrant']):
            organization = organization + 'Organization name:             ' + data['registryData']['registrant']['organization'] + '\n'
        if ('name' in data['registryData']['registrant']):
            organization = organization + 'Name:                          ' + data['registryData']['registrant']['name'] + '\n' \
                            'Country:                       ' + data['registryData']['registrant']['country'] + '\n' \
                            'Country code:                  ' + data['registryData']['registrant']['countryCode'] + "\n"
        if ('city' in data['registryData']['registrant']):
            organization = organization + 'City:                          ' + data['registryData']['registrant']['city'] + '\n'
        if ('street1' in data['registryData']['registrant']):
            organization = organization + 'Street:                        ' + data['registryData']['registrant']['street1'] + '\n'
        organization = remove_last_line_from_string(organization)
        return organization


def contactInfo(data):
    contact = '' + Fore.BLUE + '--------------------\n' \
              'Contact information:\n' \
              '--------------------' + Style.RESET_ALL + '\n'
    if ('contactEmail' in data):
        contact = contact + 'Email:                         ' + data['contactEmail'] + '\n'
    if ('registrant' in data):
        if ('telephone' in data['registrant']):
            contact =  contact + 'Telephone:                     ' + data['registrant']['telephone'] + '\n'
        if ('fax' in data['registrant']):
            contact = contact + 'Fax:                           ' + data['registrant']['fax'] + '\n'
    if ('registrant' in data['registryData']):
        if ('telephone' in data['registryData']['registrant']):
            contact = contact + 'Telephone:                     ' + data['registryData']['registrant']['telephone'] + '\n'
        if ('fax' in data['registryData']['registrant']):
            contact = contact + 'Fax:                           ' + data['registryData']['registrant']['fax'] + '\n'
    if ('customField1Value' in data):
        contact = contact + 'Registrar email:               ' + data['customField1Value'] + '\n'
    if ('customField2Value' in data):
        contact = contact + 'Registrar telephone:           ' + data['customField2Value'] + '\n'
    if ('customField3Value' in data):
        contact = contact + 'Registrar URL:                 ' + data['customField3Value'] + '\n'
    contact = remove_last_line_from_string(contact)
    return contact

def domainErrorTest(args,api_key):
    request = getRequest(args,api_key)
    rawdata = request.json()

    if ("ErrorMessage" in rawdata or "dataError" in rawdata['WhoisRecord']):
        return True
    else:
        return False

