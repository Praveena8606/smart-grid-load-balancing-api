from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.grid_connections = []
        self.forecast_connections = []

    # =====================================================
    # GRID
    # =====================================================

    async def connect_grid(self, websocket: WebSocket):
        await websocket.accept()
        self.grid_connections.append(websocket)

        print(f"Grid Client Connected | Total = {len(self.grid_connections)}")

    def disconnect_grid(self, websocket: WebSocket):
        if websocket in self.grid_connections:
            self.grid_connections.remove(websocket)

        print(f"Grid Client Disconnected | Total = {len(self.grid_connections)}")

    async def broadcast_grid(self, message: dict):

        print("=" * 60)
        print(f"Connections : {len(self.grid_connections)}")
        print(f"Broadcasting: {message}")

        disconnected = []

        for ws in self.grid_connections:
            try:
                await ws.send_json(message)
                print("Message sent successfully")

            except Exception as e:
                print(f"WebSocket Send Error: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect_grid(ws)

        print("=" * 60)

    # =====================================================
    # FORECAST
    # =====================================================

    async def connect_forecast(self, websocket: WebSocket):
        await websocket.accept()
        self.forecast_connections.append(websocket)

        print(
            f"Forecast Client Connected | Total = {len(self.forecast_connections)}"
        )

    def disconnect_forecast(self, websocket: WebSocket):
        if websocket in self.forecast_connections:
            self.forecast_connections.remove(websocket)

        print(
            f"Forecast Client Disconnected | Total = {len(self.forecast_connections)}"
        )

    async def broadcast_forecast(self, message: dict):

        print(f"Forecast Broadcast -> {message}")

        disconnected = []

        for ws in self.forecast_connections:
            try:
                await ws.send_json(message)

            except Exception as e:
                print(f"Forecast Send Error: {e}")
                disconnected.append(ws)

        for ws in disconnected:
            self.disconnect_forecast(ws)


manager = ConnectionManager()