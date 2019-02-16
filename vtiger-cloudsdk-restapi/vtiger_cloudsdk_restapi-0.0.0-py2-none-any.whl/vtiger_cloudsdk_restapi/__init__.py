# The content of this file is subject to ("Vtiger Public License 1.2") refer to LIECENSE for more details.
# Copyright (c) Vtiger.
# All Rights Reserved.

from requests import Request, Session
import json
import urllib

class Client:

	def __init__(self, domain, username, password):
		self.__endpoint = None
		self.__username = None
		self.__password = None
		self.__cache = {}

		self.__set_endpoint(domain)
		self.__set_credentials(username, password)

	def __set_endpoint(self, url):
		try:
			url.index("://")
		except ValueError:
			url = "https://" + url

		rest_path = False
		try:
			url.index("restapi")
			rest_path = True
		except ValueError:
			pass

		try:
			url.index("modules")
			rest_path = True
		except ValueError:
			pass

		if rest_path == False:
			url = url + "/restapi/v1/vtiger/default"

		self.__endpoint = url

	def __set_credentials(self, username, password):
		self.__username = username
		self.__password = password

	def __from_cache(self, key):
		if self.__cache.has_key(key):
			return self.__cache.get(key)
		else:
			return None

	def __to_cache(self, key, value):
		self.__cache[key] = value

	def __operation(self, method, name, parameters = None):
		url = self.__endpoint + name
		if parameters is not None:
			if method == "GET":
				pairs = []
				for k in parameters:
					v = parameters[k]
					if isinstance(v, basestring) is False:
						v = json.dumps(v)
					pairs.append(k + "=" + urllib.quote(v))
				url = url + "?" + ("&".join(pairs))
				parameters = None
			else:
				for k in parameters:
					v = parameters[k]
					if isinstance(v, basestring) is False:
						parameters[k] = json.dumps(v)

		ssn = Session()
		req = Request(method, url, auth=(self.__username, self.__password), data=parameters)
		r = ssn.send(ssn.prepare_request(req))

		if r.status_code != 200:
			raise BaseException(r.reason)

		response = r.text
		try:
			response = json.loads(response)
		except ValueError:
			print (r.request.data)
			raise BaseException(response)

		if response["success"] == False:
			raise BaseException(response["error"]["message"])

		return response["result"]

	def api(self, method, name, parameters = None):
		return self.__operation(method.upper(), name, parameters)

	def myid(self):
		_me = self.me()	
		return _me["id"]

	def me(self):
		_me = self.__from_cache("api.me")
		if _me is None:
			_me = self.__operation("GET", "/me")
			self.__to_cache("api.me", _me)
		return _me

	def list_types(self, types = None):
		if isinstance(types, basestring):
			types = [types]
		return self.__operation("GET", "/listtypes", {"fieldTypeList": types})

	def describe(self, type):
		return self.__operation("GET", "/describe", {"elementType": type})

	def create(self, type, record):
		return self.__operation("POST", "/create", {
			"elementType": type,
			"element": record
		})

	def retrieve(self, id):
		return self.__operation("GET", "/retrieve", {
			"id": id
		})

	def query(self, query):
		return self.__operation("GET", "/query", {
			"query": query
		})

	def update(self, record):
		return self.__operation("POST", "/update", {
			"element": record
		})

	def revise(self, record):
		return self.__operation("POST", "/revise", {
			"element": record
		})

	def delete(self, id):
		return self.__operation("POST", "/delete", {
			"id": id
		})

	def image(self, id):
		return self.__operation("GET", "/files_retrieve", {
			"id": id
		})

	def related_types(self, type):
		return self.__operation("GET", "/relatedtypes", {
			"elementType": type
		})

	def add_related(self, id, related_id, related_label):
		return self.__operation("POST", "/add_related", {
			"sourceRecordId": id,
			"relatedRecordId": related_id,
			"relationIdLabel": related_label
		})
	
	def retrieve_related(self, id, related_label, related_type):
		return self.__operation("GET", "/retrieve_related", {
			"id": id,
			"relatedLabel": related_label,
			"relatedType" : related_type
		})

	def query_related(self, id, related_label, query):
		return self.__operation("GET", "/query_related", {
			"id"   : id,
			"relatedLabel": related_label,
			"query": query
		})

	def delete_related(self, id, related_id):
		return self.__operation("POST", "/delete_related", {
			"sourceRecordId": id,
			"relatedRecordId": related_id
		})

	def tags_add(self, id, tags):
		if isinstance(tags, basestring):
			tags = [tags]
		return self.__operation("POST", "/tags_add", {
			"id": id,
			"tags": tags
		})

	def tags_retrieve(self, id):
		result = self.__operation("POST", "/tags_retrieve", {
			"id": id
		})
		return result["tags"]
	
	def tags_delete(self, id, tags, delete_all = False):
		if delete_all is False:
			delete_all = 0
		else:
			delete_all = 1

		return self.__operation("POST", "/tags_delete", {
			"id": id,
			"tags": tags,
			"delete_all": delete_all
		})

	def sync(self, modified_time, module_type, sync_type):
		return self.__operation("GET", "/sync", {
			"modifiedTime": modified_time,
			"elementType" : module_type,
			"syncType"    : sync_type
		})

	def convert_lead(self, id, create_potential = [], create_contact = [], create_account = []):
		if create_potential is False or create_potential is None:
			create_potential["create"] = False
		else:
			create_potential["create"] = True

		if create_account is False or create_account is None:
			create_account["create"] = False
		else:
			create_account["create"] = True


		if create_contact is False or create_contact is None:
			create_contact["create"] = False
		else:
			create_contact["create"] = True

		create_account["name"]   = "Accounts"
		create_contact["name"]   = "Contacts"
		create_potential["name"] = "Potentials"

		return self.__operation("POST", "/convertlead", {
			"element": {
				"leadId": id,
				"entities": {
					"Contacts": create_contact,
					"Accounts": create_account,
					"Potentials": create_potential
				}
			}
		})

	def reopen(self, id):
		return self.__operation("POST", "/reopen", {"id": id})

	def account_hierarchy(self, id):
		return self.__operation("GET", "/get_account_hierarchy", {"id": id})