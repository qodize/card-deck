import datetime as dt
import os
import logging
import flask as fl
import flask_socketio as fl_sock
import config

os.makedirs('/var/log/card', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(f'/var/log/card/{dt.datetime.now().isoformat()}.log')]
)


async_mode = 'gevent'
app = fl.Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
# socketio = fl_sock.SocketIO(app)
socketio = fl_sock.SocketIO(app, async_mode=async_mode, path='socket.io', cors_allowed_origins=["http://127.0.0.1:8080",
                                                                                        "http://localhost:4200",
                                                                                        "http://localhost:4201",
                                                                                        "https://gusev.vladislav.ru"])

@app.route('/')
def index():
    return 'Привет!'


if __name__ == '__main__':
    socketio.run(app, '127.0.0.1', 8080, allow_unsafe_werkzeug=True)
