import os
import json
import asyncio
import redis

from app.websocket_manager import manager

# ==========================================
# Redis Connection
# ==========================================

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

# ==========================================
# Subscribe Channels
# ==========================================

pubsub = redis_client.pubsub()

pubsub.subscribe(
    "grid_updates",
    "forecast_updates"
)

print("Subscribed to Redis Channels")


# ==========================================
# Redis Listener
# ==========================================

async def redis_listener():

    print("Redis Listener Started...")

    while True:

        try:

            message = pubsub.get_message(
                ignore_subscribe_messages=True
            )

            if message is None:
                await asyncio.sleep(0.1)
                continue

            print("=" * 60)
            print("MESSAGE RECEIVED FROM REDIS")
            print(message)

            data = json.loads(message["data"])

            print("CHANNEL :", message["channel"])
            print("DATA    :", data)

            if message["channel"] == "grid_updates":

                print("Broadcasting Grid Update...")

                await manager.broadcast_grid(data)

            elif message["channel"] == "forecast_updates":

                print("Broadcasting Forecast Update...")

                await manager.broadcast_forecast(data)

        except Exception as e:

            print("Redis Listener Error:", e)

        await asyncio.sleep(0.1)       