from client import RRSpotify
import os

if __name__ == "__main__":

    try:
        os.mkdir("data")
    except:
        pass

    login = input("Enter Spotfiy login: ")
    password = input("Enter Spotify password: ")
    core = RRSpotify(login, password)

    print('Запуск скрипта')
    core.download()