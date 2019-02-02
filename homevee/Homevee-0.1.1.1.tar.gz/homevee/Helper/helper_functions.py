#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import socket
import subprocess
import time
import traceback
import urllib
from OpenSSL import crypto
from socket import gethostname

import os
import urllib2

from passlib.hash import pbkdf2_sha512
#from Helper.HTTPRequest import HTTPRequest
from homevee import constants
#from Helper import compression
from homevee.db_utils import get_database_con, set_server_data, get_server_data

'''Prüft, ob der Nutzer die angegebene Berechtigung besitzt'''
def has_permission(username, permission, db):
    permissions = get_permissions(username, db)

    if permissions is None:
        return False
    else:
        return (permission in permissions or 'admin' in permissions)

def get_permissions(username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT PERMISSIONS FROM USERDATA WHERE USERNAME = :user", {'user': username})

        result = cur.fetchone()

        if result is not None:
            permissions = json.loads(result['PERMISSIONS'])['permissions']

            return permissions
        else:
            return None

def save_request_to_db(data, reply, db):
    return

    if 'password' in data:
        del data['password']

    if data['action'] == "arcontrol":
        del data['imagedata']

    with db:
        cur = db.cursor()

        cur.execute("INSERT INTO REQUEST_DATA (RESPONSE) VALUES (:response)",
            {'response': reply})

        request_id = cur.lastrowid

        for key in data.keys():
            cur.execute("INSERT INTO REQUEST_DATA_PARAMS (REQUEST_ID, PARAM_KEY, PARAM_VALUE) VALUES(:id, :key, :value)",
                {'id': request_id, 'key': key, 'value': data[key]})

        cur.close();

        return True

def send_to_client(data, conn, is_http):
    if not is_http:
        print("Sent Response: "+data)
    elif is_http:
        data = 'HTTP/1.1 200 OK\nContent-Type: text/html\n'+data+'\n'
        print("Sent HTTP-Response: "+data)

    #Prüfen, ob alle Daten gesendet wurden
    len_send = conn.send(bytearray(str.encode(data)))
    #len_send = conn.send(compressed_data)
    print("Data: "+str(len(data))+" | Sent: "+str(len_send))

    #if(len_send is 0):
    #    send_to_client(json.dumps({'status': 'error'}), conn, is_http)

def get_rooms(username, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ROOMS")

        rooms = []

        for data in cur.fetchall():
            if has_permission(username, data['LOCATION'], db):
                rooms.append({'name': data['NAME'], 'location': data['LOCATION'], 'icon': data['ICON']})

        cur.close()

        return {'rooms': rooms}

def parse_http_headers(data):
    if data.startswith("GET"):
        print("HTTP-GET-Request")
        #request = HTTPRequest(data).path
        #path, param_string = request.split('?', 1)
    elif data.startswith("POST"):
        print("HTTP-POST-Request")
        lines = data.split('\n')
        param_string = lines[-1]
    else:
        raise AttributeError

    params = {}

    param_fragments = param_string.split('&')

    for param in param_fragments:
        if '=' in param:
            key, value = param.split('=')
            params[key] = value

    return params

def hash_password(password):
    salt = os.urandom(12).encode('hex')

    hashed_pw = pbkdf2_sha512.encrypt(password+salt, rounds=200000)

    #print "Password: "+password
    #print "Salt: "+salt
    #print "Hashed: "+hashed_pw

    return (hashed_pw, salt)

def verify_password(password, salt, hashed_pw):
    return pbkdf2_sha512.verify(password+salt, hashed_pw)

def verify_user(username, password):
    db = get_database_con()

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM USERDATA WHERE USERNAME == :user", {'user': username})

        user = cur.fetchone()

        if(user is None):
            return False

        hashed_pw = user['PASSWORD']
        salt = user['PW_SALT']

        verified = verify_password(password, salt, hashed_pw)

        #print "Username: "+username
        #print "Password: " + password
        #print "Salt: " + salt
        #print "Hashed: " + hashed_pw
        #print "Verified: "+str(verified)

        return verified

def remote_control_enabled(db):
    REMOTE_CONTROL_ENABLED = get_server_data("USE_REMOTE_CONTROL", db)
    return REMOTE_CONTROL_ENABLED == "true"

def set_remote_control_enabled(username, enabled, db):
    if(not has_permission(username, "admin", db)):
        return {'result': 'noadmin'}
    set_server_data("USE_REMOTE_CONTROL", enabled, db)

    return {'result': 'ok'}

def save_remote_data(username, remote_id, linked_account, db):
    if(not has_permission(username, "admin", db)):
        return {'result': 'noadmin'}

    set_server_data("REMOTE_ID", remote_id, db)
    set_server_data("REMOTE_LINKED_ACCOUNT", linked_account, db)

    return {'result': 'ok'}

def load_remote_data(username, db):
    if(not has_permission(username, "admin", db)):
        return {'result': 'noadmin'}

    remote_id = get_server_data("REMOTE_ID", db)
    access_token = get_server_data("REMOTE_ACCESS_TOKEN", db)

    linked_account = get_server_data("REMOTE_LINKED_ACCOUNT", db)

    #check if account is still linked

    #load premium membership
    url = "https://cloud.homevee.de/server-api.php?action=getpremiumuntil&remoteid="+remote_id+"&accesstoken="+access_token
    contents = urllib2.urlopen(url).read()
    data = json.loads(contents)
    is_premium = None

    try:
        is_premium = data['is_premium']
        premium_until = data['premium_until']
    except:
        premium_until = None

    return {'remote_id': remote_id,
            'access_token': access_token,
            'linked_account': linked_account, 'premium_until': premium_until, 'is_premium': is_premium,
            'remote_control_enabled': remote_control_enabled(db)}

def connect_remote_id_with_account(username, account_name, account_secret, db):
    if(not has_permission(username, "admin", db)):
        return {'result': 'noadmin'}

    remote_id = get_server_data("REMOTE_ID", db)
    url = "https://homevee.de/connect-remote-id.php?remote_id="+remote_id+"&account_name="+account_name+"&account_secret="+account_secret

    response = urllib.urlopen(url).read()

    if response == "ok":
        set_server_data("REMOTE_LINKED_ACCOUNT", account_name, db)

    return {'result': response}

def update_ip_thread():
    last_ip = None

    db = get_database_con()

    while(True):
        remote_id = get_server_data("REMOTE_ID", db)
        access_token = get_server_data("REMOTE_ACCESS_TOKEN", db)

        my_ip = get_my_ip()

        if my_ip != last_ip or my_ip != get_my_ip_from_cloud(remote_id):
            update_ip(my_ip, remote_id, access_token)

        last_ip = my_ip

        #wait some time
        time.sleep(5*60) #5 Minuten

def update_cert_thread():
    db = get_database_con()

    while (True):
        remote_id = get_server_data("REMOTE_ID", db)
        access_token = get_server_data("REMOTE_ACCESS_TOKEN", db)

        # generate_cert

        check_cert(None, remote_id, access_token)

        # wait some time
        time.sleep(12 *60 * 60)  # 12 Stunden

def check_cert(db=None, remote_id=None, access_token=None):
    cert_data = get_local_cert()

    if db is not None:
        remote_id = get_server_data("REMOTE_ID", db)
        access_token = get_server_data("REMOTE_ACCESS_TOKEN", db)

    if cert_data is None:
        generate_cert()

    if cert_data != get_my_cert_from_cloud(remote_id):
        update_cert(cert_data, remote_id, access_token)

def update_ip(ip, remote_id, access_token):

    MAX_RETRIES = 10
    retries = 0

    contents = None

    # update local ip in cloud
    url = "https://cloud.homevee.de/server-api.php?action=updatelocalip&remoteid=" + remote_id + "&accesstoken=" + access_token + "&localip=" + ip
    while(contents != "ok" and retries < MAX_RETRIES):
        try:
            contents = urllib2.urlopen(url).read()
        except:
            traceback.print_exc()

        retries += 1

def update_cert(cert_data, remote_id, access_token):
    print "updating local cert..."

    cert_data = cert_data.replace("\n", "")
    cert_data = cert_data.replace("-----BEGIN CERTIFICATE-----", "")
    cert_data = cert_data.replace("-----END CERTIFICATE-----", "")

    MAX_RETRIES = 10
    retries = 0

    contents = None

    # update cert in cloud
    url = "https://cloud.homevee.de/server-api.php?action=updatecert&remoteid=" + remote_id + "&accesstoken=" + access_token + "&cert=" + urllib.quote(
        cert_data)
    print url

    while (contents != "ok" and retries < MAX_RETRIES):
        try:
            contents = urllib2.urlopen(url).read()
        except:
            traceback.print_exc()

        retries += 1

    print contents

def get_my_ip():
    #return "192.168.2.110"

    try:
        cmd = "hostname -i"
        data = subprocess.check_output(cmd, shell=True).decode('utf-8')
        #return "192.168.2.110"
        ip, mac = data.split(" ")
    except:
        ip = socket.gethostbyname(socket.gethostname())

    print "my ip address: " + ip

    return ip

def generate_cert():
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "DE"
    cert.get_subject().ST = "Germany"
    cert.get_subject().L = "Germany"
    cert.get_subject().O = "Homevee"
    cert.get_subject().OU = "Homevee"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    open(constants.LOCAL_SSL_CERT, "wt").write(
        crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    open(constants.LOCAL_SSL_PRIVKEY, "wt").write(
        crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

def get_local_cert():
    if(os.path.isfile(constants.LOCAL_SSL_CERT)):
        file = open(constants.LOCAL_SSL_CERT, "r")
        content = file.read()
        if content is not None and content != '':
            return content

    return None

def get_my_ip_from_cloud(remote_id):
    try:
        url = "http://cloud.homevee.de/server-api.php?action=getlocalip&remoteid="+remote_id
        contents = urllib2.urlopen(url).read()

        data = json.loads(contents)

        if 'ip' in data and data['ip'] is not None:
            return data['ip']
        else:
            return None
    except:
        traceback.print_exc()
        return None

def get_my_cert_from_cloud(remote_id):
    try:
        url = "http://cloud.homevee.de/server-api.php?action=getcert&remoteid="+remote_id
        contents = urllib2.urlopen(url).read()

        data = json.loads(contents)

        if 'cert' in data and data['cert'] is not None:
            return data['cert']
        else:
            return None
    except:
        traceback.print_exc()
        return None
