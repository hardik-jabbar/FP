import socketio

# Create a Socket.IO server instance
# async_mode="asgi" is for FastAPI/Uvicorn integration.
# cors_allowed_origins="*" is permissive; adjust for production.
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    # logger=True,  # Set to True for more verbose Socket.IO logging
    # engineio_logger=True  # Set to True for Engine.IO specific logging
)

# Create an ASGI application that wraps the Socket.IO server
socket_app = socketio.ASGIApp(
    sio,
    # socketio_path='socket.io' # Default path, can be customized if needed e.g. /ws/socket.io
)

# --- Basic Socket.IO Event Handlers ---

@sio.event
async def connect(sid, environ):
    """
    Handles new client connections.
    `environ` contains the WSGI/ASGI environment, including headers for potential auth.
    """
    print(f"Socket.IO client connected: SID={sid}")
    # TODO: Authentication logic
    # Example: token = environ.get('HTTP_AUTHORIZATION', '').split('Bearer ')[-1]
    # user = await authenticate_ws_user(token) # Your async function
    # if not user:
    #     raise socketio.exceptions.ConnectionRefusedError('Authentication failed')
    # await sio.save_session(sid, {'user_id': user.id, 'username': user.email})
    # print(f"User {user.email} authenticated for SID {sid}")
    await sio.emit('connection_ack', {'message': 'Successfully connected!', 'sid': sid}, room=sid)


@sio.event
async def disconnect(sid):
    """Handles client disconnections."""
    print(f"Socket.IO client disconnected: SID={sid}")
    # session = await sio.get_session(sid)
    # if session and 'field_room' in session:
    #     room_name = session['field_room']
    #     # Notify others in the room
    #     await sio.emit("user_left_field", {"sid": sid, "user_id": session.get('user_id')}, room=room_name, skip_sid=sid)
    #     print(f"User {session.get('user_id')} (SID: {sid}) left room {room_name}")
    # Clean up session if needed
    # await sio.save_session(sid, {})


# --- Field-Specific Room Management ---

@sio.on("join_field_room")
async def handle_join_field_room(sid, data: dict):
    """Allows a client to join a room for a specific field_id to receive GPS updates."""
    field_id = data.get("field_id")
    if not field_id:
        await sio.emit("room_join_error", {"message": "field_id is required"}, room=sid)
        return

    room_name = f"field_{field_id}"
    sio.enter_room(sid, room_name)
    # await sio.save_session(sid, {**await sio.get_session(sid), 'field_room': room_name}) # Store current room
    print(f"Client {sid} joined room: {room_name}")
    await sio.emit("room_joined_ack", {"room": room_name}, room=sid)
    # Notify others in the room (optional)
    # await sio.emit("user_joined_field", {"sid": sid, "field_id": field_id}, room=room_name, skip_sid=sid)


@sio.on("leave_field_room")
async def handle_leave_field_room(sid, data: dict):
    """Allows a client to leave a field-specific room."""
    field_id = data.get("field_id")
    if not field_id:
        await sio.emit("room_leave_error", {"message": "field_id is required"}, room=sid)
        return

    room_name = f"field_{field_id}"
    sio.leave_room(sid, room_name)
    # session = await sio.get_session(sid)
    # if session and session.get('field_room') == room_name:
    #     del session['field_room'] # Remove from session
    #     await sio.save_session(sid, session)
    print(f"Client {sid} left room: {room_name}")
    await sio.emit("room_left_ack", {"room": room_name}, room=sid)
    # Notify others (optional)
    # await sio.emit("user_left_field", {"sid": sid, "field_id": field_id}, room=room_name, skip_sid=sid)


# --- GPS Location Updates ---

@sio.on("update_location")
async def handle_update_location(sid, data: dict):
    """
    Handles incoming GPS location updates from a client.
    Data should ideally include: {'field_id': ..., 'latitude': ..., 'longitude': ..., 'timestamp': ...}
    """
    print(f"Received location update from SID {sid}: {data}")

    field_id = data.get("field_id")
    # TODO: Validate data structure (lat, lon, field_id)
    # TODO: Authenticate: Check if user associated with 'sid' is allowed to update this 'field_id'.
    #       This requires retrieving user from session: session = await sio.get_session(sid)
    #       Then, check user's permissions for the field_id.

    if field_id:
        room_name = f"field_{field_id}"
        # Broadcast the location data to all clients in the specific field's room, except the sender.
        await sio.emit("location_broadcast", data, room=room_name, skip_sid=sid)
        print(f"Location data from SID {sid} broadcasted to room {room_name}")
    else:
        # Send error back to sender if field_id is missing
        await sio.emit("location_update_error", {"message": "field_id is required in location data"}, room=sid)
        print(f"Location update from SID {sid} rejected: missing field_id.")
