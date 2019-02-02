#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import socket
import ssl
import sys
import time
import traceback
from thread import start_new_thread
from websocket_server import WebsocketServer
import API
import AESCipher
import constants
import cronjobs
import webinterface
from DeviceAPI import mqtt_api
#from Functions import ar_control, people_classifier
from Functions.chat import send_chat_message
#from Helper import compression
from Helper.helper_functions import save_request_to_db, parse_http_headers, send_to_client, \
    generate_cert, update_ip_thread, update_cert_thread, update_cert, check_cert
from API import process_data
import VoiceAssistant
from cloud_communication import connect_to_cloud, cloud_connection_loop
from constants import END_OF_MESSAGE
from cronjobs import heating_scheme
from cronjobs.overview_notification import send_overview_notifications
from db_utils import get_database_con, set_server_data
from firebase_utils import send_notification_to_users
from smart_speaker_communication import smart_speaker_loop

HOST = ''  # Symbolic name meaning all available interfaces
PORT = 7777  # Arbitrary non-privileged port

#Zeitzone anpassen
os.environ['TZ'] = 'Europe/Berlin'

'''while True:
    data = raw_input("Data: ")
    key = raw_input("Key: ")

    aes = AESCipher.AESCipher(key)
    new_aes = AESCipher.AESCipher(key)
    print("Data: "+data)
    cipher = aes.encrypt(data)
    print("Cipher: "+cipher)
    plain = new_aes.decrypt(cipher)
    print("Plain: "+plain)'''

#aes = AESCipher.AESCipher('3s6v9y$B&E)H@McQfTjWmZq4t7w!z%C*')
#print("Plain: "+aes.decrypt('qYqXviw/9yowSeMeJqkRhC6QUtQdPjFhyUdlzb0Cyz4xddOQbLMpNUjs8hMbk8al'))

#cronjobs.save_energy_data.init_thread()

test_speech = True
if test_speech:
    while(True):
        input = raw_input("Gib einen Sprachbefehl ein: ")
        print(VoiceAssistant.voice_command_cloud("sascha", input, None, None, get_database_con()))

def websocket_client(client, server):
    server.set_fn_message_received(handle_websocket_msg)

def start_websocket_server():
    server = WebsocketServer(7889, host='')
    server.set_fn_new_client(websocket_client)
    server.run_forever()

def handle_websocket_msg(client, server, data):
    # infinite loop so that function do not terminate and thread do not end.
    db = get_database_con()

    sent_data = None

    while True:
        try:
            # Receiving from client
            method_start_time = time.time()

            data = data.decode("utf-8")

            if data == "":
                db.close()
                return

            print("Received: " + str(data))

            is_http = False
            is_resend = False

            error = False

            # Ist HTTP-Aufruf?
            try:
                data = parse_http_headers(data)
                is_http = True
            except AttributeError:
                try:
                    data = json.loads(data)
                    data = json.loads(data['msg'])
                    print("Request is not in HTTP-Format")
                except:
                    print("Data could not be parsed")
                    server.send_message(client, json.dumps({'status': 'error'}))
                    error = True

            '''if 'resend' in data and data['resend'] is True:
                # Daten erneut senden
                print("Resend!")
                is_resend = True
                print(str(len(sent_data)) + " | " + sent_data)

                send_to_client(sent_data[data['resendstart']:], conn, is_http)'''

            if not error and not is_resend:
                if not is_resend:
                    reply = process_data(data, db)

                    reply['computing_time'] = time.time() - method_start_time

                if (reply is not None):
                    server.send_message(client, json.dumps(reply))

                    save_request_to_db(data, reply, db)
                else:
                    print("Error in reply")
                    server.send_message(client, json.dumps({'status': 'error'}))

                if not data:
                    break
        # except socket.error:
        #    break
        except Exception as e:
            traceback.print_exc()
            print("Fehler: " + str(e))
            server.send_message(client, json.dumps({'status': 'error'}))

        # Stop endless loop
        break

    # came out of loop
    db.commit()
    db.close()
    print("Verbindung beendet")

