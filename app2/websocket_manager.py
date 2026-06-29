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

    def disconnect_grid(self, websocket: WebSocket):

        if websocket in self.grid_connections:

            self.grid_connections.remove(websocket)

    async def broadcast_grid(self, message: dict):

        disconnected = []

        for connection in self.grid_connections:

            try:

                await connection.send_json(message)

            except Exception:

                disconnected.append(connection)

        for ws in disconnected:

            self.disconnect_grid(ws)

    # =====================================================
    # FORECAST
    # =====================================================

    async def connect_forecast(self, websocket: WebSocket):

        await websocket.accept()

        self.forecast_connections.append(websocket)

    def disconnect_forecast(self, websocket: WebSocket):

        if websocket in self.forecast_connections:

            self.forecast_connections.remove(websocket)

    async def broadcast_forecast(self, message: dict):

        disconnected = []

        for connection in self.forecast_connections:

            try:

                await connection.send_json(message)

            except Exception:

                disconnected.append(connection)

        for ws in disconnected:

            self.disconnect_forecast(ws)


manager = ConnectionManager()