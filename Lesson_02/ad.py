import redis
import hashlib
from os import urandom
from flask import Flask
from flask import request
from flask import Response
from time import strftime


def redis_session_key(day, session_id):
    """Создаёт ключ для хранения в redis, используя дату и ключ сессии.
    :return: ключ-строка
    """
    return 'page:index:counter:' + str(day) + ':' + str(session_id)


def check_session_id(day, session_id):
    """Проверяет зарегистрирована ли сессия с таким id.
    :return: True/False
    """
    if r.get(redis_session_key(day, session_id)):
        return True
    return False


def create_session_id():
    """Генерирует сессионный ключ. Его стоит проверить на уникальность
    перед выдачей ключа пользователю.
    :return: строка
    """
    hash = hashlib.sha512(str(urandom(128)).encode('utf-8'))
    session_id = str(hash.hexdigest())
    return session_id


app = Flask(__name__)
r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/')
def theanswer():
    day = strftime("%Y-%m-%d")
    resp = Response()

    session_id = request.cookies.get('session_id')
    if not session_id:  # если это новый пользователь, то ему надо выдать новый id
        session_id = create_session_id()

        while check_session_id(day, session_id):  # id сессии должен быть уникальным
            session_id = create_session_id()  # если получилось неуникальное, то пересоздаём

        r.incr(redis_session_key(day, session_id))
        resp.set_cookie('session_id', session_id, max_age=None)

    resp.set_data('42 - ' + str(r.get(redis_session_key(day, session_id))))
    return resp