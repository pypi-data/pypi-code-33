import asyncio
import datetime
import logging
import random
from ipaddress import ip_address

import pycoap.constants as C
from pycoap.exceptions import (MessageTimeoutError, ProtocolError,
                               ReceiveTimeoutError)
from pycoap.packet.packet import Packet


class Proto(asyncio.DatagramProtocol):
    def __init__(self, onReceiveCallback, onErrorCallback):
        assert callable(onReceiveCallback)
        assert callable(onErrorCallback)

        self.transport = None
        self.onReceiveCallback = onReceiveCallback
        self.onErrorCallback = onErrorCallback

        self.lastMessage = None
        self.logger = logging.getLogger("{}.{}".format(__name__,self.__class__.__name__))

    #Overrides asyncio.DatagramProtocol.connection_made
    def connection_made(self, transport):
        self.transport = transport
        self.logger.debug("Connected")

    #Overrides asyncio.DatagramProtocol.datagram_received
    def datagram_received(self, data, addr):
        #self.logger.debug("Received: {} from:{}".format(data, addr) )
        self.onReceiveCallback(data, addr)

    #Overrides asyncio.DatagramProtocol.error_received
    def error_received(self, exception):
        newException = ProtocolError( "Protocol Error: {}".format(exception) )
        self.logger.debug("Error Received: {}".format(newException) )
        self.onErrorCallback( newException, self.lastMessage )

    #Overrides asyncio.DatagramProtocol.connection_lost
    def connection_lost(self, exc):
        self.logger.debug("Socket closed")
        self.connected = False

    def close(self):
        self.transport.close()

    def send(self,message):
        #self.logger.debug("Send: {}".format(message) )
        self.lastMessage = message # Save the last message so it can be sent back when and errror is received
        self.transport.sendto(message)




