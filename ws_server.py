import json
import threading

import jwt
from flask import request
from flask_sock import Sock

from config import JWT_SECRET, JWT_ALGO

# room_id -> { username: ws_connection }
rooms = {}
rooms_lock = threading.Lock()


def _authenticate(token):
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None, None
    return payload.get("room"), payload.get("user")


def _broadcast(room_id, message, exclude_user=None):
    with rooms_lock:
        room = rooms.get(room_id, {})
        targets = [(user, sock) for user, sock in room.items() if user != exclude_user]

    data = json.dumps(message)
    dead_users = []
    for user, sock in targets:
        try:
            sock.send(data)
        except Exception:
            dead_users.append(user)

    if dead_users:
        _cleanup_dead_users(room_id, dead_users)


def _send_to_user(room_id, target_user, message):
    """Sends a targeted message to a specific user inside a room."""
    with rooms_lock:
        room = rooms.get(room_id, {})
        sock = room.get(target_user)

    if sock:
        try:
            sock.send(json.dumps(message))
        except Exception:
            _cleanup_dead_users(room_id, [target_user])


def _cleanup_dead_users(room_id, dead_users):
    """Helper to prune disconnected sockets safely."""
    with rooms_lock:
        room = rooms.get(room_id)
        if room:
            for user in dead_users:
                room.pop(user, None)


def init_app(app):
    """Attach the /ws WebSocket route to the given Flask app."""
    sock = Sock(app)

    @sock.route("/ws")
    def ws_route(ws):
        token = request.args.get("token")
        room_id, username = _authenticate(token)
        if not room_id or not username:
            ws.close()
            return

        with rooms_lock:
            room = rooms.setdefault(room_id, {})
            old_socket = room.get(username)
            room[username] = ws
            others = [u for u in room.keys() if u != username]
            count = len(room)

        # If the same user reconnects (refresh/reconnect), close their old socket.
        if old_socket is not None and old_socket is not ws:
            try:
                old_socket.close()
            except Exception:
                pass

        ws.send(json.dumps({"type": "room-info", "users": others, "count": count}))
        _broadcast(room_id, {"type": "user-joined", "user": username, "count": count}, exclude_user=username)

        try:
            while True:
                raw = ws.receive()
                if raw is None:
                    break  # client disconnected
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get("type")
                if msg_type == "join":
                    continue  # already handled on connect
                if msg_type == "leave":
                    break

                # Authoritatively stamp the username from the token
                msg["user"] = username

                # Extract the direct target user if one is provided by the frontend
                target_user = msg.get("target")

                # WebRTC Handshaking signals MUST be routed 1-to-1 directly to the target
                if msg_type in ["offer", "answer", "ice"] and target_user:
                    _send_to_user(room_id, target_user, msg)
                else:
                    # Global room events (Chat messages, Reactions, Screen Share Toggles, Hand Raises)
                    _broadcast(room_id, msg, exclude_user=username)
        finally:
            with rooms_lock:
                current_room = rooms.get(room_id, {})
                if current_room.get(username) is ws:
                    current_room.pop(username, None)
                remaining = len(current_room)
                if not current_room:
                    rooms.pop(room_id, None)

            _broadcast(room_id, {"type": "user-left", "user": username, "count": remaining})

    return sock