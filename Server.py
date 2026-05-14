import hashlib
import os
import subprocess
import json

from flask import Flask, request, jsonify, render_template
from web3 import Web3
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# =========================
# INIT
# =========================

load_dotenv()

app = Flask(__name__)

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["iot_system"]
collection = db["sensor_data"]

# =========================
# BLOCKCHAIN
# =========================

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# =========================
# LOAD CONTRACT ADDRESSES
# =========================

with open("Blockchain/addresses.json") as f:

    addresses = json.load(f)

contract_address = addresses["iotdata"]

verifier_address = addresses["verifier"]

print("\n===== CONTRACT ADDRESSES =====")

print("IoTData Contract:")
print(contract_address)

print("\nVerifier Contract:")
print(verifier_address)

print("==============================\n")

with open("Blockchain/artifacts/contracts/IoTData.sol/IoTData.json") as f:
    iot_json = json.load(f)

abi = iot_json["abi"]

account = w3.eth.accounts[0]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# =========================
# VERIFIER CONTRACT
# =========================

with open("Blockchain/artifacts/contracts/Verifier.sol/Groth16Verifier.json") as f:
    verifier_json = json.load(f)

verifier_abi = verifier_json["abi"]

verifier_contract = w3.eth.contract(
    address=verifier_address,
    abi=verifier_abi
)

print("✅ Verifier Connected")

# =========================
# FUNCTIONS
# =========================

def hash_data(data):
    return hashlib.sha256(str(data).encode()).hexdigest()

# =========================
# ZKP FUNCTION
# =========================

def generate_zkp(temp_value):

    try:

        # demo circuit: data² = hash
        data_val = int(temp_value)
        hash_val = data_val * data_val

        input_data = {
            "data": data_val,
            "hash": hash_val
        }

        with open("ZKP/input.json", "w") as f:
            json.dump(input_data, f)

        # Generate Witness
        subprocess.run([
            "node",
            "ZKP/HashCheck_js/generate_witness.js",
            "ZKP/HashCheck_js/HashCheck.wasm",
            "ZKP/input.json",
            "ZKP/witness.wtns"
        ], check=True)

        # Generate Proof
        subprocess.run([
            r"C:\Users\Zhen Xuan\AppData\Roaming\npm\snarkjs.cmd",
            "groth16",
            "prove",
            "ZKP/circuit_final.zkey",
            "ZKP/witness.wtns",
            "ZKP/proof.json",
            "ZKP/public.json"
        ], check=True)

        # Load Proof
        with open("ZKP/proof.json") as f:
            proof = json.load(f)

        with open("ZKP/public.json") as f:
            public = json.load(f)

        return proof, public

    except Exception as e:

        print("❌ ZKP ERROR:", e)

        return None, None

# =========================
# ROUTES
# =========================

@app.route("/data", methods=["POST"])
def receive_data():

    data = request.json

    # =========================
    # HASHING
    # =========================

    data_hash = hash_data(data)

    # =========================
    # ZKP GENERATION
    # =========================

    proof, public = generate_zkp(data["temperature"])

    # =========================
    # BLOCKCHAIN ZKP VERIFY
    # =========================

    verified = False

    if proof:

        try:

            # =========================
            # CONVERT PROOF TO UINT256
            # =========================

            pi_a = [
                int(proof["pi_a"][0]),
                int(proof["pi_a"][1])
            ]

            pi_b = [
                [
                    int(proof["pi_b"][0][1]),
                    int(proof["pi_b"][0][0])
                ],
                [
                    int(proof["pi_b"][1][1]),
                    int(proof["pi_b"][1][0])
                ]
            ]

            pi_c = [
                int(proof["pi_c"][0]),
                int(proof["pi_c"][1])
            ]

            public_signals = [
                int(x) for x in public
            ]

            # =========================
            # VERIFY PROOF
            # =========================

            verified = verifier_contract.functions.verifyProof(
                pi_a,
                pi_b,
                pi_c,
                public_signals
            ).call()

        except Exception as e:

            print("❌ VERIFY ERROR:", e)

    # =========================
    # ONLY VERIFIED DATA ALLOWED
    # =========================

    if verified:

        try:

            # =========================
            # STORE ON BLOCKCHAIN
            # =========================

            tx = contract.functions.storeData(
                data["device_id"],
                data["timestamp"],
                int(data["temperature"]),
                data_hash,
                json.dumps(proof)
            ).transact({"from": account})

            receipt = w3.eth.wait_for_transaction_receipt(tx)

            print("✅ Stored on Blockchain")

            # =========================
            # STORE IN MONGODB
            # =========================

            collection.insert_one({

                "device_id": data["device_id"],
                "timestamp": data["timestamp"],
                "temperature": data["temperature"],
                "hash": data_hash,
                "zkp_verified": verified,
                "zkp_proof": proof,
                "public_signals": public

            })

            print("✅ Stored in MongoDB")

            # =========================
            # OUTPUT
            # =========================

            print("\n" + "="*60)

            print("📡 VERIFIED IoT DATA RECEIVED")

            print("="*60)

            print(f"Device ID           : {data['device_id']}")
            print(f"Time                : {data['timestamp']}")
            print(f"Temperature         : {data['temperature']}°C")

            print("\n🔐 HASH")
            print(f"SHA-256             : {data_hash}")

            print("\n🧠 ZKP")
            print(f"Proof Generated     : {'YES' if proof else 'NO'}")
            print(f"Proof Verified      : {verified}")

            print("\n⛓ BLOCKCHAIN")
            print(f"Tx Hash             : {tx.hex()}")
            print(f"Block Number        : {receipt.blockNumber}")

            print("\n🗄 DATABASE")
            print("Stored in MongoDB")

            print("="*60 + "\n")

            return jsonify({
                "status": "stored",
                "zkp_verified": verified
            })

        except Exception as e:

            print("❌ BLOCKCHAIN ERROR:", e)

            return jsonify({
                "status": "blockchain_failed",
                "zkp_verified": False
            })

    else:

        # =========================
        # ALERT ATTACK
        # =========================

        print("\n" + "="*60)

        print("🚨 ALERT ATTACK DETECTED")

        print("="*60)

        print(f"Device ID           : {data['device_id']}")
        print(f"Time                : {data['timestamp']}")
        print(f"Temperature         : {data['temperature']}°C")

        print("\n❌ INVALID ZKP PROOF")

        print("⛔ Data Rejected")
        print("⛔ Not Stored in Blockchain")
        print("⛔ Not Stored in MongoDB")
        print("⛔ Not Displayed in Dashboard")

        print("="*60 + "\n")

        return jsonify({
            "status": "rejected",
            "zkp_verified": False
        })

