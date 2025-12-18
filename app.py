from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
from database import insert_data

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key
socketio = SocketIO(app, cors_allowed_origins="*")

# Keep track of which room each socket is in
users = {}

# ------------------ Routes ------------------


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            return "Passwords do not match, please try again"
        else:
            print("Username:", username)
            print("Email id:", email)
            print("Password:", password)
            user_exists = insert_data.user_exists(email)
            if not user_exists:
                print("Registering new account....")
                success, message = insert_data.add_user_accounts(username, password, email)
                if success:
                    print("User account created successfully!")
                    return redirect(url_for("login"))
                else:
                    print("User Account creation/registration Failed")
                    return render_template("new_user_registration.html")
            else:
                print("Email address already registered. Please proceed to the login page")
                return redirect(url_for("login"))
    return render_template("new_user_registration.html")


@app.route("/snq_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == "password":
            session['username'] = username
            return redirect(url_for("home"))
        elif username == "admin2" and password == "password2":
            session['username'] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials, try again."
    return render_template("login.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    username = session.get('username', 'Guest')

    if request.method == "POST":
        action = request.form.get("action")

        if action == "new_meeting":
            return redirect(url_for("new_meeting"))

        elif action == "join_meeting":
            meeting_input = request.form.get("meeting_id", "").strip()

            if not meeting_input:
                return "Meeting ID cannot be empty", 400

            if "/meeting/" in meeting_input:
                room_id = meeting_input.split("/meeting/")[-1]
            else:
                room_id = meeting_input

            return redirect(url_for("meeting_room", room_id=room_id))

    return render_template("snq_home.html", username=username)


@app.route('/new_meeting', methods=["GET", "POST"])
def new_meeting():
    room_id = str(uuid.uuid4())
    return redirect(url_for('start_meeting', room_id=room_id))


@app.route('/start_meeting/<room_id>', methods=["GET", "POST"])
def start_meeting(room_id):
    username = session.get('username', 'Guest')
    subject = ""

    if request.method == "POST":
        subject = request.form.get("meeting_subject_line", "").strip()
        print("Meeting Subject:", subject)

        if not subject:
            return "Meeting subject cannot be empty.", 400

        session['meeting_subject'] = subject

        return redirect(url_for('meeting_room', room_id=room_id))

    return render_template('new_meeting.html', room_id=room_id, username=username, meeting_subject=subject)


@app.route('/meeting/<room_id>', methods=["GET", "POST"])
def meeting_room(room_id):
    username = session.get('username', 'Guest')
    meeting_subject = session.get('meeting_subject', 'No Subject')
    return render_template('room.html', room_id=room_id, username=username, meeting_subject=meeting_subject)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()  # Clears all session data
    return redirect(url_for("login"))

# ------------------ WebSocket Events ------------------


@socketio.on('message')
def handle_message(data):
    room = data.get('room')
    emit('message', data, room=room)


@socketio.on('join')
def handle_join(data):
    room = data.get('room')
    join_room(room)
    users[request.sid] = room
    print(f"Socket {request.sid} joined room {room}")
    emit('user-joined', {'socketId': request.sid}, room=room, include_self=False)
    emit('message', {'type': 'chat', 'text': 'A user has joined the room.'}, room=room)


@socketio.on('offer')
def handle_offer(data):
    to = data.get('to')
    sdp = data.get('sdp')
    if to:
        emit('offer', {'from': request.sid, 'sdp': sdp}, room=to)


@socketio.on('answer')
def handle_answer(data):
    to = data.get('to')
    sdp = data.get('sdp')
    if to:
        emit('answer', {'from': request.sid, 'sdp': sdp}, room=to)


@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    to = data.get('to')
    candidate = data.get('candidate')
    if to:
        emit('ice-candidate', {'from': request.sid, 'candidate': candidate}, room=to)


@socketio.on('disconnect')
def handle_disconnect():
    room = users.pop(request.sid, None)
    if room:
        emit('user-disconnected', {'socketId': request.sid}, room=room)
    print(f"Socket {request.sid} disconnected")


# ------------------ Run Server ------------------

if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True)