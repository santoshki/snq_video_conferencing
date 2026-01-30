from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import jwt
import time

app = Flask(__name__)

# ------------------------
# CONFIG
# ------------------------
app.secret_key = "your_flask_session_secret"

JWT_SECRET = "super_shared_secret_change_this"
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 3600  # 1 hour


# ------------------------
# LOGIN
# ------------------------
@app.route("/snq_login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # ⚠️ Replace with DB later
        if username == "admin" and password == "password":
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid credentials", 401

    return render_template("login.html")


@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))
# ------------------------
# HOME
# ------------------------
@app.route("/home", methods=["GET", "POST"])
def home():
    username = session.get("user")

    if not username:
        return redirect(url_for("login"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "new_meeting":
            return redirect(url_for("new_meeting"))

    return render_template("snq_home.html", username=username)


# ------------------------
# CREATE MEETING
# ------------------------
@app.route("/new_meeting")
def new_meeting():
    if "user" not in session:
        return redirect(url_for("login"))

    room_id = str(uuid.uuid4())
    return redirect(url_for("meeting_room", room_id=room_id))


# ------------------------
# MEETING ROOM
# ------------------------
@app.route("/meeting/<room_id>")
def meeting_room(room_id):
    username = session.get("user", "Guest")

    # Create JWT for Erlang
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
        username=username,
        token=token
    )


# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
