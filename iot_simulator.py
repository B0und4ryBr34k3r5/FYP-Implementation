import requests
import random
import time
from datetime import datetime

current_temp = random.uniform(24, 28)

def generate_temperature():
    global current_temp
    change = random.gauss(0, 0.3)
    current_temp += change
    current_temp = max(15, min(40, current_temp))
    return round(current_temp, 2)

while True:
    data = {
        "device_id": "sensor_001",
        "timestamp": datetime.now().isoformat(),
        "temperature": generate_temperature()
    }

    try:
        requests.post("http://127.0.0.1:5000/data", json=data)
        print(f"Sent: {data['temperature']}°C")
    except Exception as e:
        print("Error:", e)

    time.sleep(5)