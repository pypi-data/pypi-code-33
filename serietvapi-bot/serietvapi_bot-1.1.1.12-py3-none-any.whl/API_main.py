# -*- coding: utf-8 -*-
from __future__ import unicode_literals # standard
import json, sys, os, time, threading, asyncio # standard
import requests # da scaricare
from telethon import TelegramClient, events, sync # da scaricare
from serietvapi_bot.__init__ import __version__

class Client(TelegramClient):
	def __init__(self, tg_api_id, tg_api_hash, bot):
		super().__init__('SerieTvItaly_bot_session', tg_api_id, tg_api_hash)
		self.tg_id = tg_api_id
		self.tg_hash = tg_api_hash
		self.bot_api = bot

	def invia_file(self, nome_file, destinatario = "@SerieTvItaly_bot", caption = ""):
		self.send_file(destinatario, nome_file, caption=caption, force_document=True)

class Bot_API(Client):
	def __init__(self, id, pw):
		self.id = id
		self.pw = pw

	def execute_command(self, version, name_function, type_action, params={}, headers={}):
		def_paras = {'a_id':self.id, 'a_pw':self.pw}
		if (len(params) != 0):
			for key in params:
				def_paras[key] = params[key]
		response = requests.get("https://tvditaly.altervista.org/api/" + type_action + "/" + str(version) + "/" + name_function, params=def_paras, headers=headers)
		json_response = response.json()
		return json_response
		

files = []

def main():
	# update to latest version
	rj = requests.get("https://tvditaly.altervista.org/api/r/1/api_versions?av=" + __version__ + "&tv=API&s=stable").json()
	if (rj['ok'] == True):
		os.system('sudo pip install -U serietvapi_bot')

	# controlliamo se il file per le credenziali esiste
	if not os.path.exists("SerieTvItaly_bot.json"):
		json.dump({'api_id': 603638, 'api_hash': 'e0c8fdcd4516ef60e80c6bf89708d628', 'bot_a_id': None, 'bot_a_pw': None}, open("SerieTvItaly_bot.json", 'w'))

	with open("SerieTvItaly_bot.json") as f:
		config_file = json.load(f)
	
	bot_api_id = config_file['bot_a_id']
	bot_api_pw = config_file['bot_a_pw']

	if (bot_api_id == None or bot_api_pw == None):
		print("Le credenziali non sono valide, aggiornale ora")
		bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")
		bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

	while bot_api_id == "":
		print("Devi inserire un ID valido")
		bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")

	while bot_api_pw == "":
		print("Devi inserire una PW valida")
		bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

	rj_status = requests.get("https://tvditaly.altervista.org/api/r/1/account_status?a_id=" + str(bot_api_id) + "&a_pw=" + str(bot_api_pw)).json()

	if (rj_status['ok'] == True):
		print("L'account è valido, inserirò le credenziali API del Bot SerieTvItaly_bot per le prossime volte.\nDovrai nuovamente inserirle quando l'account scadrà.")
	else:
		print("L'account non è valido devi inserire nuovamente le credenziali API del Bot SerieTvItaly_bot")
		bot_api_pw = ""
		bot_api_id = ""
		json.dump({'api_id': config_file['api_id'], 'api_hash': config_file['api_hash'], 'bot_a_id': None, 'bot_a_pw': None}, open("SerieTvItaly_bot.json", 'w'))
		while bot_api_id == "":
			print("Devi inserire un ID valido")
			bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")

		while bot_api_pw == "":
			print("Devi inserire una PW valida")
			bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

		rj_status = requests.get("https://tvditaly.altervista.org/api/r/1/account_status?a_id=" + str(bot_api_id) + "&a_pw=" + str(bot_api_pw)).json()
	json.dump({'api_id': 603638, 'api_hash': 'e0c8fdcd4516ef60e80c6bf89708d628', 'bot_a_id': bot_api_id, 'bot_a_pw': bot_api_pw}, open("SerieTvItaly_bot.json", 'w'))
	
	with open("SerieTvItaly_bot.json") as f:
		config_file = json.load(f)
	
	bot = Bot_API(config_file['bot_a_id'], config_file['bot_a_pw'])
	client = Client(config_file['api_id'], config_file['api_hash'], bot)
	print("Ora è tutto pronto per funzionare in modo corretto")
	with client:
		if "download_episode" in rj_status["purpose"]:
			client.send_message("@SerieTvItaly_bot", "api " + bot.id + " benvenuto")
			from serietvapi_bot import download_episode
			ep_t = []
			while True:
				Episode_Downloader = download_episode.Downloader(bot)
				Episode_Downloader.start()
				ep_t.append(Episode_Downloader)
				for t in ep_t:
					t.join()

				for file in Episode_Downloader.files:
					print("Carico il file chiamato " + file)
					rj = bot.execute_command(1, "tg_message", "r", {'msg':'<b>📤 Caricamento file in corso</b>\n\nIl file chiamato ' + file + ' è in fase di invio al Bot.'}, Episode_Downloader.download_ua)
					client.invia_file(file, caption=os.path.splitext(file)[0])
					os.remove(file)

				if Episode_Downloader.flag_error == True:
					print("Rilevato un errore durante la fase di download di un epiodio, vedere descrizione fornita dal bot")
					break

		else:
			print("Non ho riconosciuto questa funzione come valida, assicurati di avere l'ultima versione di questo script.")

if __name__ == "__main__":
	main()