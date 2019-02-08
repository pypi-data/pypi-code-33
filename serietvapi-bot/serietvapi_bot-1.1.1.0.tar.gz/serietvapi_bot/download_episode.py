# -*- coding: utf-8 -*-
from __future__ import unicode_literals # standard
from random import randint # standard
import youtube_dl, requests # da scaricare
import os, json, os.path, threading, string, random

class Downloader(threading.Thread):
	def __init__(self, api_id, api_pw):
		self.a_id = api_id
		self.a_pw = api_pw
		self.files = []
		threading.Thread.__init__(self)

	def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
		return ''.join(random.choice(chars) for _ in range(size))

	def run(self):
		headers = {'User-Agent': 'init/1.0'}
		NewUDA = self.id_generator()
		Update_UA = requests.get("https://tvditaly.altervista.org/api/w/1/private_update_value?a_id=" + self.a_id + "&a_pw=" + self.a_pw + "&tb=api_bot_profiles&campo=UA&record=" + NewUDA + "&k=api_id&kv=" + self.a_id, headers=headers).json()

		if Update_UA["ok"] == False:
			print(Update_UA["info"])
		else:
			headers = {'User-Agent': NewUDA}

			JSON_infos = requests.get("https://tvditaly.altervista.org/api/r/1/download_episode?a_id=" + self.a_id + "&a_pw=" + self.a_pw, headers=headers).json()

			if (JSON_infos["ok"] == False):
				if "reeason" in JSON_infos:
					print(JSON_infos["info"] + "\n\t" + JSON_infos["reeason"])
				else:
					print(JSON_infos["info"])
				global epi_error
				epi_error = True
			else:
				SerieInfo_array = JSON_infos["info"]["episodi"]["info_episodio"]

				counter = 0
				file_names = []
				threads = []
				for single_SerieInfo in SerieInfo_array:
					Name_File = single_SerieInfo["openload_file_name"]
					rj = requests.get("https://tvditaly.altervista.org/api/r/1/tg_message?a_id=" + str(self.a_id) + "&a_pw=" + str(self.a_pw) + "&msg=<b>📥 Download file in corso</b>\n\nIl file chiamato " + Name_File + " è in fase di download.")
					exec("%s = self.Openload_Down(\"%s\", \"%s\", %d, %d, \"%s\", \"%s\")" % ("YDL_OPEN_" + str(counter), single_SerieInfo["link_diretto"], Name_File, 0, single_SerieInfo["id_episodio"], self.a_id, self.a_pw))
					exec("%s.start()" % ("YDL_OPEN_" + str(counter)))
					exec("threads.append(%s)" % ("YDL_OPEN_" + str(counter)))
					print("Avvio download del file chiamato: " + Name_File)
					self.files.append(Name_File)
					counter += 1

				for t in threads: # aspettiam che finisce il download dei file
					t.join()

	class Openload_Down(threading.Thread):
		"""docstring for Openload_Down"""
		def __init__(self, link_downl, Name_File, ChatID, id_episodio, id, pw):
			threading.Thread.__init__(self)
			self.single_link = link_downl
			self.from_id = ChatID
			self.fname = Name_File
			self.id_ep = id_episodio
			self.i = id
			self.p = pw

		def run(self):
			ydl_opts = {
				'format': '0',
				'quiet': True,
				'no_warnings': True,
				'nocheckcertificate': True,
				'outtmpl': self.fname,
			}

			try:
				with youtube_dl.YoutubeDL(ydl_opts) as ydl:
					ydl.download([self.single_link])
				rj = requests.get("https://tvditaly.altervista.org/api/r/1/tg_message?a_id=" + str(self.i) + "&a_pw=" + str(self.p) + "&msg=<b>👍 Download file completato</b>\n\nIl file chiamato " + self.fname + " è stato scaricato sul tuo PC.")

			except Exception as e:
				print("C'è stato un errore: " + str(e))
				global epi_error
				epi_error = True