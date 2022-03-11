"""
	#RescueRussianSpotify
	This script download all Spotify music library
"""

import requests
import syncmm
import os

from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality

from pydub import AudioSegment

from edit_song import MetaData

bad_sym = [
	"?",
	"\\",
	"/",
	":",
	"*",
	'"',
	"<",
	">",
	"|"
]

class DownloadSong:

	_title = None
	_artists = None
	_track_num = None
	_url = None
	_album_title = None

	def __init__(self, title, artists, track_num, album_title, url):
		self._title = title
		self._artists = artists
		self._track_num = track_num
		self._url = url
		self._album_title = album_title
	
	def from_url_to_uri(self, song_link):
		start = song_link.find("track/")
		if start == -1:
			return song_link
		return "spotify:track:{}".format(song_link[start+6:]) # 6 это смещение по тегу
	
	def __download_stream(self, stream):
		data = bytes('',encoding='utf-8')
		size = stream.input_stream.stream().size()
		for _ in range(size):
			data += stream.input_stream.stream().read()

		return data
	
	def __get_release_date_from_stream(self, stream):
		release_date__year = str(stream.track.album.date.year)
		release_date__month = stream.track.album.date.month
		release_date__day = stream.track.album.date.day
		if len(str(release_date__month)) == 1:
			release_date__month = "0" + str(release_date__month)
		
		if len(str(release_date__day)) == 1:
			release_date__day = "0" + str(release_date__day)
		
		release_date = "{}-{}-{}".format(
			release_date__year,
			release_date__month,
			release_date__day
		)
		return release_date
	
	def set_metadata(self, release_date):
		m = MetaData(self._title + ".mp3")
		m.change(
			self._title,
			self._artists, 			
			self._album_title,			
			self._track_num,
			release_date
		)
		m.set_album_cover("cover.jpg")

	def start(self, session, cover_url):
		track_id = TrackId.from_uri(
			self.from_url_to_uri(self._url)
		)
		
		try:
			stream = session.content_feeder().load(track_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None)
		except:
			print(f"Трек недоступен - {self._title} / {self._artists}")
		else:
			cache = self.__download_stream(stream)

			if not os.path.isfile("cover.jpg"):
				r = requests.get(cover_url)
				with open("cover.jpg", 'wb') as f:
					f.write(r.content)

			with open("cache",'wb') as f:
				f.write(cache)
			
			song = AudioSegment.from_file("cache", 'ogg')
			song.export(f"{self._title}.mp3", 'mp3')
			os.remove("cache")
			
			release_date = self.__get_release_date_from_stream(stream)

			self.set_metadata(release_date)


class RRSpotify:

	start_from = None

	def __init__(self, login, password):

		print("Получение апи спотифай")
		self.library = syncmm.spotify(login, password)
		print("Апи получен")
	
	def download(self):
		
		print("Получение всех альбомов")

		
		albums = self.library.albums()

		if self.start_from:
			it = iter(albums)
			get = next(it, None)
			while get['uri'].split(":")[-1] not in self.start_from:
				get = next(it, None)

			albums = list(it)

		print(f"Получено альбомов: {len(albums)}")

		os.chdir("data")

		for album in albums:

			good_album = album['album']
			for s in bad_sym:
				good_album = good_album.replace(s, " ")
			
			good_group = album['artists'][0]
			for s in bad_sym:
				good_group = good_group.replace(s, " ")

			# Создаем папку исполнителя
			try:
				os.mkdir(good_group)
			except:
				pass
			
			# Переходим в папку исполнителя
			os.chdir(good_group)

			# Создаем папку альбома
			try:
				os.mkdir(good_album)
			except:
				pass

			# Переходим в папку альбома
			os.chdir(good_album)

			print(f"Скачивание альбома - {album['album']}")

			for track in album['tracks']:
				
				# Удаляем запрещенные для папок символы
				good_title = track['title']

				for s in bad_sym:
					good_title = good_title.replace(s, " ")

				download = DownloadSong(
					url = track['uri'],
					title = good_title,
					artists = good_group,
					track_num = track['track_num'],
					album_title = good_album
				)

				print(f"    Скачивание трека - {track['title']}")

				download.start(
					session = self.library._session, 
					cover_url = album['cover_url']
				)

			os.chdir("..")
			os.chdir("..")