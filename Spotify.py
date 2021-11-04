from tempfile import SpooledTemporaryFile
from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality
from librespot.proto.Metadata_pb2 import Album

from pydub import AudioSegment
import os

from edit_song import MetaData
from lastfm import AlbumCover

LOGIN = ""
PASSWORD = ""
LAST_FM_API_KEY = ""

class Downloader:

    def __init__(self, login: str, password: str, last_fm_api_key: str):
        self.__session = Session.Builder().user_pass(LOGIN, PASSWORD).create()
        self.__LAST_FM_API_KEY = last_fm_api_key
    
    def __link_parse(self, link: str):
        start = link.find("track/")
        if start == -1:
            return None
        end = link.find("?si")
        return "spotify:track:{}".format(link[start+6:end]) # 6 это смещение по тегу

    def __download_from_stream(self, stream) -> bytes:
        b = bytes('',encoding='utf-8')
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
    
    def __download_album_cover(self, artist: str, album: str):
        a = AlbumCover(self.__LAST_FM_API_KEY)
        cover_in_bytes = a.get_album_cover(artist, album)
        with open("cover.png", "wb") as f:
            f.write(cover_in_bytes)
    
    def __set_song_metadata(self, artist: str, album: str, title: str, track_num: int, release_date: str, path_to_cover: str):
        m = MetaData(title + ".mp3")
        m.change(artist, album, title, track_num, release_date)
        m.set_album_cover(path_to_cover)

    def download_song(self, link: str):
        """
            link must be "spotify:track:0Y9D1Bc4fAkeZnVsGKdij6"
            or "https://open.spotify.com/track/2URDbWGmPz3vhagl25p8OC?si=15ee14d7e038406f"
        """
        if link.startswith("https://"):
            link = self.__link_parse(link)

        track_id = TrackId.from_uri(link)
        stream = self.__session.content_feeder().load(track_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None)
        with open("cached_song","wb") as f:
            f.write(self.__download_from_stream(stream))

        artist, album, title, track_num, release_date = self.__get_song_metadata(stream.track)
        self.__decompile_cache_to_mp3(title)
        self.__download_album_cover(artist, album)

        self.__set_song_metadata(artist, album, title, track_num, release_date, "cover.png")

if __name__ == "__main__":
    d = Downloader(LOGIN, PASSWORD, LAST_FM_API_KEY)
    d.download_song("https://open.spotify.com/track/2URDbWGmPz3vhagl25p8OC?si=6a4c3c70c074475e")