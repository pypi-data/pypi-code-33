import aiohttp
import asyncio
import sys

base_url = 'https://timchen.tk/api'

class Timchen:
	def __init__(self, url, desc, id, async=True):
		self.url = url
		self.description = desc
		self.id = id
		self.async = async

	def __str__(self):
		return f'Image: {self.url}\nDescription: {self.description}'
	def __repr__(self):
		if self.async:
			return f'await timchen.get_from_id({self.id})'
		else:
			return f'timchen.get_from_id_async({self.id})'
	def __int__(self):
		return self.id
	def __dict__(self):
		return {'url':self.url,'desc':self.desc,'id':self.id}


async def _get(path):
	async with aiohttp.ClientSession() as s:
		r = await s.get(base_url+path)
		return await r.json()

async def get_random():
	r = await _get('/random')
	return Timchen(r['url'], r['desc'], r['id'])

async def get_from_id(id):
	r = await _get(f'/get/{id}')
	return Timchen(r['url'], r['desc'], r['id'])

async def get_all(id):
	r = await _get(f'/get/{id}')
	timchens = []
	for t in r:
		timchens.append(Timchen(r['url'], r['desc'], r['id']))
	return tuple(timchens)



def _get_sync(path):
	if 'requests' not in sys.modules:
		import requests
	r = requests.get(base_url+path)
	return r.json()

def get_random_sync():
	r = _get_sync('/random')
	return Timchen(r['url'], r['desc'], r['id'], False)

def get_from_id_sync(id):
	r = _get_sync(f'/get/{id}')
	return Timchen(r['url'], r['desc'], r['id'], False)

def get_all_sync(id):
	r = _get_sync(f'/get/{id}')
	return Timchen(r['url'], r['desc'], r['id'], False)