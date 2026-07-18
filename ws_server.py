import json
import threading

import jwt
from flask import request
from flask_sock import Sock

from config import JWT_SECRET, JWT_ALGO

# room_id -> { connection_id: {"ws": ws_connection, "user": username} }
#
# Keyed by a unique per-connection id rather than username. Two people
# with the same display name (or the same person open in two tabs) each
# get their own slot instead of overwriting/kicking each other, which is
# what capped this at 2 working participants before.
rooms = {}
rooms_lock = threading.Lock()


def _authenticate(token):
    if not token:
        return None, None, None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None, None, None
    return payload.get("room"), payload.get("user"), payload.get("cid")


def _broadcast(room_id, message, exclude_cid=None):
    with rooms_lock:
        room = rooms.get(room_id, {})
        targets = [(cid, entry["ws"]) for cid, entry in room.items() if cid != exclude_cid]

    data = json.dumps(message)
    dead_cids = []
    for cid, sock in targets:
        try:
            sock.send(data)
        except Exception:
            dead_cids.append(cid)

    if dead_cids:
        _cleanup_dead_connections(room_id, dead_cids)


def _send_to_cid(room_id, target_cid, message):
    """Sends a targeted message to one specific connection inside a room."""
    with rooms_lock:
        room = rooms.get(room_id, {})
        entry = room.get(target_cid)
        sock = entry["ws"] if entry else None

    if sock:
        try:
            sock.send(json.dumps(message))
        except Exception:
            _cleanup_dead_connections(room_id, [target_cid])


def _cleanup_dead_connections(room_id, dead_cids):
    """Helper to prune disconnected sockets safely."""
    with rooms_lock:
        room = rooms.get(room_id)
        if room:
            for cid in dead_cids:
                room.pop(cid, None)


def init_app(app):
    """Attach the /ws WebSocket route to the given Flask app."""
    sock = Sock(app)

    @sock.route("/ws")
    def ws_route(ws):
        token = request.args.get("token")
        room_id, username, cid = _authenticate(token)
        if not room_id or not username or not cid:
            ws.close()
            return

        with rooms_lock:
            room = rooms.setdefault(room_id, {})
            old_entry = room.get(cid)
            room[cid] = {"ws": ws, "user": username}
            others = [
                {"cid": other_cid, "user": entry["user"]}
                for other_cid, entry in room.items()
                if other_cid != cid
            ]
            count = len(room)

        # Same connection id reconnecting (e.g. a flaky socket retry) closes
        # its own stale predecessor. This can no longer happen to a
        # *different* participant, since every participant now has a
        # distinct cid.
        if old_entry is not None and old_entry["ws"] is not ws:
            try:
                old_entry["ws"].close()
            except Exception:
                pass

        ws.send(json.dumps({"type": "room-info", "users": others, "count": count}))
        _broadcast(
            room_id,
            {"type": "user-joined", "user": username, "cid": cid, "count": count},
            exclude_cid=cid,
        )

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

                # Authoritatively stamp the sender's identity from the token
                # rather than trusting whatever the client claims.
                msg["user"] = username
                msg["cid"] = cid

                # Extract the direct target connection if one is provided
                target_cid = msg.get("target")

                # WebRTC Handshaking signals MUST be routed 1-to-1 directly to the target
                if msg_type in ["offer", "answer", "ice"] and target_cid:
                    _send_to_cid(room_id, target_cid, msg)
                else:
                    # Global room events (Chat messages, Reactions, Screen Share Toggles, Hand Raises)
                    _broadcast(room_id, msg, exclude_cid=cid)
        finally:
            with rooms_lock:
                current_room = rooms.get(room_id, {})
                if current_room.get(cid, {}).get("ws") is ws:
                    current_room.pop(cid, None)
                remaining = len(current_room)
                if not current_room:
                    rooms.pop(room_id, None)

            _broadcast(
                room_id,
                {"type": "user-left", "user": username, "cid": cid, "count": remaining},
            )

    return sock