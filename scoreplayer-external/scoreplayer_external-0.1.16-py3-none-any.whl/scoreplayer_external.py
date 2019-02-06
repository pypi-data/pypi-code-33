#!/usr/bin/env python
"""

Python external for controlling the Decibel ScorePlayer canvas mode, v0.1.16
Copyright (c) 2018 Aaron Wyatt

This module provides a python wrapper for sending OSC canvas commands to the
Decibel ScorePlayer.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange
from pythonosc import osc_message_builder, udp_client, dispatcher, osc_server
import time
import socket
import threading
from datetime import datetime

#The scoreObject class is used to provide a python representation of objects
#drawn onto the ScorePlayer canvas.
class scoreObject:
    __addressPrefix = '/Renderer/Command/'
    
    def __init__(self, name, external, objtype='canvas'):
        self.name = name
        self.objtype = objtype
        self.external = external
        self.removed = False

        #Create the dictionary of commands which are valid for the each different object type.
        self.__validCommands = {}

        common = ['setColour']
        nonline = ['addLayer', 'addScroller', 'addText', 'addGlyph', 'addStave', 'addLine']
        noncanvas = ['remove', 'setOpacity', 'fade']
        nonlinecanvas = ['setPosition', 'move']
        
        self.__validCommands['canvas'] = ['clear']
        self.__validCommands['layer'] = ['loadImage', 'clearImage', 'setSize']
        self.__validCommands['scroller'] = ['loadImage', 'clearImage', 'setSize', 'setScrollerWidth', 'setScrollerPosition', 'setScrollerSpeed', 'start', 'stop']
        self.__validCommands['text'] = ['setText', 'setFont', 'setFontSize']
        self.__validCommands['glyph'] = ['setGlyph', 'setGlyphSize']
        self.__validCommands['stave'] = ['setSize', 'setLineWidth', 'setClef', 'removeClef', 'addNotehead', 'addNote', 'removeNote', 'clear']
        self.__validCommands['line'] = ['setWidth', 'setStartPoint', 'setEndPoint']
        
        for key in self.__validCommands:
            self.__validCommands[key].extend(common)
            if key != 'line':
                self.__validCommands[key].extend(nonline)
            if key != 'canvas':
                self.__validCommands[key].extend(noncanvas)
            if key != 'line' and key != 'canvas':
                self.__validCommands[key].extend(nonlinecanvas)

    #These methods each send a single command to the score object that they represent.            
    def addLayer(self, objname, part, x, y, width, height):
        self.sendCommand('addLayer', objname, part, int(x), int(y), int(width), int(height))
        return scoreObject(objname, self.external, 'layer')

    def addScroller(self, objname, part, x, y, width, height, scrollerWidth, speed):
        self.sendCommand('addScroller', objname, part, int(x), int(y), int(width), int(height), int(scrollerWidth), float(speed))
        return scoreObject(objname, self.external, 'scroller')

    def addText(self, objname, part, x, y, fontSize=36):
        self.sendCommand('addText', objname, part, int(x), int(y), float(fontSize))
        return scoreObject(objname, self.external, 'text')

    def addGlyph(self, objname, part, x, y, glyphSize=36):
        self.sendCommand('addGlyph', objname, part, int(x), int(y), float(glyphSize))
        return scoreObject(objname, self.external, 'glyph')

    def addStave(self, objname, part, x, y, width, height, lineWidth):
        self.sendCommand('addStave', objname, part, int(x), int(y), int(width), int(height), int(lineWidth))
        return scoreObject(objname, self.external, 'stave')

    def addLine(self, objname, part, x1, y1, x2, y2, lineWidth):
        self.sendCommand('addLine', objname, part, int(x1), int(y1), int(x2), int(y2), int(lineWidth))
        return scoreObject(objname, self.external, 'line')

    def remove(self):
        self.sendCommand('remove')
        self.removed = True

    def clear(self):
        self.sendCommand('clear')

    def loadImage(self, imgname, autosizing=0):
        self.sendCommand('loadImage', imgname, autosizing)

    def clearImage(self):
        self.sendCommand('clearImage')

    def setPosition(self, x, y):
        self.sendCommand('setPosition', int(x), int(y))

    def setSize(self, width, height):
        self.sendCommand('setSize', int(width), int(height))

    def setColour(self, r, g, b, a=255):
        self.sendCommand('setColour', int(r), int(g), int(b), int(a))

    def setOpacity(self, opacity):
        self.sendCommand('setOpacity', float(opacity))

    def move(self, x, y, duration):
        self.sendCommand('move', int(x), int(y), float(duration))

    def fade(self, opacity, duration):
        self.sendCommand('fade', float(opacity), float(duration))

    def setScrollerWidth(self, scrollerWidth):
        self.sendCommand('setScrollerWidth', int(scrollerWidth))

    def setScrollerPosition(self, scrollerPosition):
        self.sendCommand('setScrollerPosition', int(scrollerPosition))

    def setScrollerSpeed(self, scrollerSpeed):
        self.sendCommand('setScrollerSpeed', float(scrollerSpeed))

    def setText(self, text):
        self.sendCommand('setText', text)

    def setFont(self, font):
        self.sendCommand('setFont', font)

    def setFontSize(self, fontSize):
        self.sendCommand('setFontSize', float(fontSize))

    def setGlyph(self, glyphType):
        self.sendCommand('setGlyph', glyphType)

    def setGlyphSize(self, glyphSize):
        self.sendCommand('setGlyphSize', float(glyphSize))

    def setLineWidth(self, lineWidth):
        self.sendCommand('setLineWidth', int(lineWidth))

    def setClef(self, clef, position):
        self.sendCommand('setClef', clef, int(position))

    def removeClef(self, position):
        self.sendCommand('removeClef', int(position))

    def addNotehead(self, note,  position, filled=1):
        self.sendCommand('addNotehead', note, int(position), int(filled))

    def addNote(self, note, position, duration):
        self.sendCommand('addNote', note, int(position), int(duration))

    def removeNote(self, note, position):
        self.sendCommand('removeNote', note, int(position))

    def setWidth(self, width):
        self.sendCommand('setWidth', int(width))

    def setStartPoint(self, x, y):
        self.sendCommand('setStartPoint', int(x), int(y))

    def setEndPoint(self, x, y):
        self.sendCommand('setEndPoint', int(x), int(y))

    def start(self):
        self.sendCommand('start')

    def stop(self):
        self.sendCommand('stop')

    #The method used to actually send the OSC command via our external object.
    #It checks whether the command is valid for the given object, and makes sure the object
    #hasn't already been removed.
    def sendCommand(self, command, *args):
        if self.removed:
            print ('{} has been removed'.format(self.name))
            return
        if command in self.__validCommands[self.objtype]:
            self.external.sendMessage(scoreObject.__addressPrefix + self.name + '/' + command, *args)
        else:
            print('Command not valid for this type of object ({}.{})'.format(self.name, command))

class scorePlayerExternal:
    #The protocol version expected. Current version is 14.
    protocolVersion = 14
    
    def __init__(self):
        self.__services = {}
        self.listeningPort = 8000
        self.__service = None
        self.__connectionHandler = None
        self.__errorHandler = None
        self.playHandler = None
        self.resetHandler = None
        self.tickHandler = None
        self.printTicks = False
        self.printMessages = False
        self.printTimestamp = True
        
        #Set up our message routing and start listening on our port.
        self.__dispatcher = dispatcher.Dispatcher()
        self.__dispatcher.map('/Server/RegistrationOK', self.__onConnect)
        self.__dispatcher.map('/Server/BadProtocolVersion', self.__onError)
        self.__dispatcher.map('/External/NewServer', self.__onReconnect)
        self.__dispatcher.map('/Control/Play', self.__onPlay)
        self.__dispatcher.map('/Control/Reset', self.__onReset)
        self.__dispatcher.map('/Tick', self.__onTick)
        self.__dispatcher.map('/External/*', self.__extMessage)
        self.__dispatcher.map('/Server/Request*', self.__loadMessage)

        #If our port is unavailable, increase the port number by 1 and try again.
        while True:
            try:
                self.__server = osc_server.ThreadingOSCUDPServer(('0.0.0.0', self.listeningPort), self.__dispatcher)
                break
            except:
                self.listeningPort += 1
            
        self.__server_thread = threading.Thread(target=self.__server.serve_forever)
        self.__server_thread.start()
        print('Listening on port {}'.format(self.listeningPort))

    def selectServer(self):
        #Set up our service browser
        zeroconf = Zeroconf()
        browser = ServiceBrowser(zeroconf, '_decibel._udp.local.', handlers=[self.__serviceChange])
        time.sleep(1)
    
        while True:
            i = 1
            print('Choose an iPad to connect to')
            servers = []
            #List each service we've discovered
            for service in self.__services.values():
                serverName = service.server
                scoreName = service.name
                if serverName.endswith('.local.'):
                    serverName = serverName[:-7]
                scoreName = scoreName[:(scoreName.find(service.type)) - 1]
                scoreName = scoreName[:(scoreName.rfind('.'))]
                print('{}: {} ({})'.format(i, serverName, scoreName))
                #Save the service info to an array
                servers.append(service)
                i += 1
            print('Or\n{}: Refresh List'.format(i))
            while True:
                selection = int(input('Enter Selection: '))

                if selection == i:
                    print()
                    break
                elif selection >= i or selection < 0:
                    print('Invalid selection')
                else:
                    zeroconf.close()
                    self.__service = servers[selection - 1]
                    return

    def connect(self, connectionHandler, errorHandler=None):
        if self.__service is None:
            print('No server selected')
            return
        
        #Connect to our server
        address = socket.inet_ntoa(self.__service.address)
        return self.connectToAddress(address, self.__service.port, connectionHandler, errorHandler)

    #Connect to a specified address and port. This can be used if the required service cannot
    #be found using zeroconf.
    def connectToAddress(self, address, port, connectionHandler=None, errorHandler=None):
        self.__connectionHandler = connectionHandler
        self.__errorHandler = errorHandler
        
        self.__client = udp_client.SimpleUDPClient(address, port)
        self.__client.send_message('/Server/RegisterExternal', ['Decibel Networking Protocol v' + str(scorePlayerExternal.protocolVersion), self.listeningPort])        

        if self.__connectionHandler is not None:
            return scoreObject('canvas', self)
    
    def sendMessage(self, message, *args):
        self.__client.send_message(message, args)

    def __serviceChange(self, zeroconf, service_type, name, state_change):
        if state_change is ServiceStateChange.Added:
            self.__services[name] = zeroconf.get_service_info(service_type, name)
        elif state_change is ServiceStateChange.Removed:
            del self.__services[name]

    def __onConnect(self, oscAddress):
        if self.printMessages:
            self.__printMessage(oscAddress)
        if self.__connectionHandler is not None:
            handler = self.__connectionHandler
            self.__connectionHandler = None
            time.sleep(0.1)
            handler()

    def __onError(self, oscAddress, errorMessage):
        if self.printMessages:
            self.__printMessage(oscAddress, errorMessage)
        self.__server.shutdown()
        if self.__errorHandler is not None:
            self.__errorHandler()

    def __onPlay(self, oscAddress):
        if self.printMessages:
            self.__printMessage(oscAddress)
        if self.playHandler is not None:
            self.playHandler()

    def __onReset(self, oscAddress):
        if self.printMessages:
            self.__printMessage(oscAddress)
        if self.resetHandler is not None:
            self.resetHandler()

    def __onTick(self, oscAddress, location):
        if self.printTicks:
            self.__printMessage(oscAddress, location)
        if self.tickHandler is not None:
            self.tickHandler(location)

    def __extMessage(self, oscAddress, *oscArgs):
        if self.printMessages:
            self.__printMessage(oscAddress, *oscArgs)

    def __loadMessage(self, oscAddress):
        if self.printMessages:
            self.__printMessage(oscAddress)

    def __printMessage(self, oscAddress, *oscArgs):
        argsString = ''
        for arg in oscArgs:
            if isinstance(arg, str):
                argsString += '"{}", '.format(arg)
            else:
                argsString += '{}, '.format(arg)
        if len(argsString) > 1:
            argsString = argsString[:-2]
        if self.printTimestamp:
            outString = '{}: {} {}'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), oscAddress, argsString)
        else:
            outString = '{} {}'.format(oscAddress, argsString)
        #Explicitly print our newline so it isn't separated from the message when multiple
        #messages arrive at the same time.
        outString = outString.rstrip() + '\n'
        print(outString, end="")

    #Connect our external to a new device if the old server has left the network.
    def __onReconnect(self, oscAddress, address, port):
        self.connectToAddress(address, port)

    def shutdown(self):
        self.__server.shutdown()

    #Commands to easily send basic control signals to the iPad
    def play(self):
        self.sendMessage('/Control/Play')

    def reset(self):
        self.sendMessage('/Control/Reset')

    def loadScore(self, name, composer, scoreType, scoreVersion='0'):
        self.sendMessage('/Server/LoadRequest', name, composer, scoreType, scoreVersion)
