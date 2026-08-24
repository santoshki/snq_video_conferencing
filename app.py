from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import json
import os
import uuid
import jwt
import time
from config import JWT_SECRET, JWT_ALGO, JWT_EXP_SECONDS, FLASK_SECRET_KEY, ICE_SERVERS
import ws_server
from database import create_record, authenticate_user, create_guest
from database.supabase_client import get_supabase

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

def normalize_meeting_id(raw_id):
    if not raw_id:
        return None
    normalized = raw_id.strip().lower()
    return normalized or None


@app.get("/room_styles.css")
def room_styles():
    return send_from_directory(app.static_folder, "room_styles.css", max_age=0)
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
            user_id = create_record.create_user_record(first_name,last_name,email,username,password)
            if not user_id:
                return "User already exists or account creation failed.", 400

            session["user"] = username
            session["user_id"] = user_id

            return redirect(url_for("home"))

    return render_template("create_account.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email:
            return "Email is required.", 400
        try:
            redirect_url = url_for(
                "reset_password",
                _external=True
            )

            print("Password reset redirect URL:", redirect_url)
            response = get_supabase().auth.reset_password_email(
                email,
                {
                    "redirect_to": redirect_url
                }
            )
            print("Password reset response:", response)
            return """
                If an account exists with this email address,
                a password reset link has been sent.
            """
        except Exception as e:
            print("Password reset error:", e)
            return f"Unable to process password reset request: {str(e)}", 500
    return render_template("forgot_password.html")


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if request.method == "GET":
        return render_template("reset_password.html")

    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")
    access_token = request.form.get("access_token", "")
    refresh_token = request.form.get("refresh_token", "")

    if password != confirm_password:
        return "Passwords do not match.", 400
    if len(password) < 8:
        return "Password must be at least 8 characters.", 400
    if not access_token:
        return "Invalid or expired password reset link.", 400

    try:
        get_supabase().auth.set_session(
            access_token,
            refresh_token
        )
        response = get_supabase().auth.update_user({
            "password": password
        })
        if response.user:
            session.clear()
            return redirect(url_for("login"))
        return "Unable to reset password.", 400

    except Exception as e:
        print("Password update error:", e)
        return f"Unable to reset password: {str(e)}", 500
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
        elif action == "join_meeting":
            meeting_id = normalize_meeting_id(request.form.get("meeting_id"))
            meeting_name = request.form.get("meeting_name")
            if not meeting_id:
                return redirect(url_for("home"))

            session["meeting_id"] = meeting_id
            session["meeting_title"] = (
                meeting_name.strip()
                if meeting_name
                else "SnQ Meeting"
            )
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


@app.route("/guest_register/<room_id>", methods=["GET", "POST"])
def guest_register(room_id):
    """Allow guests to register before joining a meeting."""

    normalized_room_id = normalize_meeting_id(room_id)
    if not normalized_room_id:
        return redirect(url_for("home"))

    if normalized_room_id != room_id:
        return redirect(url_for("guest_register", room_id=normalized_room_id))

    room_id = normalized_room_id

    # If user is already logged in, redirect directly to meeting
    if "user" in session:
        return redirect(url_for("meeting_room", room_id=room_id))

    # If guest already registered for this session, redirect to meeting
    if "guest_id" in session and "guest_name" in session:
        return redirect(url_for("meeting_room", room_id=room_id))

    if request.method == "POST":
        guest_name = request.form.get("guest_name", "").strip()
        guest_email = request.form.get("guest_email", "").strip()

        print(f"\n🔵 Guest registration attempt:")
        print(f"   Name: {guest_name}")
        print(f"   Email: {guest_email if guest_email else '(none)'}")
        print(f"   Room: {room_id}")

        if not guest_name:
            print("❌ Name validation failed - name is empty")
            return render_template(
                "guest_register.html",
                room_id=room_id,
                meeting_title=session.get("meeting_title", "SnQ Meeting"),
                error="Guest name is required."
            ), 400

        # Create guest record in database
        print("📤 Calling create_guest_record...")
        guest_id = create_guest.create_guest_record(guest_name, guest_email if guest_email else None)

        print(f"📥 create_guest_record returned: {guest_id}")

        if not guest_id:
            print("❌ Guest registration failed - no guest_id returned")
            error_msg = (
                "Failed to register as guest. Please try again. "
                "Check the terminal for error details."
            )
            return render_template(
                "guest_register.html",
                room_id=room_id,
                meeting_title=session.get("meeting_title", "SnQ Meeting"),
                error=error_msg
            ), 500

        # Store guest info in session
        session["guest_id"] = guest_id
        session["guest_name"] = guest_name
        session["guest_email"] = guest_email if guest_email else None

        print(f"✅ Guest session created: {guest_name} ({guest_id})")
        return redirect(url_for("meeting_room", room_id=room_id))

    return render_template(
        "guest_register.html",
        room_id=room_id,
        meeting_title=session.get("meeting_title", "SnQ Meeting")
    )


@app.route("/meeting/<room_id>")
def meeting_room(room_id):

    normalized_room_id = normalize_meeting_id(room_id)
    if not normalized_room_id:
        return redirect(url_for("home"))

    if normalized_room_id != room_id:
        return redirect(url_for("meeting_room", room_id=normalized_room_id))

    room_id = normalized_room_id

    # Check if user is authenticated (logged in) or registered as guest
    username = session.get("user")
    guest_id = session.get("guest_id")
    guest_name = session.get("guest_name")

    # If neither logged in nor registered as guest, redirect to guest registration
    if not username and not (guest_id and guest_name):
        return redirect(url_for("guest_register", room_id=room_id))

    # Use logged-in username or guest name
    if username:
        display_name = username
    else:
        display_name = guest_name

    meeting_title = session.get("meeting_title", "SnQ Meeting")
    connection_id = uuid.uuid4().hex

    token = jwt.encode(
        {
            "user": display_name,
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
        username=display_name,
        token=token,
        connection_id=connection_id,
        ice_servers_json=json.dumps(ICE_SERVERS)
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False, threaded=True)