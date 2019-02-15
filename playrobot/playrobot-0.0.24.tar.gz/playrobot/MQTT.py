import paho.mqtt.client as paho
import time

SUBSCRIBE = 'PlayRobotAIoT'
BROKER = 'broker.hivemq.com'
CLIENT = 'default'
client = ''
ACTION = ''

def on_message(client, userdata, message):
    time.sleep(1)
    mqttmsg = str(message.payload.decode("utf-8"))
    print("received message =",mqttmsg)
    ACTION(mqttmsg)
    
def send(publish,text):
    client.publish(publish,text)
    
def setProperty(name,action,subscribe = 'PlayRobotAIoT',broker = 'broker.hivemq.com'):
    global SUBSCRIBE,BROKER,CLIENT,ACTION
    SUBSCRIBE = subscribe
    BROKER = broker
    CLIENT = name
    ACTION = action
    
def connect():
    global client,CLIENT,ACTION
    if CLIENT == 'default' or ACTION == '':
        raise BaseException('please using MQTT.setProperty to assign ACTION and CLIENT')
    client = paho.Client(CLIENT)
    ###########MQTT部分###################
    #MQTT client name，注意同名稱會搶線問題
    client.on_message=on_message
    print("connecting to broker ",BROKER)
    client.connect(BROKER)#connect
    client.loop_start() #start loop to process received messages
    
    print("subscribing ")
    
    #subscribe的頻道名稱
    client.subscribe(SUBSCRIBE)
    
