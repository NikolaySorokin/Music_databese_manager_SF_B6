from bottle import route
from bottle import run
from bottle import request
from bottle import HTTPError
import album

@route("/albums/<artist>")
def get_albums(artist):
    """
    Выводит количество альбомомв исполнителя artist и пронумерованный список альбомов
    """
    list_albums = album.find(artist)
    if not list_albums:
        message = "Альбомов исполнителя {} не найдено".format(artist)
        result = HTTPError(404, message)
    else:
        # Находим кол-во альбомов
        albums_amount = len(list_albums)
        result = ("Количество альбомов {}: {}<br>".format(artist, albums_amount))
        # Добавляем к результату пронумерованный список альбомов
        albums_names = [album.album for album in list_albums]
        for i in range(1, albums_amount+1):
            result += "{} - {}<br>".format(i, albums_names[i-1])
    return result

@route("/albums", method="POST")
def new_album():
    """
    Получает данные нового альбома из запроса и сохраняет в базу данных
    """
    album_data = {
        "year": request.forms.get("year"),
        "artist": request.forms.get("artist"),
        "genre": request.forms.get("genre"),
        "album": request.forms.get("album")
    }
    http_code, message = album.save_album(album_data)
    if http_code == 200:
        result = message
    else:
        result = HTTPError(http_code, message)

    return result


if __name__ == "__main__":
    run(host="localhost", port=8080, debug=True)
