import requests
import random
import time
from datetime import datetime

# TEMPERATURE SIMULATION
# Initialize starting temperature with a random value between 30 and 60
current_temp = random.uniform(30, 60)

# Counter
generation_count = 0

def generate_temperature():
    """
    Generates a simulated temperature reading.
    Normally fluctuates slightly using a Gaussian distribution, but 
    periodically forces an anomaly (high temperature) to test the system's alert capabilities.
    """
    global current_temp
    global generation_count

    generation_count += 1

    # FORCE HIGH TEMPERATURE
    # Every 6th reading
    if generation_count >= 6:

        generation_count = 0

        # Force high temperature (Anomaly simulation)
        current_temp = random.uniform(76, 90)

        return round(current_temp, 2)

    # NORMAL TEMPERATURE
    # Use Gaussian (normal) distribution to simulate natural temperature drift
    # mean=0, standard deviation=8
    change = random.gauss(0, 8)

    current_temp += change

    # Clamp the temperature between realistic bounds (10 to 70)
    current_temp = max(10, min(70, current_temp))

    return round(current_temp, 2)

# IOT SIMULATOR LOOP
# Infinite loop to continuously send data to the backend server
while True:

    # Construct the JSON payload representing the sensor reading
    data = {

        "device_id": "sensor_001",

        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "temperature": generate_temperature()

    }

    try:

        requests.post(
            "http://127.0.0.1:5000/data",
            json=data
        )

        print(
            f"Sent Temperature: {data['temperature']}°C"
        )

    except Exception as e:

        print("Error:", e)

    time.sleep(10)