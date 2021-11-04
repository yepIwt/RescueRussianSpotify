import requests

API_URL = "https://ws.audioscrobbler.com/2.0/"
OPENNING_SEARCH_PARAMETR = b'<image size="">'
CLOSING_SEARCH_PARAMETR = b'</image>'

class AlbumCover:

    def __init__(self, api_key: str) -> None:
        self._API_KEY = api_key
    
    def __get_cover_link(self, content: bytes) -> bytes:

        start = content.find(
            OPENNING_SEARCH_PARAMETR,
        )

        end = content.find(
            CLOSING_SEARCH_PARAMETR,
            start
        )

        return content[start+15:end] # 15 это смещение относительно начала поиска по тегу
    
    def get_album_cover(self, artist_name: str, album_name: str) -> bytes:

        payload = {
            'api_key': API_KEY,
            'method': 'album.getinfo',
            'artist': artist_name,
            'album': album_name
        }
        
        r = requests.get(API_URL, params=payload)

        if r.status_code != 200:
            return b""
        
        cover_link = self.__get_cover_link(r.content)

        r = requests.get(cover_link)
        
        if r.status_code != 200:
            return b""

        return r.content
        

if __name__ == "__main__":
    API_KEY = ""
    a = AlbumCover(api_key = API_KEY)
    result = a.get_album_cover("The White Stripes", "Elephant")
    print(result)