# Function for handling connections. This will be used to create threads
def clientthread(conn):
    # infinite loop so that function do not terminate and thread do not end.
    db = get_database_con()

    is_http = False

    sent_data = None

    while True:
        try:
            # Receiving from client
            method_start_time = time.time()

            data = ""

            while(True):
                new_data = conn.recv(8192)

                #print(new_data)

                #data = data + compression.decompress_string(new_data)

                data = data + new_data

                if(data.endswith(END_OF_MESSAGE)):
                    break

            if data == "":
                db.close()
                conn.close()
                return

            data = data[:len(END_OF_MESSAGE)*-1]

            data = data.decode("utf-8")

            print("Received: " + str(data))

            is_http = False
            is_resend = False

            error = False

            #Ist HTTP-Aufruf?
            try:
                data = parse_http_headers(data)
                is_http = True
            except AttributeError:
                try:
                    data = json.loads(data)
                    data = json.loads(data['msg'])
                    print("Request is not in HTTP-Format")
                except:
                    print("Data could not be parsed")
                    send_to_client(json.dumps({'status': 'error'}), conn, is_http)
                    error = True

            if 'resend' in data and data['resend'] is True:
                #Daten erneut senden
                print("Resend!")
                is_resend = True
                print(str(len(sent_data)) + " | " +sent_data)

                send_to_client(sent_data[data['resendstart']:], conn, is_http)

            if not error and not is_resend:
                if not is_resend:
                    message = process_data(data, db)

                    #print "compressing: "+message

                    #start_time = time.time()
                    #compressed_message = compression.compress_string(message)
                    #end_time = time.time()

                    #print "uncompressed: "+str(len(message))
                    #print "compressed: "+str(len(compressed_message))+", time: "+str(end_time-start_time)

                    #compressed_message = compressed_message.decode('iso-8859-1').encode('utf8')

                    msg = json.dumps({'msg': message, 'computing_time': (time.time() - method_start_time)*1000})

                if(msg is not None):
                    send_to_client(msg, conn, is_http)

                    sent_data = msg

                    save_request_to_db(data, msg, db)
                else:
                    print("Error in reply")
                    send_to_client(json.dumps({'status': 'error'}), conn, is_http)

                if not data:
                    break
        #except socket.error:
        #    break
        except Exception as e:
            traceback.print_exc()
            print("Fehler: "+str(e))
            send_to_client(json.dumps({'status': 'error'}), conn, is_http)

        #Stop endless loop
        break

    # came out of loop
    conn.close()
    db.commit()
    db.close()
    print("Verbindung beendet")

def listen_for_requests(s):
    #s = ssl.wrap_socket(s, keyfile=constants.LOCAL_SSL_PRIVKEY, certfile=constants.LOCAL_SSL_CERT, server_side=True)

    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))

    # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread, (conn,))

# now keep talking with the client

#Smart Speaker Communication
start_new_thread(smart_speaker_loop, ())

#Connect to MQTT-Broker
start_new_thread(mqtt_api.init_client,())

#Start Websocket-Server
#start_new_thread(start_websocket_server, ())

#Start HTTP-Server
#start_new_thread(webinterface.start_http_server, ())

#Start cronjobs
cronjobs.start_cronjobs()

#Communicate with cloud
start_new_thread(cloud_connection_loop, ())

#Lokale IP und Zertifikat regelmäßig aktualisieren
start_new_thread(update_ip_thread, ())
start_new_thread(update_cert_thread, ())

#Reset Image-Classifier flags
#db = get_database_con()
#set_server_data(ar_control.IS_TRAINING_TAG, "false", db)
#set_server_data(people_classifier.IS_TRAINING_TAG, "false", db)

#check if certs exist
check_cert(db=get_database_con())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    traceback.print_exc()
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')

while True:
    try:
        listen_for_requests(s)
    except KeyboardInterrupt:
        break
    except:
        traceback.print_exc()

s.close()
