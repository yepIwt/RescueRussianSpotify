from tempfile import SpooledTemporaryFile
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.proto.Metadata_pb2 import Album

from pydub import AudioSegment
import os, sys
import syncmm
import time

from edit_song import MetaData
#from lastfm import AlbumCover

import requests

LOGIN = ""
PASSWORD = ""
LAST_FM_API_KEY = ""

class Downloader:

    def __init__(self, login: str = None, password: str = None, session: Session = None):
        if session:
            self.__session = session
        else:
            self.__session = Session.Builder().user_pass(login, password).create()
        #self.__session = Session.Builder().user_pass(LOGIN, PASSWORD).create()
    
    def _link_parse(self, link: str):
        link_type = None
        if "track" in link:
            link_type = "track"
        elif "album" in link:
            link_type = "album"
        elif "episode" in link:
            link_type = "episode"
 
        start = link.find(link_type + "/")
        if start == -1:
            return None
        end = link.find("?si")
        return "spotify:{}:{}".format(link_type, link[start+6:end]) # 6 это смещение по тегу

    def __download_from_stream(self, stream) -> bytes:
        b = bytes('', encoding='utf-8')
        size = stream.input_stream.stream().size()
        for _ in range(size):
            b += stream.input_stream.stream().read()
        return b
    
    def __decompile_cache_to_mp3(self, title: str):
        song = AudioSegment.from_file("cached_song","ogg")
        song.export(title + ".mp3","mp3")
        os.remove("cached_song")
    
    def __get_song_metadata(self, track) -> tuple:
        artist = track.artist[-1].name
        title = track.name
        album = track.album.name
        track_num = track.number

        release_date__year = str(track.album.date.year)
        release_date__month = track.album.date.month
        release_date__day = track.album.date.day
        if len(str(release_date__month)) == 1:
            release_date__month = "0" + str(release_date__month)
        
        if len(str(release_date__day)) == 1:
            release_date__day = "0" + str(release_date__day)
        
        release_date = "{}-{}-{}".format(
            release_date__year,
            release_date__month,
            release_date__day
        )
        return artist, album, title, track_num, release_date
    
    def __download_album_cover(self, url: str):
        r = requests.get(url)
        with open("cover.png", "wb") as f:
            f.write(r.content)
    
    def __set_song_metadata(self, artist: str, album: str, title: str, track_num: int, release_date: str, path_to_cover: str):
        m = MetaData(title + ".mp3")
        m.change(artist, album, title, track_num, release_date)
        m.set_album_cover(path_to_cover)

    def download_track(self, uri_link: str, folder_to_save: str, url_to_cover: str):
        """
            link must be "spotify:track:0Y9D1Bc4fAkeZnVsGKdij6"
        """

        track_id = TrackId.from_uri(uri_link)
        try:
            stream = self.__session.content_feeder().load(track_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None)
        except:
            print("Трек недоступен", link)
            return

        with open("cached_song","wb") as f:
            f.write(self.__download_from_stream(stream))

        artist, album, title, track_num, release_date = self.__get_song_metadata(stream.track)
        self.__decompile_cache_to_mp3(title)
        self.__download_album_cover(url_to_cover)

        self.__set_song_metadata(artist, album, title, track_num, release_date, "cover.png")
        os.replace(title + ".mp3", os.path.join(folder_to_save, title + ".mp3"))


class Main:

    __parser_spotify = None
    __downloader = None

    def __init__(self, login: str, password: str): # TODO: token auth
        self.__parser_spotify = syncmm.spotify(login, password)
        self.__downloader = Downloader(session=self.__parser_spotify._session)

    def download_by_link(self, link: str, path_to_folder: str):
        uri = self.__downloader._link_parse(link)
        print(uri)
        song = self.__parser_spotify._get_a_track_by_uri(uri)
        print(f"Downloading song: {song['artists']} - {song['album']} - {song['title']}")
        self.__downloader.download_track(song['uri'], path_to_folder, song['cover_url'])
        print(f"Downloaded!")

    def download_all_liked_tracks(self, path_to_folder: str):
        liked = self.__parser_spotify.liked()
        if not os.access(path_to_folder, os.R_OK):
            os.mkdir(path_to_folder)
        
        for i,song in enumerate(liked):
            self.__downloader.download_song(song['uri'], path_to_folder, song['cover_url'])
            print(f"Downloaded {i+1}) {song['artists'][0]} - {song['title']}")

if __name__ == "__main__":
    m = Main(LOGIN, PASSWORD)
    m.download_by_link(sys.argv[1], sys.argv[2])