import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.ws_manager import ws_manager
from app.crud.session_crud import get_ctv_session_by_id
from app.db import engine

from sqlmodel import Session as DBSession

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/ctv/{session_id}")
async def ctv_websocket(websocket: WebSocket, session_id: uuid.UUID):
    """WebSocket endpoint for CTV ad creatives.

    The CTV connects after registering a session and stays connected
    to receive real-time interaction events from paired smartphones.
    """
    # Validate session exists (short-lived DB session, not held open for WS lifetime)
    with DBSession(engine) as db:
        ctv_session = get_ctv_session_by_id(session_id, db)
        if not ctv_session:
            await websocket.close(code=4004, reason="Session not found")
            return

    await ws_manager.connect(str(session_id), websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")
            if event == "heartbeat":
                await websocket.send_json({"event": "heartbeat_ack"})
    except WebSocketDisconnect:
        ws_manager.disconnect(str(session_id))
