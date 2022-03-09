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
			self._artists[0], 
			self._album_title,
			self._title,
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

	def __init__(self, login, password):

		print("Получение апи спотифай")
		self.library = syncmm.spotify(login, password)
		print("Апи получен")
	
	def download(self):
		
		print("Получение всех альбомов")
		
		# Получим все альбомы пользователя
		albums = self.library.albums()
		print(f"Получено альбомов: {len(albums)}")

		os.chdir("data")

		for album in albums:

			# Создаем папку исполнителя

			try:
				os.mkdir(album['artists'][0])
			except:
				pass
			
			# Переходим в папку исполнителя
			os.chdir(album['artists'][0])

			# Создаем папку альбома
			try:
				os.mkdir(album['album'])
			except:
				pass

			# Переходим в папку альбома
			os.chdir(album['album'])

			print(f"Скачивание альбома - {album['album']}")

			for track in album['tracks']:
				download = DownloadSong(
					url = track['uri'],
					title = track['title'],
					artists = track['artists'],
					track_num = track['track_num'],
					album_title = album['album']
				)

				print(f"    Скачивание трека - {track['title']}")

				download.start(
					session = self.library._session, 
					cover_url = album['cover_url']
				)

			os.chdir("..")
			os.chdir("..")