# -*- coding: utf-8 -*-
from __future__ import unicode_literals # standard
import json, sys, os # standard
import requests # da scaricare
from telethon import TelegramClient, events, sync # da scaricare
from serietvapi_bot.__init__ import __version__

def main():
	# update to latest version
	rj = requests.get("https://tvditaly.altervista.org/api/r/1/api_versions?av=" + __version__ + "&tv=API&s=stable").json()
	if (rj['ok'] == True):
		os.system('pip install -U serietvapi_bot')

	# controlliamo se il file per le credenziali esiste
	if not os.path.exists("SerieTvItaly_bot.json"):
		print("Ti verranno richiesti alcuni dati che non verranno condivisi con il bot e sviluppatori.\nLe credenziali richieste servono per eseguire le API del bot @SerieTvItaly_bot con il profilo da te indicato.\n\nSe vuoi modificare l'account in uso puoi modificare il file JSON chiamato SerieTvItaly_bot.json oppure eliminarlo ed avviare questo file per crearne uno nuovo con nuove informazioni.\n\nDove trovo le credenziali? Andando sul sito my.telegram.org")
		try:
			api_id = int(input("Telegram Client > Inserisci la tua api_id (valore numerico): "))
		except Exception as e:
			print("\nLa api_id è un valoe numerico\n")
			api_id = int(input("Telegram Client > Inserisci la tua api_id (valore numerico): "))

		api_hash = input("Telegram Client > Inserisci la tua api_hash: ")
		json.dump({'api_id': api_id, 'api_hash': api_hash, 'bot_a_id': None, 'bot_a_pw': None}, open("SerieTvItaly_bot.json", 'w'))

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
			import download_episode
			ep_t = []
			epi_error = False
			while True:
				Episode_Downloader = download_episode.Downloader(config_file['bot_a_id'], config_file['bot_a_pw'])
				Episode_Downloader.start()
				ep_t.append(Episode_Downloader)
				for t in ep_t:
					t.join()
				if epi_error == True:
					break

		else:
			print("Non ho riconosciuto questa funzione come valida, assicurati di avere l'ultima versione di questo script.")

if __name__ == "__main__":
	main()