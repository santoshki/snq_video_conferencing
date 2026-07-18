from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import uuid
import jwt
import time

from config import JWT_SECRET, JWT_ALGO, JWT_EXP_SECONDS
from ws_server import start_signaling_server

app = Flask(__name__)

app.secret_key = "your_flask_session_secret"


@app.route("/snq_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Replace with database authentication later
        if username == "admin" and password == "password":
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():

    if request.method == "POST":

        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return "Passwords do not match.", 400
        if len(password)<8:
            return "Password must be at least 8 characters.", 400
        else:
            session["user"] = username
            return redirect(url_for("home"))

    return render_template("create_account.html")

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/home", methods=["GET", "POST"])
def home():

    username = session.get("user")

    if not username:
        return redirect(url_for("login"))

    if request.method == "POST":

        action = request.form.get("action")

        # ======================================================
        # CREATE NEW MEETING
        # ======================================================
        if action == "create_meeting":

            meeting_id = request.form.get("meeting_id")
            meeting_title = request.form.get("meeting_title")

            if not meeting_id:
                return redirect(url_for("home"))

            # Store meeting information
            session["meeting_id"] = meeting_id
            session["meeting_title"] = meeting_title.strip() if meeting_title else "Untitled Meeting"

            # TODO:
            # Save meeting_id + meeting_title in database

            return redirect(
                url_for(
                    "meeting_room",
                    room_id=meeting_id
                )
            )

        # ======================================================
        # JOIN EXISTING MEETING
        # ======================================================
        elif action == "join_meeting":

            meeting_id = request.form.get("meeting_id")
            meeting_name = request.form.get("meeting_name")

            if not meeting_id:
                return redirect(url_for("home"))

            session["meeting_id"] = meeting_id

            # If user entered a meeting name, use it.
            # Otherwise we'll display a default title.
            session["meeting_title"] = (
                meeting_name.strip()
                if meeting_name
                else "SnQ Meeting"
            )

            # TODO:
            # Later fetch actual title from DB using meeting_id

            return redirect(
                url_for(
                    "meeting_room",
                    room_id=meeting_id
                )
            )

    return render_template(
        "snq_home.html",
        username=username
    )


@app.route("/generate_meeting_id")
def generate_meeting_id():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Google Meet style meeting id
    meeting_id = "-".join([
        uuid.uuid4().hex[:3],
        uuid.uuid4().hex[3:6],
        uuid.uuid4().hex[6:9]
    ])

    return jsonify({
        "meeting_id": meeting_id
    })


@app.route("/meeting/<room_id>")
def meeting_room(room_id):

    username = session.get("user", "Guest")

    meeting_title = session.get("meeting_title", "SnQ Meeting")

    token = jwt.encode(
        {
            "user": username,
            "room": room_id,
            "exp": int(time.time()) + JWT_EXP_SECONDS
        },
        JWT_SECRET,
        algorithm=JWT_ALGO
    )

    return render_template(
        "room.html",
        room_id=room_id,
        meeting_title=meeting_title,
        username=username,
        token=token
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    # use_reloader=False keeps this to a single process. With the reloader
    # on, Flask spawns a child process that re-imports this module, and on
    # Windows in particular the old process/socket doesn't always get
    # cleaned up on restart, which causes "address already in use" (10048)
    # errors on the signaling server's port.
    start_signaling_server(port=8080)
    app.run(debug=True, use_reloader=False)