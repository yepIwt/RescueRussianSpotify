"""
	#RescueRussianSpotify
	This script download a song by URI
	Example: python download_by_uri.py <uri>
"""

# Spotify
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality

import os, sys

from pydub import AudioSegment

import secrets
LOGIN = secrets.LOGIN
PASSWORD = secrets.PASSWORD

def from_song_link_to_uri(song_link):
	start = song_link.find("track/")
	if start == -1:
		return song_link
	return "spotify:track:{}".format(song_link[start+6:]) # 6 это смещение по тегу

if __name__ == "__main__":
	args = sys.argv[1:]
	song_link = ""
	if args:
		song_link = args[0]

	if not LOGIN or not PASSWORD:
		print("Edit this script and add credentials (lOGIN, PASSWORD)")
	elif not song_link:
		print("Use 'python download_by_uri.py <link-to-song>'")
	else:
		session = Session.Builder().user_pass(LOGIN, PASSWORD).create()
		track_id = TrackId.from_uri(
			from_song_link_to_uri(song_link)
		)
		
		# Подключаемся к потоку
		stream = session.content_feeder().load(track_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None)
		
		# Подгружаем метаданные
		artist = stream.track.artist[-1].name
		title = stream.track.name
		album = stream.track.album.name

		file_title = f"{artist} [{album}] - {title}"

		# Начинаем считывать поток
		data = bytes('',encoding='utf-8')
		size = stream.input_stream.stream().size()
		for _ in range(size):
			data += stream.input_stream.stream().read()
		
		with open("cache", 'wb') as f:
			f.write(data)
		
		# Ковертируем
		song = AudioSegment.from_file("cache",'ogg')
		song.export(f"{file_title}.mp3", 'mp3')
		os.remove('cache')

		# Записываем считанный поток в файл
		with open(f"{file_title}.mp3", 'wb') as f:
			f.write(data)

		print("Done!")