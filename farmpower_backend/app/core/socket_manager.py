import socketio

# 1. Create a Socket.IO server instance
# For FastAPI, async_mode="asgi" is used.
# cors_allowed_origins="*" is permissive; adjust for production (e.g., your frontend URL).
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    # logger=True, # Uncomment for detailed Socket.IO logs
    # engineio_logger=True # Uncomment for detailed Engine.IO logs
)

# 2. Create an ASGI application for the Socket.IO server
# This will be mounted into the main FastAPI application.
socket_app = socketio.ASGIApp(
    sio,
    # socketio_path='sockets' # Optional: if you want to customize the path for Socket.IO connections
)

# Basic event handlers will be defined here later in the subtask.
# For now, this sets up the server instance and ASGI app.

# Example of how event handlers will look (to be filled in later):
# @sio.event
# async def connect(sid, environ):
#     print(f"Socket connected: {sid}")
#     # Authentication logic can go here
#     # user_id = await authenticate_user_ws(environ)
#     # if not user_id:
#     #     raise socketio.exceptions.ConnectionRefusedError('Authentication failed')
#     # await sio.save_session(sid, {'user_id': user_id})

# @sio.event
# async def disconnect(sid):
#     print(f"Socket disconnected: {sid}")
#     # Clean up user session or rooms if necessary
#     # session = await sio.get_session(sid)
#     # if session.get('room'):
#     #     sio.leave_room(sid, session['room'])


# @sio.on("my_custom_event")
# async def handle_my_custom_event(sid, data):
#     print(f"Received event 'my_custom_event' from {sid} with data: {data}")
#     await sio.emit("response_event", {"status": "ok"}, room=sid) # Send response to client


# --- Basic Connection and Disconnection Handlers ---
@sio.event
async def connect(sid, environ):
    """
    Called when a new client connects to the Socket.IO server.
    `environ` contains the WSGI environment, including headers, which can be used for authentication.
    """
    print(f"Socket connected: {sid}")
    # TODO: Implement user authentication based on token in environ (e.g., from query string or headers)
    # Example: token = environ.get('HTTP_AUTHORIZATION', '').split(' ')[-1] if using Bearer token in header
    # user = await get_user_from_token(token) # Your function to validate token and get user
    # if not user:
    #     print(f"Authentication failed for SID: {sid}. Disconnecting.")
    #     raise socketio.exceptions.ConnectionRefusedError('Authentication failed')
    # await sio.save_session(sid, {'user_id': user.id, 'username': user.email}) # Save user info to session
    # print(f"User {user.email} authenticated for SID {sid}")


@sio.event
async def disconnect(sid):
    """
    Called when a client disconnects from the Socket.IO server.
    """
    print(f"Socket disconnected: {sid}")
    # session = await sio.get_session(sid)
    # if session:
    #     field_id = session.get("field_id_room") # Assuming we store the room in session
    #     if field_id:
    #         # Notify others in the room that this user left
    #         await sio.emit("user_left", {"sid": sid, "user_id": session.get('user_id')}, room=f"field_{field_id}")
    #         print(f"User {session.get('user_id')} left room field_{field_id}")
    # await sio.disconnect(sid) # Ensure disconnect is called if not automatically handled


# --- Custom Event Handlers ---

@sio.on("join_field_room")
async def handle_join_field_room(sid, data):
    """
    Allows a client to join a room specific to a field_id.
    `data` should be a dictionary, e.g., {"field_id": 123}
    """
    if not isinstance(data, dict):
        print(f"Invalid data format for join_field_room from {sid}. Expected dict.")
        return

    field_id = data.get("field_id")
    if field_id:
        room_name = f"field_{field_id}"
        sio.enter_room(sid, room_name)
        print(f"Socket {sid} joined room {room_name}")

        # Store the current room in the user's session for later use (e.g., on disconnect)
        # session = await sio.get_session(sid)
        # session["field_id_room"] = field_id
        # await sio.save_session(sid, session)

        # Emit a message to the client that they've successfully joined
        await sio.emit("joined_room_ack", {"room": room_name, "status": "success"}, room=sid)
        # Notify others in the room
        await sio.emit("user_joined", {"sid": sid, "field_id": field_id}, room=room_name, skip_sid=sid)
    else:
        print(f"No field_id provided by {sid} for join_field_room.")
        await sio.emit("join_room_error", {"message": "field_id is required"}, room=sid)


@sio.on("leave_field_room")
async def handle_leave_field_room(sid, data):
    """
    Allows a client to leave a field-specific room.
    `data` should be a dictionary, e.g., {"field_id": 123}
    """
    if not isinstance(data, dict):
        print(f"Invalid data format for leave_field_room from {sid}. Expected dict.")
        return

    field_id = data.get("field_id")
    if field_id:
        room_name = f"field_{field_id}"
        sio.leave_room(sid, room_name)
        print(f"Socket {sid} left room {room_name}")

        # session = await sio.get_session(sid)
        # if session.get("field_id_room") == field_id:
        #     del session["field_id_room"] # Remove from session
        #     await sio.save_session(sid, session)

        await sio.emit("left_room_ack", {"room": room_name, "status": "success"}, room=sid)
        await sio.emit("user_left", {"sid": sid, "field_id": field_id}, room=room_name, skip_sid=sid)
    else:
        print(f"No field_id provided by {sid} for leave_field_room.")
        await sio.emit("leave_room_error", {"message": "field_id is required"}, room=sid)


@sio.on("update_location")
async def handle_update_location(sid, data):
    """
    Handles GPS location updates from a client.
    `data` might contain {'field_id': ..., 'latitude': ..., 'longitude': ..., 'timestamp': ...}
    """
    if not isinstance(data, dict):
        print(f"Invalid data format for update_location from {sid}. Expected dict.")
        return

    print(f"Location update from {sid}: {data}")

    # TODO: Validate data structure (latitude, longitude, field_id exist)
    # TODO: Authenticate if user (from sid session) is allowed to send updates for this field_id.
    # session = await sio.get_session(sid)
    # user_id = session.get('user_id')
    # if not user_id or not await can_user_update_field(user_id, data.get("field_id")):
    #     print(f"User {user_id} not authorized for field {data.get('field_id')}. Location update from {sid} rejected.")
    #     await sio.emit("location_update_error", {"message": "Not authorized or invalid field"}, room=sid)
    #     return

    field_id = data.get("field_id")
    if field_id:
        room_name = f"field_{field_id}"
        # Broadcast to other users in the same "room" (e.g., a room per field_id)
        # The client sending the update typically doesn't need to receive it back.
        await sio.emit("location_broadcast", data, room=room_name, skip_sid=sid)
        print(f"Location data from {sid} broadcasted to room {room_name}")
    else:
        print(f"No field_id provided in location update from {sid}.")
        await sio.emit("location_update_error", {"message": "field_id is required in location data"}, room=sid)
