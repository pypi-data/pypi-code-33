## @file applet.py
# @brief I4T Applet
#
# @copyright
# Copyright 2018 I4T <https://i4t.io>
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

import logging, os
log = logging.getLogger().getChild(__name__)

from i4t import I4TException

from i4t.client.channel import Channel

import paho.mqtt.client as mqtt

class Applet(object):

  def register_channels(applet):
    pass

  def on_connect(applet):
    pass

  def on_disconnect(applet):
    pass

  ##############################################################################
  # public
  ##############################################################################

  def __init__(self, client, ptoken):
    self._channels = {}
    self._channels_registered = {}
    self.client = client
    self.ptoken = ptoken
    self._root_channel = self.AppletRootChannel(self, '%')
    self.register_channels()

  def user(self, var, val=None):
    return self.client.user(var, val)

  def channel(self, channel_name, channel_cls=None):
    # register a channel
    if channel_cls is not None:
      self._channels.pop(channel_name, None)
      # TODO properly close the channel
      self._channels_registered[channel_name] = channel_cls
      return None
    # get the channel instance
    else:
      if channel_name in self._channels:
        return self._channels[channel_name]
      elif channel_name in self._channels_registered:
        channel_cls = self._channels_registered[channel_name]
        self._channels[channel_name] = channel_cls(self, channel_name)
        return self._channels[channel_name]
      else:
        raise I4TException("Channel: {} has not been registered. Pass channel_cls=Channel".format(channel_name))

  def connect(self):
    # connect
    host = self._ptoken.connection.host
    port = self._ptoken.connection.port
    channel = self._ptoken.connection.channel
    self.mqtt_client.connect(host, port=port, keepalive=60)
    self.applet_root = channel
    # start thread
    self.mqtt_client.loop_start()
    return self

  def disconnect(self):
    # disconnect
    self.mqtt_client.disconnect()
    self.mqtt_client.loop_stop()
    return self

  def invite(self, member, channel_name):
    self._root_channel.tx('%p/{}'.format(member), channel_name)

  def rx(self, topic, callback):
    # rx to a topic
    mqtt_topic = "{}/{}".format(self.applet_root, topic)
    def mqtt_cb(mqtt_cb_client, mqtt_cb_userdata, mqtt_cb_message):
      callback(mqtt_cb_message.payload)
    self.mqtt_client.message_callback_add(mqtt_topic, mqtt_cb)
    self.mqtt_client.subscribe(mqtt_topic)
    log.debug("Subscribed to {}".format(mqtt_topic))
    return self

  def tx(self, topic, data):
    # tx data to a topic
    mqtt_topic = "{}/{}".format(self.applet_root, topic)
    self.mqtt_client.publish(mqtt_topic, data)
    log.debug("Published to {} with data {}".format(mqtt_topic, data))
    return self

  @property
  def client(self):
    return self._client

  @client.setter
  def client(self, client):
    self._client = client

  @property
  def ptoken(self):
    return self._ptoken

  @ptoken.setter
  def ptoken(self, ptoken):
    self._ptoken = ptoken
    self._init_connection()

  ##############################################################################
  # private
  ##############################################################################

  def _init_connection(self):
    # configure MQTT client
    serial = self.client.iwarrant.token.serial
    self.mqtt_client = mqtt.Client(client_id=serial, clean_session=True)
    # TODO: switch to token authentication
    username = "nickdev"
    password = "1k89h3lmgVzRicXk"
    self.mqtt_client.username_pw_set(username, password=password)
    # setup callbacks
    self.mqtt_client.on_connect = self._on_connect
    self.mqtt_client.on_disconnect = self._on_disconnect
    return self

  def _on_connect(self, mqtt_client, userdata, flags, rc):
    log.debug("Connection returned result: {}".format(rc))
    # join the root channel
    self._root_channel.join()
    # user callback
    self.on_connect()
    return self

  def _on_disconnect(self, mqtt_client, userdata, rc):
    log.debug("Disconnection returned result: {}".format(rc))
    # user callback
    self.on_disconnect()
    return self

  def _rx_clients_serial(self, data):
    # TODO parse data for channel name and session token
    self.channel(data)._on_invite(data)
    return self

  class AppletRootChannel(Channel):
    pass
