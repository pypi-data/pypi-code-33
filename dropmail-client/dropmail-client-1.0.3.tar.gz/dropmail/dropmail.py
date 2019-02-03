#!/usr/bin/env python3

# Copyright (C) 2019 Jonston Chan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import websocket
import json

class Dropmail:
	def __init__(self, server='wss://dropmail.me/websocket'):
		self.emails = dict()
		self.default_email = None
		self._supported_domains = None

		self.socket = websocket.create_connection(server)
		self._on_open_connection()

	def __del__(self):
		self.socket.close()

	@property
	def supported_domains(self):
		return self._supported_domains

	@supported_domains.setter
	def supported_domains(self, supported_domains):
		# Message contains a 'D' character followed by
		# a comma-separated list of supported domains
		# 'D' for 'domain'
		self._supported_domains = supported_domains[1:].split(',')

	def next_message(self):
		# Message contains an 'I' character followed by
		# a json-encoded message
		raw_message = self.socket.recv()[1:]
		message = json.loads(raw_message)
		return message

	def get_key(self, email):
		key = self.emails[email]
		return '{}:{}'.format(email, key)

	def _associate_email(self, account_info):
		# Message contains an 'A' character followed by
		# the email, a colon and then the restore key
		# 'A' for 'address'
		email, key = account_info[1:].split(':')
		self.emails[email] = key

		return email

	def new_email(self, domain=None):
		if domain in self.supported_domains:
			packet = 'A{}'.format(domain)
		elif not domain:
			packet = 'M'
		else:
			raise ValueError('Requested address from domain "{}", but not in list of supported domains\n({})'.format(domain, self.supported_domains))

		self.socket.send(packet)

		account_info = self.socket.recv()
		email = self._associate_email(account_info)

		return email

	def restore_email(self, key):
		packet = 'R{}'.format(key)
		self.socket.send(packet)

		response = self.socket.recv()

		# 'W002Bad restore key' occurs when account could not be restored
		if response[0] == 'W':
			warning_code = response[1:4]
			warning_message = response[4:]
			raise ValueError('{} ({})'.format(warning_message, warning_code))

		email = self._associate_email(response)

		return email

	def _on_open_connection(self):
		account_info = self.socket.recv()
		email = self._associate_email(account_info)

		self.default_email = email
		self.supported_domains = self.socket.recv()