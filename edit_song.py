import eyed3
from eyed3.id3.frames import ImageFrame

class MetaData:
    
    def __init__(self, path_to_song: str):
        # if not os.access(path_to_song, os.R_OK):
        #     raise AssernationError("No song found!")
        self.__song_path = path_to_song
    
    def change(self, title: str, artist: str, album: str, track_num: int, release_date: str):
        audiofile = eyed3.load(self.__song_path)
        audiofile.tag.artist = artist
        audiofile.tag.album = album
        audiofile.tag.title = title
        audiofile.tag.track_num = track_num
        audiofile.tag.release_date = release_date
        audiofile.tag.save()

    def set_album_cover(self, path_to_cover: str):
        audiofile = eyed3.load(self.__song_path)
        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open(path_to_cover,'rb').read(), 'image/png')
        audiofile.tag.save()