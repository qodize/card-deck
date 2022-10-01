import flask as fl
import flask_socketio as fl_sock
import config

app = fl.Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = fl_sock.SocketIO(app)


@app.route('/')
def index():
    return 'Привет!'


if __name__ == '__main__':
    socketio.run(app, '127.0.0.1', 8080)
