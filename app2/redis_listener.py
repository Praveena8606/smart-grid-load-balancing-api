import os
import json
import asyncio
import redis

from app.websocket_manager import manager


# ==========================================
# Redis Connection
# ==========================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
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

            if message:

                data = json.loads(message["data"])

                channel = message["channel"]

                if channel == "grid_updates":

                    await manager.broadcast_grid(data)

                elif channel == "forecast_updates":

                    await manager.broadcast_forecast(data)

        except Exception as e:

            print("Redis Listener Error:", e)

        await asyncio.sleep(0.1)