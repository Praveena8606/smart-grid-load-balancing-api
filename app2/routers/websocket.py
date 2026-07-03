import asyncio

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.websocket_manager import manager

router = APIRouter()


# =====================================================
# GRID SOCKET
# =====================================================

@router.websocket("/ws/grid")
async def grid_socket(websocket: WebSocket):

    await manager.connect_grid(websocket)

    print("GRID Connected")

    try:
        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:

        manager.disconnect_grid(websocket)

        print("GRID Disconnected")


# =====================================================
# FORECAST SOCKET
# =====================================================

@router.websocket("/ws/forecast")
async def forecast_socket(websocket: WebSocket):

    await manager.connect_forecast(websocket)

    print("FORECAST WebSocket Connected")

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect_forecast(websocket)

        print("FORECAST WebSocket Disconnected")

       