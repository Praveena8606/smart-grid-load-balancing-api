import json
import asyncio
import redis

from app.websocket_manager import manager


# Redis Connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# Pub/Sub
pubsub = redis_client.pubsub()

pubsub.subscribe(
    "grid_updates",
    "forecast_updates"
)


async def redis_listener():

    print("Redis Listener Started...")

    while True:

        message = pubsub.get_message(ignore_subscribe_messages=True)

        if message:

            try:

                data = json.loads(message["data"])

                if message["channel"] == "grid_updates":

                    await manager.broadcast_grid(data)

                elif message["channel"] == "forecast_updates":

                    await manager.broadcast_forecast(data)

            except Exception as e:

                print("Redis Listener Error :", e)

        await asyncio.sleep(0.1)