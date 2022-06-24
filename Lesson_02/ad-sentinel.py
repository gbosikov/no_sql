from redis.sentinel import Sentinel
from ad import *


app = Flask(__name__)
sentinel = Sentinel([('localhost', 16379)], socket_timeout=0.1)
r = sentinel.master_for('THEAD_CLUSTER', socket_timeout=0.1)


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