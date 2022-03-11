from client import RRSpotify
from getpass import getpass
import os

if __name__ == "__main__":

    try:
        os.mkdir("data")
    except:
        pass

    login = input("Enter Spotfiy login: ")
    password = getpass("Enter Spotify password: ")
    core = RRSpotify(login, password)

    from_album = input("Введите ссылку на альбом с которого начнется скачивание (если сначала, то просто нажмите Enter): ")
    core.start_from = from_album

    print('Запуск скрипта')
    core.download()