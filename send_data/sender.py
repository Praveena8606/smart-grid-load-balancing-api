import requests
import random
import time
from datetime import datetime

HEALTH_URL = "http://fastapi:8000/health"
POST_URL = "http://fastapi:8000/zone-load/"

# ----------------------------------------
# Wait until FastAPI is ready
# ----------------------------------------

while True:
    try:
        response = requests.get(HEALTH_URL, timeout=5)

        if response.status_code == 200:
            print("✅ FastAPI is ready")
            break

    except Exception as e:
        print("Waiting for FastAPI...", e)

    time.sleep(5)

# ----------------------------------------
# Send Data Forever
# ----------------------------------------

while True:

    print("Sending 300 records...")

    for zone_no in range(1, 11):

        zone_id = f"ZONE_{zone_no:02d}"

        for house_no in range(1, 31):

            house_id = f"HOUSE_{house_no:03d}"

            payload = {
                "zone_id": zone_id,
                "house_id": house_id,
                "avg_power_kw": round(random.uniform(2, 6.5), 2),
                "avg_voltage": round(random.uniform(220, 240), 2),
                "avg_current": round(random.uniform(1, 5), 2),
                "record_time": datetime.utcnow().isoformat()
            }

            try:

                response = requests.post(
                    POST_URL,
                    json=payload,
                    timeout=10
                )

                print(
                    f"{zone_id} | {house_id} | Status={response.status_code}"
                )

            except Exception as e:

                print("POST Error:", e)

    print("300 records sent successfully")
    print("Waiting 5 seconds...\n")

    time.sleep(5)