# =========================
# DIGITAL TWIN
# =========================

@app.route("/DigitalTwin")
def DigitalTwin():

    # =========================
    # GET DATA FROM MONGODB
    # =========================

    data = list(collection.find().sort("_id", -1).limit(50))

    # =========================
    # TEMPERATURE + TIMESTAMP
    # =========================

    temperatures = [d.get("temperature", 0) for d in data]

    timestamps = [d.get("timestamp", "") for d in data]

    sensor_names = [d.get("device_id", "Unknown") for d in data]

    latest_temp = (
        data[0].get("temperature", "No Data")
        if data else "No Data"
    )

    # =========================
    # GET DATA FROM BLOCKCHAIN
    # =========================

    blockchain_hashes = {}
    try:
        data_count = contract.functions.getDataCount().call()
        start_index = max(0, data_count - 50)
        for i in range(start_index, data_count):
            bc_device_id, bc_timestamp, bc_temp, bc_hash, bc_proof = contract.functions.getData(i).call()
            blockchain_hashes[f"{bc_device_id}_{bc_timestamp}"] = bc_hash
    except Exception as e:
        print("❌ FAILED TO FETCH BLOCKCHAIN DATA:", e)

    # =========================
    # CROSS-VERIFICATION (BLOCKCHAIN VS DB)
    # =========================

    integrity_status = []
    tampered_data = []

    for d in data:

        device_id = d.get("device_id")
        timestamp = d.get("timestamp")

        # Get the corresponding hash stored on the blockchain
        blockchain_hash = blockchain_hashes.get(f"{device_id}_{timestamp}")

        # Recalculate hash from database data
        recalculated_hash = hashlib.sha256(

            str({
                "device_id": device_id,
                "timestamp": timestamp,
                "temperature": d.get("temperature")
            }).encode()

        ).hexdigest()

        # Compare hash
        if blockchain_hash and blockchain_hash == recalculated_hash:

            integrity_status.append("VALID ✅")

        else:

            integrity_status.append("TAMPERED ❌")
            tampered_data.append({
                "sensor": device_id,
                "timestamp": timestamp,
                "temperature": d.get("temperature")
            })

    # Latest integrity status
    latest_integrity = (
        integrity_status[0]
        if integrity_status else "UNKNOWN"
    )

    # =========================
    # SENSOR STATUS CHECK
    # =========================

    sensor_status = "OFFLINE ❌"

    if data:

        latest_timestamp = data[0].get("timestamp")

        try:

            latest_time = datetime.fromisoformat(
                latest_timestamp
            )

            current_time = datetime.now()

            time_difference = (
                current_time - latest_time
            ).total_seconds()

            # 如果 15 秒内有新数据
            if time_difference <= 15:

                sensor_status = "ONLINE ✅"

        except:

            sensor_status = "ERROR ⚠"

    # =========================
    # TEMPERATURE ALERT
    # =========================

    temperature_alert = "NORMAL ✅"

    if data:

        try:

            current_temperature = float(
                data[0].get("temperature", 0)
            )

            # High temperature
            if current_temperature >= 75:

                temperature_alert = "HIGH TEMPERATURE 🚨"

            # Low temperature
            elif current_temperature < 30:

                temperature_alert = "LOW TEMPERATURE ❄"

            # Normal temperature
            else:

                temperature_alert = "NORMAL ✅"

        except:

            temperature_alert = "SENSOR ERROR ⚠"

    return render_template(

        "DigitalTwin.html",

        temperatures=temperatures,
        timestamps=timestamps,
        latest_temp=latest_temp,
        integrity_status=latest_integrity,
        sensor_status=sensor_status,
        temperature_alert=temperature_alert,
        integrity_list=integrity_status,
        sensor_names=sensor_names,
        tampered_data=tampered_data,

    )

# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":

    print("\n🚀 Starting Server with ZKP Verification...\n")

    app.run(debug=True)