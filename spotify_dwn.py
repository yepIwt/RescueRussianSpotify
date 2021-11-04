#!/usr/bin/python
import sys

from librespot.core import Session
from librespot.metadata import TrackId
from librespot.audio.decoders import AudioQuality, VorbisOnlyAudioQuality

LOGIN = ""
PASSWORD = ""


def link_parse(link):
    start = link.find("track/")
    if start == -1:
        return None
    end = link.find("?si")
    return "spotify:track:{}".format(link[start+6:end]) # 6 это смещение по тегу

if __name__ == "__main__":

    if not sys.argv[1:]:
        print('Wrong arguments! Use ./spotify_dwn.py [link_to_song]')
    else:
        song_link = link_parse(sys.argv[1])
        if not song_link:
            print("Error link!")
        else:
            session = Session.Builder() \
                .user_pass(LOGIN, PASSWORD) \
                .create()

            track_id = TrackId.from_uri(song_link)
            stream = session.content_feeder().load(track_id, VorbisOnlyAudioQuality(AudioQuality.VERY_HIGH), False, None)

            artist = stream.track.artist[-1].name
            title = stream.track.name
            album = stream.track.album.name

            file_title = f"{artist} [{album}] - {title}"

            b = bytes('',encoding='utf-8')
            size = stream.input_stream.stream().size()
            for _ in range(size):
                b += stream.input_stream.stream().read()

            f = open(f"{file_title}.mp3", 'wb')
            f.write(b)
            f.close()