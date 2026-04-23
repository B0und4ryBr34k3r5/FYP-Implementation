import hashlib
import os
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from pymongo import MongoClient
from dotenv import load_dotenv

# =========================
# INIT
# =========================

load_dotenv()

app = Flask(__name__)

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["iot_system"]
collection = db["sensor_data"]

# Blockchain
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
# FUNCTIONS
# =========================

def hash_data(data):
    return hashlib.sha256(str(data).encode()).hexdigest()

# =========================
# ROUTES
# =========================

@app.route("/data", methods=["POST"])
def receive_data():
    data = request.json

    # Hash
    data_hash = hash_data(data)

    # MongoDB
    collection.insert_one({
        "device_id": data["device_id"],
        "timestamp": data["timestamp"],
        "temperature": data["temperature"],
        "hash": data_hash
    })

    # Blockchain
    tx = contract.functions.storeData(
        data["device_id"],
        data["timestamp"],
        int(data["temperature"])
    ).transact({"from": account})

    receipt = w3.eth.wait_for_transaction_receipt(tx)

    # OUTPUT
    print("\n" + "="*50)
    print("DATA RECEIVED FROM IoT")
    print("="*50)
    print(f"Device ID           : {data['device_id']}")
    print(f"Time                : {data['timestamp']}")
    print(f"Temp                : {data['temperature']}°C")
    print(f"Data Hash (SHA-256) : {data_hash}")
    print(f"Tx Hash             : {tx.hex()}")
    print(f"Block No            : {receipt.blockNumber}")
    print("="*50)
    print("Stored in MongoDB")
    print("Stored in Blockchain")
    print("="*50 + "\n")

    return jsonify({"status": "stored"})

@app.route("/DigitalTwin")
def DigitalTwin():
    data = list(collection.find().sort("_id", -1).limit(50))

    temperatures = [d.get("temperature", 0) for d in data][::-1]
    timestamps = [d.get("timestamp", "") for d in data][::-1]
    latest_temp = data[0].get("temperature", "No Data") if data else "No Data"

    return render_template(
        "DigitalTwin.html",
        temperatures=temperatures,
        timestamps=timestamps,
        latest_temp=latest_temp
    )

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    print("\n\nStarting Server...\n")
    app.run(debug=True)