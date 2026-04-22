import threading
import random
import time
import hashlib
import requests
import os
from datetime import datetime
from flask import Flask, request, jsonify
from web3 import Web3
from pymongo import MongoClient
from dotenv import load_dotenv

# =========================
# MONGODB PART
# =========================

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))

db = client["iot_system"]
collection = db["sensor_data"]

# =========================
# BLOCKCHAIN PART
# =========================

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "_deviceId", "type": "string"},
            {"internalType": "string", "name": "_timestamp", "type": "string"},
            {"internalType": "int256", "name": "_temperature", "type": "int256"}
        ],
        "name": "storeData",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

account = w3.eth.accounts[0]
contract = w3.eth.contract(address=contract_address, abi=abi)

# =========================
# FLASK SERVER
# =========================

app = Flask(__name__)

def hash_data(data):
    return hashlib.sha256(str(data).encode()).hexdigest()

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json

    # Step 1: Hashing
    data_hash = hash_data(data)

    # Step 2: Store in MongoDB
    mongo_record = {
        "device_id": data["device_id"],
        "timestamp": data["timestamp"],
        "temperature": data["temperature"],
        "hash": data_hash
    }
    collection.insert_one(mongo_record)

    # Step 3: Store on Blockchain
    tx = contract.functions.storeData(
        data["device_id"],
        data["timestamp"],
        int(data["temperature"])
    ).transact({"from": account})

    receipt = w3.eth.wait_for_transaction_receipt(tx)

    # Output
    print("\n" + "="*50)
    print("📡 DATA RECEIVED FROM IoT")
    print("="*50)

    print(f"Device ID : {data['device_id']}")
    print(f"Temp      : {data['temperature']}°C")

    print("\n🔐 HASH")
    print(data_hash)

    print("\n🗄 Stored in MongoDB")

    print("\n⛓ Stored in Blockchain")
    print(f"Tx Hash   : {tx.hex()}")
    print(f"Block No  : {receipt.blockNumber}")

    print("="*50 + "\n")

    return jsonify({"status": "stored"})

def run_server():
    app.run(debug=False, use_reloader=False)

# =========================
# IoT SIMULATOR
# =========================

current_temp = random.uniform(24, 28)

def generate_temperature():
    global current_temp
    change = random.gauss(0, 0.3)
    current_temp += change
    current_temp = max(15, min(40, current_temp))
    return round(current_temp, 2)

def run_simulator():
    time.sleep(2)

    while True:
        data = {
            "device_id": "sensor_001",
            "timestamp": datetime.now().isoformat(),
            "temperature": generate_temperature()
        }

        try:
            requests.post("http://127.0.0.1:5000/data", json=data)
        except Exception as e:
            print("❌ Error:", e)

        time.sleep(5)

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    print("\n🚀 Starting Full IoT System...\n")

    try:
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        print("✅ Server started at http://127.0.0.1:5000")

        run_simulator()

    except KeyboardInterrupt:
        print("\nSystem stopped\n")