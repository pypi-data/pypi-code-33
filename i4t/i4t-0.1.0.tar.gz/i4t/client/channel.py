## @file channel.py
# @brief I4T Channel
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

from i4t.client.topic import Topic

import paho.mqtt.client as mqtt

class Channel(object):

  def register_topics(channel):
    pass

  def on_invite(channel):
    pass

  def on_join(channel):
    pass

  def on_members(channel, members):
    pass

  ##############################################################################
  # public
  ##############################################################################

  def __init__(self, applet, channel_name):
    self._topics = {}
    self._topics_registered = {}
    self._members = {}
    self.applet = applet
    self.channel_name = channel_name
    self.register_topics()

  def user(self, var, val=None):
    return self.applet.user(var, val)

  def topic(self, topic_name, topic_cls=None):
    # register a topic
    if topic_cls is not None:
      self._topics.pop(topic_name, None)
      # TODO properly close the topic
      self._topics_registered[topic_name] = topic_cls
    # get the topic instance
    else:
      if topic_name in self._topics:
        return self._topics[topic_name]
      elif topic_name in self._topics_registered:
        topic_cls = self._topics_registered[topic_name]
        self._topics[topic_name] = topic_cls(self, topic_name)
        return self._topics[topic_name]
      else:
        #raise I4TException("Topic: {} has not been registered. Pass topic_cls=Topic".format(topic_name))
        topic_cls = Topic
        self._topics[topic_name] = topic_cls(self, topic_name)
        return self._topics[topic_name]

  def join(self):
    self._join_pending = True
    serial = self.applet.client.iwarrant.token.serial
    # RX updates to session
    self.rx('%s/{}'.format(serial), self._rx_session)
    # TODO send from application instance
    self.tx('%s/{}'.format(serial), serial)
    # RX P2P communications
    self.rx('%p/{}'.format(serial), self._rx_p2p)
    # TX request access to channel
    self.tx('%r', serial)
    return self

  def invite(self, member):
    self.applet.invite(member, self.channel_name)

  def rx(self, topic, callback):
    # rx to a topic
    topic = "{}/{}".format(self.channel_name, topic)
    self.applet.rx(topic, callback)
    return self

  def tx(self, topic, data):
    # tx data to a topic
    topic = "{}/{}".format(self.channel_name, topic)
    self.applet.tx(topic, data)
    return self

  @property
  def applet(self):
    return self._applet

  @applet.setter
  def applet(self, applet):
    self._applet = applet

  @property
  def members(self):
    for member in self._members:
      yield member

  ##############################################################################
  # private
  ##############################################################################

  def _on_invite(self):
    # user callback
    self.on_invite()

  def _rx_session(self, data):
    # data is a session token
    # TODO self.stoken = data
    # recieve content encryption key
    # TODO
    # decrypt content encryption key
    # TODO
    if self._join_pending:
      self._join_pending = False
      # user callback
      self.on_join()
    # update membership table
    # TODO self._members[data] = data
    self.on_members(self.members)

  def _rx_p2p(self, data):
    channel_name = data
    self.applet.channel(channel_name)._on_invite()
