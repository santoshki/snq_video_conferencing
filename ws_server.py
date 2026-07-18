"""
WebSocket signaling server for SnQ meetings.

room.html connects to ws://<host>:8080/ws?token=<jwt>. That token is the
same JWT that /meeting/<room_id> already issues (see app.py), so this
server just decodes it to find out which room/user the socket belongs to,
then relays messages between the participants of that room:

  - join    -> sends "room-info" back to the new client, and "user-joined"
               to everyone already in the room
  - leave / disconnect -> sends "user-left" to everyone still in the room
  - offer / answer / ice / chat / video-toggle / hand-raise / reaction
               -> forwarded as-is to the other participant(s) in the room

Without this server running, every client's WebSocket never connects to
anything, which is why two participants never sync and chat never
delivers - there was simply nothing listening on port 8080.
"""

import asyncio
import json
import logging
import threading
from urllib.parse import urlparse, parse_qs

import jwt
import websockets

from config import JWT_SECRET, JWT_ALGO

logger = logging.getLogger("ws_server")

# room_id -> { username: websocket }
rooms: dict[str, dict[str, "websockets.WebSocketServerProtocol"]] = {}


async def _broadcast(room_id, message, exclude_user=None):
    room = rooms.get(room_id, {})
    if not room:
        return
    data = json.dumps(message)
    dead_users = []
    for user, sock in list(room.items()):
        if user == exclude_user:
            continue
        try:
            await sock.send(data)
        except websockets.exceptions.ConnectionClosed:
            dead_users.append(user)
    for user in dead_users:
        room.pop(user, None)


def _authenticate(path):
    """Pull the JWT out of the query string and validate it."""
    query = parse_qs(urlparse(path).query)
    token = query.get("token", [None])[0]
    if not token:
        return None, None
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError as exc:
        logger.warning("Rejected WS connection: %s", exc)
        return None, None
    return payload.get("room"), payload.get("user")


async def _handler(websocket, path=None):
    # websockets>=13 no longer passes `path` to the handler; fall back to
    # the attribute exposed on the connection object in that case.
    if path is None:
        path = getattr(websocket, "path", "") or getattr(
            getattr(websocket, "request", None), "path", ""
        )

    room_id, username = _authenticate(path)
    if not room_id or not username:
        await websocket.close(code=4401, reason="Invalid or missing token")
        return

    room = rooms.setdefault(room_id, {})

    # If the same user reconnects (refresh/reconnect), replace their old socket.
    old_socket = room.get(username)
    if old_socket is not None and old_socket is not websocket:
        try:
            await old_socket.close()
        except Exception:
            pass

    room[username] = websocket

    try:
        others = [u for u in room.keys() if u != username]
        await websocket.send(json.dumps({
            "type": "room-info",
            "users": others,
            "count": len(room),
        }))
        await _broadcast(room_id, {
            "type": "user-joined",
            "user": username,
            "count": len(room),
        }, exclude_user=username)

        async for raw in websocket:
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = msg.get("type")

            if msg_type == "join":
                # Already handled above on connect - nothing more to do.
                continue
            if msg_type == "leave":
                break

            # Relay everything else (offer/answer/ice/chat/video-toggle/
            # hand-raise/reaction) to the other participant(s) in the room.
            # Always stamp the authoritative username from the token so a
            # client can't spoof another participant's identity.
            msg["user"] = username
            await _broadcast(room_id, msg, exclude_user=username)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        current_room = rooms.get(room_id, {})
        if current_room.get(username) is websocket:
            current_room.pop(username, None)
        remaining = len(current_room)
        if not current_room:
            rooms.pop(room_id, None)
        await _broadcast(room_id, {
            "type": "user-left",
            "user": username,
            "count": remaining,
        })


async def _serve(host="0.0.0.0", port=8080):
    async with websockets.serve(_handler, host, port):
        logger.info("Signaling server listening on ws://%s:%s/ws", host, port)
        await asyncio.Future()  # run forever


def _run_forever(host, port):
    asyncio.run(_serve(host, port))


def start_signaling_server(host="0.0.0.0", port=8080):
    """Start the signaling server on a background thread so it can run
    alongside the Flask app in the same process."""
    thread = threading.Thread(
        target=_run_forever, args=(host, port), daemon=True
    )
    thread.start()
    return thread