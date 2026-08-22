from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import json
import os
import uuid
import jwt
import time
from config import JWT_SECRET, JWT_ALGO, JWT_EXP_SECONDS, FLASK_SECRET_KEY, ICE_SERVERS
import ws_server
from database import create_record,authenticate_user

app = Flask(__name__)

app.secret_key = FLASK_SECRET_KEY


def normalize_meeting_id(raw_id):

    if not raw_id:
        return None
    normalized = raw_id.strip().lower()
    return normalized or None


@app.get("/room_styles.css")
def room_styles():
    """Serve the meeting stylesheet explicitly for deployments that bypass /static."""
    return send_from_directory(app.static_folder, "room_styles.css", max_age=0)

# Attaches the /ws WebSocket route to this same Flask app/port instead of
# spinning up a separate server on its own port (which Render can't expose).
ws_server.init_app(app)


@app.route("/snq_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate_user.authenticate_user(username, password)
        if user:
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
            user_id = create_record.create_user_record(first_name,last_name,email,username,confirm_password)
            if not user_id:
                return "User already exists or account creation failed.", 400

            session["user"] = username
            session["user_id"] = user_id

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

            meeting_id = normalize_meeting_id(request.form.get("meeting_id"))
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

            meeting_id = normalize_meeting_id(request.form.get("meeting_id"))
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

    normalized_room_id = normalize_meeting_id(room_id)
    if not normalized_room_id:
        return redirect(url_for("home"))

    # Redirect to the canonical (lowercased/trimmed) URL if it differs, so
    # every participant's browser bar, invite links, and JWT "room" claim
    # all agree on the exact same string used as the WebSocket room key.
    if normalized_room_id != room_id:
        return redirect(url_for("meeting_room", room_id=normalized_room_id))

    room_id = normalized_room_id

    username = session.get("user", "Guest")

    meeting_title = session.get("meeting_title", "SnQ Meeting")

    # A fresh connection id per page load (not the username) is what
    # identifies a participant's WebSocket in the room. Using the username
    # for that used to mean two participants with the same display name
    # (or the same person open in two tabs) would collide and boot each
    # other out of the room, which is what broke things beyond 2 people.
    connection_id = uuid.uuid4().hex

    token = jwt.encode(
        {
            "user": username,
            "room": room_id,
            "cid": connection_id,
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
        token=token,
        connection_id=connection_id,
        ice_servers_json=json.dumps(ICE_SERVERS)
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    # Render (and most PaaS hosts) assign the externally-reachable port via
    # the $PORT environment variable and only expose that single port, so
    # we must bind to it rather than a hardcoded port. Locally this falls
    # back to 5000. threaded=True lets the dev server handle more than one
    # concurrent WebSocket connection at a time, which the plain Werkzeug
    # server otherwise can't do.
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False, threaded=True)