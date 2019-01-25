from _thread import start_new_thread
from threading import Thread
import threading
import asyncio
import time
from abc import ABC,abstractmethod
import datetime
from time import gmtime, strftime
from requests import Session
import requests
from signalr import Connection
import json
import uuid
from threading import Thread
import asyncio
import subprocess
import sys
import os
from shutil import copyfile
from enum import Enum


class OneiroiHandler:
    daemonURL=None
    clientName=None
    NodeConnections={}
    AutoReConnect=False
    messageText = """<?xml version="1.0" encoding="utf-16"?><testMessage xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" name="TestMessage" sendFrom="NodeA" sendTo="NodeA" soureClient="capp" hide=""><test>MessagetOSend</test></testMessage>"""
    oneiroi=None
    generateDsExist = False
    IsConnected=False
    def handelOneiroi(self,oneiroi):    
        OneiroiHandler.oneiroi.connect_to_Daemon()
        OneiroiHandler.oneiroi.keep_listening()
    def __init__(self,_daemonURL,CleintID,autoReconnect,reConnectInterval,reconnectTimeout):
        self.copyGenerateDs()
        if not OneiroiHandler.oneiroi:
            OneiroiHandler.clientName=CleintID
            OneiroiHandler.daemonURL=_daemonURL
            self.AutoReConnect=autoReconnect
            OneiroiHandler.oneiroi=OneiroiConnection(OneiroiHandler.clientName,OneiroiHandler.daemonURL,autoReconnect,reConnectInterval,reconnectTimeout)
            oneiroiThread=Thread(target=self.handelOneiroi,args=(OneiroiHandler.oneiroi,))
            oneiroiThread.start()             
            time.sleep(10)    
            
    def copyGenerateDs(self):
        if not OneiroiHandler.generateDsExist:
            lst=sys.path
            for a in lst:
                fileCopied=False;
                absolutepath=a+'\Scripts'
                if(os.path.exists(absolutepath)):
                    fileAbsoultePath=absolutepath+'\generateDS.py'
                    print(fileAbsoultePath)
                    copyfile(fileAbsoultePath,'generateDs.py')
                    fileCopied=True
                    OneiroiHandler.generateDsExist=True
    def checkConnectionStatus(self):
        while True:
            if not self.oneiroi.hub.server._HubServer__connection._Connection__greenlet.started:
                self.oneiroi.connect_to_Daemon()
                break
    def Connect_TO_Node(self,NodeName,MessageHandler):
        OneiroiHandler.NodeConnections[NodeName]=MessageHandler
        IsConnected = OneiroiHandler.oneiroi.connect_To_Node(NodeName,MessageHandler)
        return IsConnected
    def Setup_Attribute_Notification(self,NodeName,AttributeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Set_Node_Attribute_Notification(NodeName,AttributeName)
    def Subscribe_To_Node_Message(self,NodeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Subscribe_To_Node_Messages(NodeName)
    def UnSubscribe_From_NodeMessages(self,NodeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.unsubscribe_From_Node_Message(NodeName)
    def Set_Node_Attribute_Value(self,NodeName,AttributeName,AttributeValue):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Set_Attribute_Value(NodeName,AttributeName,AttributeValue)
    def Get_Node_Attribute_Value(self,NodeName,AttributeName):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.get_Attribute_value(NodeName,AttributeName)
    def Send_Message(self,NodeName,xmlMessage):
        if OneiroiHandler.NodeConnections[NodeName]:
            OneiroiHandler.oneiroi.Send_Message(xmlMessage)
    def Send_Message_Object(self,msgObject):        
            OneiroiHandler.oneiroi.Send_Message_Object(msgObject)
    def create_Node_Implementation(self,NodeName): 
        if not OneiroiHandler.generateDsExist:
            print("could not find GenerteDS Pakcage")
            return
        currentNodeDefinition=OneiroiHandler.oneiroi.get_Node_Structure(NodeName)      
        if currentNodeDefinition:
            messageClassImports='';
            messageList=[];
            for messagebinding in currentNodeDefinition['allMessageBindings']:
                msg=messagebinding['MessageType'].lower()
                if not msg in messageList:
                    messageList.append(msg);
                    schema_File=open(msg+'.xsd','w+')
                    schema_File.write(messagebinding['MessageXsdSchema'])
                    schema_File.close()
                    subprocess.call(['python','generateDS.py', '-o',msg+'.py','-s',msg+'_sub.py',msg+'.xsd'])
                    messageClassImports=messageClassImports+'\n'+f'from {msg} import {msg}';
            messageClassImports=messageClassImports+'\n'
            fileName=NodeName+'_Impl1.py'
            f= open(fileName,"w+")
            dt=str(datetime.datetime.now())
            f.write("##becos Oneiroi Node Implementation\n")
            f.write(f"##Auto Generated:{dt} \n\n")
            f.write("from becos import becosOneiroi\n")
            f.write("from becosOneiroi import oneiroiReceiver\n")
            f.write("import xml.etree.ElementTree as xmlParser\n")
            f.write("from lxml import objectify\n")
            f.write(messageClassImports)
            f.write(f"class {NodeName}_Impl(becosOneiroi.oneiroiReceiver):\n")
            f.write("\tdaemonURL="+f"'{self.daemonURL}'\n")
            f.write("\tclientName="+f"'{self.clientName}'\n")
            f.write("\tconHandler=becosOneiroi.OneiroiHandler(daemonURL,clientName,True,5,60)\n")            
            f.write("\texcAttributes=['original_tagname_','name','sendFrom','sendTo','soureClient','hide','ttargetClient','sourceClient','targetClient']\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\t{attribute['attributeName']}=None\n")
            f.write("\tdef OnResponse(self,message):\n") 
            f.write("\t\tprint(message)\n") 
            f.write("\tdef OnConnectionStateChanged(self,newState):\n") 
            f.write("\t\tprint(newState)\n") 
            f.write("\tdef OnNodeResponse(self,NodeName,message):\n") 
            f.write("\t\tprint(f'NodeName:{NodeName},message{message}')\n") 
            f.write("\tdef OnMessageReceived(self,messageID,NodeName,XmlMessage):\n")
            f.write("\t\tres=xmlParser.fromstring(XmlMessage)\n")
            f.write("\t\tmessageType=res.attrib['name']\n")
            for messagebinding in currentNodeDefinition['allMessageBindings']:
                if messagebinding['MessageFlow'].lower()=='inbound':
                    f.write(f"\t\tif messageType.lower()=='{messagebinding['MessageType'].lower()}':\n")
                    f.write(f"\t\t\tself.on_{messagebinding['MessageType'].lower()}_Received(XmlMessage)\n")
            f.write("\tdef OnAttributeValueReceived(self,Client,NodeName,AttributeName,AttributeValue):\n")
            f.write("\t\tprint('')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\t\tif(AttributeName=='{attribute['attributeName']}'):\n")
                f.write(f"\t\t\tself.{attribute['attributeName']}=AttributeValue\n")
            f.write("\tdef __init__(self):\n")
            f.write(f"\t\tself.conHandler.Connect_TO_Node('{NodeName}',self)\n")
            f.write(f"\t\tself.conHandler.Subscribe_To_Node_Message('{NodeName}')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                if attribute['isNotifiable']==True:
                    f.write(f"\t\tself.conHandler.Setup_Attribute_Notification('{NodeName}','{attribute['attributeName']}')\n")
            for attribute in currentNodeDefinition['allAttributes']:
                f.write(f"\tdef set_{attribute['attributeName']}(self,newValue):\n")
                f.write(f"\t\tself.conHandler.Set_Node_Attribute_Value('{NodeName}','{attribute['attributeName']}',newValue)\n")
            for messagebinding in currentNodeDefinition['allMessageBindings']:
                if messagebinding['MessageFlow'].lower()=='inbound':
                    f.write(f"\tdef on_{messagebinding['MessageType'].lower()}_Received(self,xmlMessage):\n")
                    f.write(f"\t\tmessage_received={messagebinding['MessageType'].lower()}()\n")
                    f.write(f"\t\troot = xmlParser.fromstring(xmlMessage)\n")
                    f.write(f"\t\tmessage_received.name=root.attrib['name']\n")
                    f.write(f"\t\tmessage_received.soureClient=root.attrib['soureClient']\n")
                    f.write(f"\t\tmessage_received.targetClient=root.attrib['targetClient']\n")
                    f.write(f"\t\tmessage_received.sendFrom=root.attrib['sendFrom']\n")
                    f.write(f"\t\tmessageAttributes=message_received.__dict__.keys()\n")
                    f.write(f"\t\tfor at in messageAttributes:\n")
                    f.write(f"\t\t\tif not at in self.excAttributes:\n")
                    f.write(f"\t\t\t\tsetattr(message_received,at,root.find(at).text)\n")
                    f.write(f"\t\tprint(xmlMessage)\n")
                else:
                    f.write(f"\tdef send_{messagebinding['MessageType'].lower()}(self,inputMessage : {messagebinding['MessageType']}):\n")
                    f.write(f"\t\txmlMessage=self.getXMLString(inputMessage)\n")
                    f.write(f"\t\tself.conHandler.Send_Message('{NodeName}',xmlMessage)\n")
            f.write(f"\tdef getXMLString(self,inputMessage):\n")
            s="""
\t\txmlMessage="<?xml version='1.0' encoding='utf-8'?>"       
\t\txmlMessage= xmlMessage +f"<{inputMessage.name}  name='{inputMessage.name}' soureClient='{inputMessage.soureClient}' sendFrom='{inputMessage.sendFrom}' sendTo='{inputMessage.sendTo}' hide='' targetClient='{inputMessage.targetClient}'>"
\t\tmessageAttributes=inputMessage.__dict__.keys()     
\t\tfor at in messageAttributes:
\t\t\tif not at in self.excAttributes:
\t\t\t\txmlMessage=xmlMessage+ '  ' + f"<{at}>{getattr(inputMessage,at)}</{at}>"
\t\txmlMessage=xmlMessage+f'</{inputMessage.name}>'
\t\treturn xmlMessage
"""
            f.write(s)
            f.close()
            return True
        else:
            return False

class OneiroiConnection:
    clientName=""
    daemonURL=""
    connection=None
    hub=None
    session=requests.Session()   
    responseTimeout=1
    messageHandler=None
    messageHanlers={}
    AllNodeStructureList=None
    IsConnected=False
    AutoReconnect=False
    reconnectionInterval=2
    re_con_time=0
    reconnectionTimeout=60
    nodeSubscriptions=[]
    attributeSubscriptions=[]

    #set session parameters 
    session.params={ 'clientID':clientName}  
    def handle_error(self,error):
        print('following error has occured: ', error)
    def handle_stop(self):
        print('stpped:')
    def __init__(self,clientid,oneiroi_daemonURL,autoReconnect,reConnectInterval,reconnectTimeout):  
        self.clientName=clientid
        self.daemonURL=oneiroi_daemonURL+'signalr'
        self.AutoReconnect=autoReconnect
        self.reconnectionInterval=reConnectInterval
        self.reconnectionTimeout=reconnectTimeout
        #create a connection
        self.connection = Connection(self.daemonURL,self.session)
        self.connection.error += self.handle_error
        self.connection.stopping += self.handle_stop
        #register hub proxy and methods
        self.hub = self.connection.register_hub('OneiroiBecosHub')
        self.hub.error += self.handle_error
   
    def connect_to_Daemon(self):                   
            def ServerResponse(arg1=None, arg2=None):
                if arg2:
                    handler=self.get_Message_Handler(arg1)
                    if handler:
                        handler.OnNodeResponse(arg1,arg2)                
            def UpdateAttributeValue(NodeName,AttributeName,SourceClient,AttributeValue):
                 handler=self.get_Message_Handler(NodeName)
                 if handler:
                     handler.OnAttributeValueReceived(SourceClient,NodeName,AttributeName,AttributeValue)
            def OnMessageDeliveryAck(acknowledgement):
                print("parse OBJ")
            def OnMessageReceived(MessageID,NodeName,Message):
                 handler=self.get_Message_Handler(NodeName)
                 if handler:
                     handler.OnMessageReceived(MessageID,NodeName,Message['xmlData'])  
            def AllNodeStructureReceived(NodeStructrueList):
                 self.AllNodeStructureList=NodeStructrueList
            #initiate connection request
            self.hub.client.on('Response',ServerResponse)   
            self.hub.client.on('updateAttributevalue',UpdateAttributeValue) 
            self.hub.client.on('messageDeliveryAck',OnMessageDeliveryAck)   
            self.hub.client.on('UpDateClient',OnMessageReceived)
            self.hub.client.on('onAllNodeStructure',AllNodeStructureReceived)
            try:
                self.connection.start()
                if self.connection.started:
                    self.hub.server.invoke('getAllnodesWithStructure')        
                    self.connection.wait(2)
                    self.IsConnected=True
                    self.informConnectionStatusChange(OneiroiConnectionState.Connected)
                    if self.nodeSubscriptions:
                        for nodeName in self.nodeSubscriptions:
                            self.Subscribe_To_Node_Messages(nodeName)
                        self.nodeSubscriptions.clear()
                    if self.attributeSubscriptions:
                        for subItem in self.attributeSubscriptions:
                            arrs=subItem.split('|')
                            self.Set_Node_Attribute_Notification(arrs[0],arrs[1])
                        self.attributeSubscriptions.clear() 
                    threadStatusCheck=Thread(target=self.checkConnectionStatus,args=())
                    threadStatusCheck.start()
            except:
                print ("could not reach the server")
                self.informConnectionStatusChange(OneiroiConnectionState.disconnected)
                if self.AutoReconnect:
                    if self.re_con_time<self.reconnectionTimeout:
                        time.sleep(self.reconnectionInterval)
                        self.re_con_time=self.re_con_time+self.reconnectionInterval
                        self.connect_to_Daemon()
                    else:
                        self.informConnectionStatusChange(OneiroiConnectionState.connectionTimeOut)
    def informConnectionStatusChange(self,newState):
        for nodekey in self.messageHanlers:
            messageHanlers[nodekey].OnConnectionStateChanged(newState)
    def connect_To_Node(self,NodeName,MessageHandler):
        if self.IsConnected:
            try:
                self.messageHanlers[NodeName]=MessageHandler
                self.hub.server.invoke('CreateNode', NodeName)
                self.connection.wait(self.responseTimeout)
                return True;
            except:
                self.messageHanlers[NodeName]=MessageHandler
                print("an Error has occured")
                return False;
        else:
            self.messageHanlers[NodeName]=MessageHandler
            return False
    def Subscribe_To_Node_Messages(self,NodeName):
        if NodeName not in self.nodeSubscriptions:
                self.nodeSubscriptions.append(NodeName)       
        if self.IsConnected:
            self.hub.server.invoke('subScribe',self.clientName,  NodeName)
            self.connection.wait(self.responseTimeout) 
    def unsubscribe_From_Node_Message(self,NodeName):
        if self.IsConnected:
            self.hub.server.invoke('UNsubScribe',self.clientName,NodeName)
            self.connection.wait(self.responseTimeout)
    def Set_Attribute_Value(self,NodeName,AttributeName,AttributeValue):
        if self.IsConnected:
            self.hub.server.invoke('setAttributeValue',NodeName,AttributeName ,AttributeValue,self.clientName)
            self.connection.wait(self.responseTimeout)
    def get_Attribute_value(self,NodeName,AttributeName):
        if self.IsConnected:
            self.hub.server.invoke('getAttributeValue',NodeName,AttributeName ,self.clientName)
            self.connection.wait(self.responseTimeout)
    def get_Attribute_value_ofClient(self,NodeName,AttributeName,ClientID):
        if self.IsConnected:
            self.hub.server.invoke('getAttributeValue',NodeName,AttributeName ,ClientID)
            self.connection.wait(self.responseTimeout)
    def Set_Node_Attribute_Notification(self,NodeName,AttributeName,):
        node_attr=NodeName+'|'+AttributeName
        if node_attr not in self.attributeSubscriptions:
                self.attributeSubscriptions.append(node_attr)  
        if self.IsConnected:
            self.hub.server.invoke('setNotificationForAttribute',self.clientName,NodeName,AttributeName)
            self.connection.wait(self.responseTimeout)
    def Send_Message(self,xmlMessage):
        if self.IsConnected:
            print( str(uuid.uuid4()))
            self.hub.server.invoke('handleOneiroiMessage', str(uuid.uuid4()) ,xmlMessage)
            self.connection.wait(self.responseTimeout)   
    def Send_Message_Object(self,messageObj):
        if self.IsConnected:
            print( str(uuid.uuid4()))
            self.hub.server.invoke('handleMessage', str(uuid.uuid4()) ,messageObj)
            self.connection.wait(self.responseTimeout)  
    def keep_listening(self,duration_in_Seconds=3600):       
        self.hub.server.invoke('inform', self.clientName)        
        self.connection.wait(duration_in_Seconds)
    def get_Message_Handler(self,NodeName):
        if len(self.messageHanlers)>0:
            return self.messageHanlers[NodeName]
        else:
            return None
    def get_Node_Structure(self,NodeName):
        currentNodeDefinition=None
        if self.AllNodeStructureList:
            for node in self.AllNodeStructureList:
                if node['NodeName']==NodeName:
                    currentNodeDefinition=node
                    break
        return currentNodeDefinition
    def checkConnectionStatus(self):
        while True:
            if not self.hub.server._HubServer__connection._Connection__greenlet.started:
                self.connection.started=False
                self.informConnectionStatusChange(OneiroiConnectionState.disconnected)
                self.connect_to_Daemon()
                break
    

class oneiroiReceiver(ABC):
    @abstractmethod
    def OnResponse(self,message):
        pass
    @abstractmethod
    def OnNodeResponse(self,NodeName,message):
        pass
    @abstractmethod
    def OnMessageReceived(self,messageID,NodeName,Message):
        pass
    @abstractmethod
    def OnAttributeValueReceived(self,Client,NodeName,AttributeName,AttributeValue):
        pass
class OneiroiConnectionState(Enum):
    disconnected = 0
    Connecting = 1
    Connected = 2
    Reconnecting = 3
    connectionTimeOut=4
    