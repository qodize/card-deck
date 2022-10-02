import datetime as dt
import os
import logging

import flask as fl
import flask_socketio as fl_sock
import psycopg2

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
                                                                                        "https://gusev-vladislav.ru"])


@app.route('/')
def index():
    return """<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js" integrity="sha512-q/dWJ3kcmjBLU4Qc47E4A9kTB4m3wuTY7vkFJDTZKjTs8jhyGQnaUrxa0Ytd0ssMZhbNua9hE+E7Qv1j+DyZwA==" crossorigin="anonymous"></script>
<script type="text/javascript" charset="utf-8">
    var socket = io();
    socket.on('connect', function() {
        socket.emit('my event', {data: 'I\'m connected!'});
    });
</script>"""


@app.route('/api/users/<phone>', methods=['GET'])
def get_user(phone):
    user = db_manager.Users.get(phone)
    return user.__dict__ if user else fl.Response(status=404)


@app.route('/api/users/<phone>/groups', methods=['GET'])
def get_user_groups(phone):
    groups = db_manager.Users.get_user_groups(phone)
    for group in groups:
        group.users = db_manager.Groups.get_group_users(group.id)
        for i in range(len(group.users)):
            group.users[i] = group.users[i].__dict__
        for user in group.users:
            user['last_emotion_value'] = db_manager.Emotions.get_last_emotion_value(user['id'])

    print({'groups': [group.__dict__ for group in groups]})
    return {'groups': [group.__dict__ for group in groups]}


@app.route('/api/groups/<group_id>/users', methods=['GET'])
def get_group_users(group_id):
    users = db_manager.Groups.get_group_users(group_id)
    return {'users': [user.__dict__ for user in users]}


@app.route("/api/groups/", methods=['POST'])
def create_group():
    data = fl.request.json
    owner_id = data.get('owner_id', -1)
    try:
        group = db_manager.Groups.create(owner_id)
    except psycopg2.Error as e:
        logging.error(e)
        return fl.Response(status=400)
    return group.__dict__


@app.route("/api/groups/<group_id>/emotions")
def get_group_emotions(group_id):
    emotions = db_manager.Groups.get_group_emotions(group_id)
    e_dicts = [e.__dict__ for e in emotions]
    for e in e_dicts:
        e['ts'] = e['ts'].isoformat()
    return {'emotions': e_dicts}


@app.route("/api/emotions", methods=['GET', 'POST'])
def emotions_handler():
    if fl.request.method == 'POST':
        data = fl.request.json
        phonenumber = data.get('user_id')
        value = data.get('value')
        title = data.get('title', '')
        description = data.get('description', '')
        if phonenumber is None or value is None:
            return fl.Response(status=400)
        e = db_manager.Emotions.create_emotion(phonenumber, value, title, description)
        e_data = e.__dict__
        e_data['ts'] = e_data['ts'].isoformat()
        socketio.emit('emotion_created', e_data)
        return e_data
    elif fl.request.method == 'GET':
        emotions_list = db_manager.Emotions.get_all_emotions()
        emotions_dict = dict()
        for emotion in emotions_list:
            emotions_dict[emotion.user_id] = emotions_dict.get(emotion.user_id, []) + [emotion.__dict__]
        for emotion_ls in emotions_dict.values():
            for emotion in emotion_ls:
                emotion['ts'] = emotion['ts'].isoformat()
        return emotions_dict


@socketio.on('connect')
def connect():
    fl_sock.emit('connect', 'Connected')


@socketio.on('disconnect')
def disconnect():
    print('Disconnected')


if __name__ == '__main__':
    socketio.run(app, '127.0.0.1', 8080, debug=True)
