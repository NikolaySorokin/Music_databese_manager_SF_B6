import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime

DB_PATH = "sqlite:///albums.sqlite3"
Base = declarative_base()

class Album(Base):
    __tablename__ = "album"
    id = sa.Column(sa.INTEGER, primary_key=True, autoincrement=True)
    year = sa.Column(sa.INTEGER)
    artist = sa.Column(sa.TEXT)
    genre = sa.Column(sa.TEXT)
    album = sa.Column(sa.TEXT)

def connect_db():
    engine = sa.create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def find(artist):
    """
    Находит альбомы в базе данных по артисту
    """
    session = connect_db()
    albums = session.query(Album).filter(Album.artist == artist).all()
    return albums

def get_album(album_data):
    """
    Возвращает объект Album из данных полученных в запросе
    """
    new_album = Album(
        year=album_data["year"],
        artist=album_data["artist"],
        genre=album_data["genre"],
        album=album_data["album"]
    )
    return new_album

def save_album(album_data):
    """
    Сохраняет новый альбом в базу данных.
    Возвращает код ошибки 409 и сообщение,
    если не прошел проверку валидности или такой альбом уже есть в базе.
    Если всё ОК, возвращает код 200 и сообщение.
    """
    session = connect_db()
    new_album = get_album(album_data)
    # Проверяем валидность данных из запроса, получаем сообщение от валидатора.
    validator_message = validator(new_album)
    if validator_message:
        return 409, validator_message
    # Проверяем наличие артиста из запроса в базе данных
    # и наличие у данного артиста альбома полученного из запроса
    elif session.query(Album).filter(Album.artist == new_album.artist).first() and\
            session.query(Album).filter(Album.album == new_album.album).first():
        session.close()
        return 409, "Альбом `{}` уже есть в базе данных".format(new_album.album)
    else:
        session.add(new_album)
        session.commit()
        return 200, "Альбом `{}` сохранен в базу данных.".format(new_album.album)

def validator(album):
    """
    Проверка валидности данных из запроса.
    Данные о годе выпуска альбома (year), артисте (artist) и названии альбома (album) должны быть.
    Возвращает список сообщений о некорректно введенных данных,
    если все ОК возвращает пустой список.
    """
    result = []

    if not album.artist or not album.album:
        result.append("Отсутствуют данные (артист или название альбома)")
    if not valid_year(album.year):
        result.append("Некорректный год выпуска альбома")

    return ("<br>").join(result)

def valid_year(year):
    """
    Проверка валидности введенного года выпуска альбома
    """
    if year:
        try:
            y = int(year)
            if y > datetime.datetime.now().year or y < 0:
                return False
            else:
                return True
        except ValueError:
            return False