class Xmitter(object):
    
    @staticmethod
    async def create(destIP, destPort):
        xmitter = Xmitter(destIP, destPort)
        await xmitter.start()
        return xmitter

    def __init__(self, destIP, destPort):

        assert isinstance(destIP,str), "ip must be a string" 
        ip_address(destIP) #Raises ValueError if not a valid IP
        assert isinstance(destPort, int), "port must be an int"
        assert 0 <= destPort <= 65535, "port out of range"

        self.destIP = destIP
        self.destPort = destPort
        self.proto = None
        self.sock = None
        self.receiveQueue = asyncio.Queue()
        self._received_message_ids = {}


        self.acks = {}

        self.logger = logging.getLogger("{}.{}".format(__name__,self.__class__.__name__))


    async def start(self):
        if self.proto is None:
            loop = asyncio.get_event_loop()
            self.sock, self.proto = await loop.create_datagram_endpoint( 
                                    lambda: Proto(self._onReceive, self._onError),
                                    remote_addr=(self.destIP, self.destPort))

    def stop(self):
        if self.proto is not None:
            self.proto.close()
            self.proto = None
            self.sock = None

    async def send(self,packet):
        """ 
        Sends a packet

        Uses loop to resend packet (if necessary).  Packet is sent then await for ack event.  
        The ack event is set when packets are received in _onReceive() based on the packet
        messageID.   If ack event is not set before ack_timeout, increment retry_count, 
        double ack_timeout and send again.  Continue looping until the ack event is set or
        max retries is reached

        """

        assert isinstance( packet, Packet ), "must be a packet object"
        assert self.proto is not None, "Protocol has not been initialized.  Use the create() coro to instantiate!"

        #Initialize vars to keep track of send progress
        self.acks[packet.messageID] = asyncio.Event()
        retry_count = 0
        ack_timeout = C.ACK_TIMEOUT_MIN * random.uniform(1, C.ACK_MAX_RANDOM_FACTOR)

        while True:
            try:
                self.logger.debug("MessageID: {} Transmitting {} Packet.   Retry Count: {}   Ack Timeout: {}"
                            .format(packet.messageID, repr(packet.messageType), retry_count, ack_timeout))
                #self.logger.debug("Receiving packet {}".format( packet.dumpToStr() ))
                self.proto.send( bytes(packet) )

                #ONLY CON packets need to be resent if not acked
                if packet.messageType != "CON":
                    return retry_count

                await asyncio.wait_for(self.acks[packet.messageID].wait(), ack_timeout )

                self.logger.debug("MessageID: {} Acked.".format( packet.messageID ) )

                return retry_count

            except asyncio.TimeoutError:
                
                #Check for max retries
                if retry_count == C.MAX_RETRANSMITS:
                    raise MessageTimeoutError("Max Retry count reached")        

                ack_timeout *= 2
                retry_count += 1

            


    async def receive(self,timeout=None):
        """
        Receive a result

        Pop a result from the receive queue.  If queue is empty await until is arrives

        If the result in an exception rais it,  otherwise return it 
        """
        try:
            result = await asyncio.wait_for(self.receiveQueue.get(), timeout)
        except asyncio.TimeoutError:
            raise ReceiveTimeoutError("") 

        if isinstance(result,Exception):
            raise result
        else:
            return result


    def _onReceive( self, data, addr ):
        """
        Handel an incoming packet

        Called by self.proto when a packet arrives.  If packet is good it's put into 
        the receive queue
        """
        
        #Make sure the packet came  from the expected source
        sourceIP , sourcePort = addr
        if sourceIP != self.destIP or sourcePort != self.destPort:
            self.logger.debug("Dropping packet from unknown source")
            return

        #Log and drop a packet that can not be parsed
        try:
            packet =  Packet.from_bytes(data)
            #self.logger.debug("Receiving packet {}".format( packet.dumpToStr() ))
        except Exception as error:
            self.logger.warning("Dropping Invalid packet, COAP parse error: " + str(error) )
            return

        #Duplicate message detection
        if self._is_duplicate_message(packet.messageID):
            self.logger.warning("Dropping duplicate message with ID {}".format(packet.messageID) )
            return


        #Special processing based on the Message Type

        if packet.messageType == "CON":
            #send empty ack to source
            self.logger.debug("CON response received, sending ACK to source")
            ackPacket = Packet(messageType = C.MESSAGE_TYPE_ACK, code = C.CODE_EMPTY, 
                                messageID = packet.messageID)
            self.proto.send(bytes(ackPacket))

        elif packet.messageType == "NON":
            pass

        elif packet.messageType == "ACK":
            if packet.messageID in self.acks:
                self.acks[packet.messageID].set()
            
        elif packet.messageType == "RST":
            #set the message ID as acked so resending stops
            if packet.messageID in self.acks:
                self.acks[packet.messageID].set()

            #Put an exception in the receive queue
            self.receiveQueue.put_nowait( ProtocolError("Reset Packet Received") )  
            self.logger.debug("Reset packet received, returning exception" )
            return


        #Special processing for different code groups
        #Not sure if this is the best place for these checks
        #May move later.

        # Pass response packets on to the receive queue. 
        if packet.code.isResponse():
            self.receiveQueue.put_nowait(packet)
    
        # Request packets do not make sense drop them
        elif packet.code.isRequest():
            self.logger.debug("Dropping received request packet")
            return

        # Empty packets generally should not be passed along
        # May be changed in the future with an option to allow pings
        elif packet.code.isEmpty():
            self.logger.debug("Dropping received empty packet")
            return 

    def _onError( self, exception, lastDatagram):
        """ 
        Handel an error

        Called by self.proto for protocol errors, puts the exception in the receive queue
        """

        #Sends ACK to last packet that was sent
        #Note: its possible for lastDatagram to be None if an error was received before sending
        if lastDatagram is not None:
            lastPacket = Packet.from_bytes(lastDatagram)
            if lastPacket.messageID in self.acks:
                    self.acks[lastPacket.messageID].set()

        #Puts the exception in the receive queue
        self.receiveQueue.put_nowait(exception)


    def _is_duplicate_message(self, is_dupe_id):
        """
        Detects duplicate messages
        Stores messages ids in self._received_message_ids.  Returns true if message has 
        already been seen, i.e. is a duplicate

        Also purges old message ids on each run
        """
        #Create a copy of the packet keys array so we can delete when looping over it
        message_ids = []
        message_ids[:] = self._received_message_ids.keys()

        for message_id in message_ids:
            # If the id age is greater exchange lifetime #default is 300 seconds
            age = (datetime.datetime.now() - self._received_message_ids[message_id]).total_seconds() 
            if age > C.MSG_EXCHANGE_LIFETIME:
                del self._received_message_ids[message_id]


        #Check if dupe
        if is_dupe_id in self._received_message_ids:
            return True
        else:
            self._received_message_ids[is_dupe_id] = datetime.datetime.now()
