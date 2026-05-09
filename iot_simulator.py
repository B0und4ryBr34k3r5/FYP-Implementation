import requests
import random
import time
from datetime import datetime

# =========================
# TEMPERATURE SIMULATION
# =========================

current_temp = random.uniform(30, 60)

# Counter
generation_count = 0

def generate_temperature():

    global current_temp
    global generation_count

    generation_count += 1

    # =========================
    # FORCE HIGH TEMPERATURE
    # Every 6th reading
    # =========================

    if generation_count >= 6:

        generation_count = 0

        # Force high temperature
        current_temp = random.uniform(76, 90)

        return round(current_temp, 2)

    # =========================
    # NORMAL TEMPERATURE
    # =========================

    change = random.gauss(0, 8)

    current_temp += change

    current_temp = max(10, min(70, current_temp))

    return round(current_temp, 2)

# =========================
# IOT SIMULATOR LOOP
# =========================

while True:

    data = {

        "device_id": "sensor_001",

        "timestamp": datetime.now().isoformat(),

        "temperature": generate_temperature()

    }

    try:

        requests.post(
            "http://127.0.0.1:5000/data",
            json=data
        )

        print(
            f"📡 Sent Temperature: {data['temperature']}°C"
        )

    except Exception as e:

        print("❌ Error:", e)

    time.sleep(5)