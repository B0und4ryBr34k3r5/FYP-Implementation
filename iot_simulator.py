import threading
import requests
import random
import time
from datetime import datetime
from flask import Flask, request, jsonify
import hashlib

# =========================
# SERVER PART
# =========================

app = Flask(__name__)
database = []

def hash_data(data):
    data_string = str(data)
    return hashlib.sha256(data_string.encode()).hexdigest()

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json
    data_hash = hash_data(data)

    record = {
        "data": data,
        "hash": data_hash
    }

    database.append(record)

    # ===== 美化输出 =====
    print("\n" + "="*40)
    print("IoT Sending Data")
    print("="*40)

    print(f"Device ID : {data['device_id']}")
    print(f"Time      : {data['timestamp']}")
    print(f"Temp      : {data['temperature']}°C")

    print("\nHASH GENERATED")
    print(f"{data_hash}")

    print("="*40 + "\n")

    return jsonify({
        "status": "stored",
        "hash": data_hash
    })


def run_server():
    app.run(debug=False, use_reloader=False)


# =========================
# IoT SIMULATOR PART
# =========================

current_temp = random.uniform(24, 28)

def generate_temperature():
    global current_temp
    change = random.gauss(0, 0.3)
    current_temp += change
    current_temp = max(15, min(40, current_temp))
    return round(current_temp, 2)


def generate_sensor_data():
    return {
        "device_id": "sensor_001",
        "timestamp": datetime.now().isoformat(),
        "temperature": generate_temperature()
    }


def run_simulator():
    time.sleep(2)  # 等 server 启动

    while True:
        data = generate_sensor_data()

        try:
            response = requests.post("http://127.0.0.1:5000/data", json=data)
            res = response.json()

            # ===== 美化输出 =====
            print("\n" + "="*40)
            print("Server Received Data")
            print("="*40)

            print(f"Device ID : {data['device_id']}")
            print(f"Time      : {data['timestamp']}")
            print(f"Temp      : {data['temperature']}°C")

            print("\n🔁 SERVER RESPONSE")
            print(f"Status    : {res['status']}")
            print(f"Hash      : {res['hash']}")

            print("="*40 + "\n")

        except Exception as e:
            print("\n❌ ERROR:", e)

        time.sleep(3)


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("\n Starting IoT System...\n")

    # 启动 server（后台）
    try:
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        print("✅ Server started at http://127.0.0.1:5000\n")

    # 启动 simulator
        run_simulator()
    
    except KeyboardInterrupt:
        print("\nSystem stopped by user\n")