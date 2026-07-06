import asyncio

from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from app.websocket_manager import manager

router = APIRouter()

# ==========================================
# GRID WEBSOCKET
# ==========================================

@router.websocket("/ws/grid")
async def grid_socket(websocket: WebSocket):

    await manager.connect_grid(websocket)

    print("GRID WebSocket Connected")

    try:

        while True:

            # Keep the connection alive
            await asyncio.sleep(1)

    except WebSocketDisconnect:

        manager.disconnect_grid(websocket)

        print("GRID WebSocket Disconnected")

    except Exception as e:

        manager.disconnect_grid(websocket)

        print("GRID Socket Error:", e)


# ==========================================
# FORECAST WEBSOCKET
# ==========================================

@router.websocket("/ws/forecast")
async def forecast_socket(websocket: WebSocket):

    await manager.connect_forecast(websocket)

    print("FORECAST WebSocket Connected")

    try:

        while True:

            await asyncio.sleep(1)

    except WebSocketDisconnect:

        manager.disconnect_forecast(websocket)

        print("FORECAST WebSocket Disconnected")

    except Exception as e:

        manager.disconnect_forecast(websocket)

        print("FORECAST Socket Error:", e)
       