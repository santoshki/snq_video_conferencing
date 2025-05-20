from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import uuid

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/snq_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password":
            return redirect(url_for("home"))
        else:
            return "Invalid credentials, try again."
    return render_template("login.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "new_meeting":
            return redirect(url_for("new_meeting"))
        elif action == "join_meeting":
            return "Join Meeting feature not implemented yet."
    return render_template("snq_home.html")


@app.route('/new_meeting')
def new_meeting():
    room_id = str(uuid.uuid4())
    return redirect(url_for('meeting_room', room_id=room_id))


@app.route('/meeting/<room_id>')
def meeting_room(room_id):
    return render_template('room.html', room_id=room_id)


@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    emit('message', data, room=room)


@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    join_room(room)
    emit('message', {'type': 'chat', 'text': 'A user has joined the room.'}, room=room)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

