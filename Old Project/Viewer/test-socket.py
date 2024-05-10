from flask import Flask
from flask_socketio import SocketIO, Namespace, emit

app = Flask(__name__)
socketio = SocketIO(app)

if __name__ == '__main__':
    socketio.run(app, debug=True)


class MyCustomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_event(self, data):
        emit('my_response', data)


socketio.on_namespace(MyCustomNamespace('/'))
