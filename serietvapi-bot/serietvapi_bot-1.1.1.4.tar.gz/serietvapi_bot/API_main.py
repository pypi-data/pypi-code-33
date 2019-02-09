# -*- coding: utf-8 -*-
from __future__ import unicode_literals # standard
import json, sys, os, time, threading # standard
import requests # da scaricare
from telethon import TelegramClient, events, sync # da scaricare
from serietvapi_bot.__init__ import __version__

class Uploader(threading.Thread):
	def __init__(self, api_id, api_pw, c):
		threading.Thread.__init__(self)
		self.a_id = api_id
		self.a_pw = api_pw
		self.client = c

	def run(self):
		while True:
			global files
			if len(files) > 0:
				for file in files:
					print("Carico il file chamato " + file)
					rj = requests.get("https://tvditaly.altervista.org/api/r/1/tg_message?a_id=" + str(self.a_id) + "&a_pw=" + str(self.a_pw) + "&msg=<b>📤 Caricamento file in corso</b>\n\nIl file chiamato " + file + " è in fase di invio al Bot.")
					self.client.send_file("@SerieTvItaly_bot", file, caption=os.path.splitext(file)[0], force_document=True)
					files.remove(file)
					time.sleep(60)

files = []

def main():
	# update to latest version
	rj = requests.get("https://tvditaly.altervista.org/api/r/1/api_versions?av=" + __version__ + "&tv=API&s=stable").json()
	if (rj['ok'] == True):
		os.system('pip install -U serietvapi_bot')

	# controlliamo se il file per le credenziali esiste
	if not os.path.exists("SerieTvItaly_bot.json"):
		json.dump({'api_id': 603638, 'api_hash': 'e0c8fdcd4516ef60e80c6bf89708d628', 'bot_a_id': None, 'bot_a_pw': None}, open("SerieTvItaly_bot.json", 'w'))

	with open("SerieTvItaly_bot.json") as f:
		config_file = json.load(f)

	client = TelegramClient('SerieTvItaly_bot_session', config_file['api_id'], config_file['api_hash'])

	with client:
		print("Ora che il client è configurato correttamente devi autenticarti con il Bot @SerieTvItaly_bot, se il tuo account è ancora valido non devi inseire nuovamente le credenziali in caso contrario dovrai inseire nuovamente le credenziali.")
		
		bot_api_id = config_file['bot_a_id']
		bot_api_pw = config_file['bot_a_pw']

		if (bot_api_id == None or bot_api_pw == None):
			print("Le credenziali non sono valide, aggiornale ora")
			bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")
			bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

		while (bot_api_pw == "" or bot_api_id == ""):
			print("Devi inserire entrambe le credenziali perché tutte obbligatorie.")
			bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")
			bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

		rj_status = requests.get("https://tvditaly.altervista.org/api/r/1/account_status?a_id=" + str(bot_api_id) + "&a_pw=" + str(bot_api_pw)).json()

		if (rj_status['ok'] == True):
			print("L'account è valido, inserirò le credenziali API del Bot SerieTvItaly_bot per le prossime volte.\nDovrai nuovamente inserirle quando l'account scadrà.")
		else:
			print("L'account non è valido devi inserire nuovamente le credenziali API del Bot SerieTvItaly_bot")
			bot_api_pw = ""
			bot_api_id = ""
			json.dump({'api_id': config_file['api_id'], 'api_hash': config_file['api_hash'], 'bot_a_id': None, 'bot_a_pw': None}, open("SerieTvItaly_bot.json", 'w'))
			while (bot_api_pw == "" or bot_api_id == ""):
				print("Devi inserire entrambe le credenziali perché tutte obbligatorie.")
				bot_api_id = input("@SerieTvItaly_bot > Immetti la tua api_id: ")
				bot_api_pw = input("@SerieTvItaly_bot > Immetti la tua api_pw: ")

			json.dump({'api_id': config_file['api_id'], 'api_hash': config_file['api_hash'], 'bot_a_id': bot_api_id, 'bot_a_pw': bot_api_pw}, open("SerieTvItaly_bot.json", 'w'))
		
		with open("SerieTvItaly_bot.json") as f:
			config_file = json.load(f)

		if "download_episode" in rj_status["purpose"]:
			from serietvapi_bot import download_episode
			ep_t = []
			epi_error = False
			Upload_file = Uploader(config_file['bot_a_id'], config_file['bot_a_pw'], client)
			Upload_file.start()
			while True:
				Episode_Downloader = download_episode.Downloader(config_file['bot_a_id'], config_file['bot_a_pw'])
				Episode_Downloader.start()
				ep_t.append(Episode_Downloader)
				for t in ep_t:
					t.join()

				for file in Episode_Downloader.files:
					global files
					files.append(file)

				if epi_error == True:
					break

		else:
			print("Non ho riconosciuto questa funzione come valida, assicurati di avere l'ultima versione di questo script.")

if __name__ == "__main__":
	main()