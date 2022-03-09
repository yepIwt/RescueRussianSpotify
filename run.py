from client import RRSpotify

if __name__ == "__main__":
    login = input("Enter Spotfiy login: ")
    password = input("Enter Spotify password: ")
    core = RRSpotify(login, password)

    print('Запуск скрипта')
    core.download()