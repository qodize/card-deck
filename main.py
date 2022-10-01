import datetime as dt
import os
import logging

import flask as fl
import flask_socketio as fl_sock
import config
import db_manager

os.makedirs('/tmp/cardlog', exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(f'/tmp/cardlog/{dt.datetime.now().isoformat()}.log')]
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
    return f'{db_manager.ping()}'


@app.route('/api/users/<phone>', methods=['GET'])
def get_user(phone):
    user = db_manager.Users.get(phone)
    return user.__dict__ if user else fl.Response(status=404)


@app.route('/api/users/<user_id>/groups', methods=['GET'])
def get_user_groups(user_id):
    groups = db_manager.Users.get_user_groups(user_id)
    return {'groups': [group.__dict__ for group in groups]}


@app.route('/api/groups/<group_id>/users', methods=['GET'])
def get_group_users(group_id):
    users = db_manager.Groups.get_group_users(group_id)
    return {'users': [user.__dict__ for user in users]}


@app.route("/api/groups/", methods=['POST'])
def create_group():
    data = fl.request.json
    owner_id = data.get('owner_id')
    if not owner_id:
        return fl.Response(status=400)
    group = db_manager.Groups.create(owner_id)
    return group.__dict__


if __name__ == '__main__':
    socketio.run(app, '127.0.0.1', 8080, debug=True)
