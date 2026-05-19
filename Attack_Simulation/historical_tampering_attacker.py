import os
import random
from pymongo import MongoClient
from dotenv import load_dotenv

def simulate_historical_tampering_attack():
    """
    HISTORICAL DATA TAMPERING ATTACK SIMULATION

    Attack Vector: An attacker gains direct access to the MongoDB database
    and tampers with an OLDER record (not the latest), attempting to modify 
    historical sensor data without detection. The targeted record is within 
    the latest 50 entries, which is the range displayed by the Digital Twin.

    What this tests: Whether the system's cross-verification mechanism can 
    detect tampering on non-latest (historical) records, not just the most 
    recent one. This validates that the blockchain integrity check covers 
    ALL records in the dashboard window, not only the newest entry.
    """
    print("==================================================")
    print("HISTORICAL DATA TAMPERING ATTACKER INITIALIZED")
    print("==================================================")
    print("[*] Bypassing Server API...")
    print("[*] Connecting directly to MongoDB database...")

    try:
        # Load .env from the project root (one level up from Attack_Simulation/)
        project_root = os.path.join(os.path.dirname(__file__), "..")
        load_dotenv(os.path.join(project_root, ".env"))
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri)
        db = client["iot_system"]
        collection = db["sensor_data"]

        print("[*] Connection successful.")
        print("[*] Fetching latest 30 sensor records...")

        # Get the latest 30 records (within the Digital Twin dashboard display range)
        recent_docs = list(collection.find().sort("_id", -1).limit(30))

        if len(recent_docs) < 3:
            print("[!] Not enough data in the database (need at least 3 records).")
            print("[!] Start the iot_simulator.py and wait for some data first!")
            return

        # Pick a random record that is NOT the latest one
        # Skip index 0 (latest), pick from index 2 onwards for a clearly "older" record
        target_index = random.randint(2, len(recent_docs) - 1)
        target_doc = recent_docs[target_index]

        original_temp = target_doc.get("temperature")
        device_id = target_doc.get("device_id")
        timestamp = target_doc.get("timestamp")

        print(f"\n[*] Total records available: {len(recent_docs)}")
        print(f"[*] Targeting record #{target_index + 1} (from newest)")
        print(f"[*] Target Device: {device_id}")
        print(f"[*] Target Timestamp: {timestamp}")
        print(f"[*] Original Temperature: {original_temp}°C")

        # Malicious modification — inject an obviously fake temperature
        fake_temp = 369.66
        print(f"\n[!] INJECTING MALICIOUS PAYLOAD INTO HISTORICAL RECORD...")
        print(f"[!] Changing temperature from {original_temp}°C to {fake_temp}°C...")

        # Update the document in MongoDB without updating the hash!
        # The blockchain still holds the original hash, so cross-verification should detect this.
        collection.update_one(
            {"_id": target_doc["_id"]},
            {"$set": {"temperature": fake_temp}}
        )

        print(f"\n[✓] ATTACK SUCCESSFUL!")
        print(f"[✓] Historical record #{target_index + 1} has been silently modified.")
        print(f"\n[*] Attack Summary:")
        print(f"    Record Position  : #{target_index + 1} of {len(recent_docs)} (from newest)")
        print(f"    Device ID        : {device_id}")
        print(f"    Timestamp        : {timestamp}")
        print(f"    Original Temp    : {original_temp}°C")
        print(f"    Tampered Temp    : {fake_temp}°C")
        print(f"\n[*] Check your Digital Twin Dashboard.")
        print(f"[*] The cross-verification should detect this historical tampering!")
        print("==================================================")

    except Exception as e:
        print(f"[!] Failed to execute attack: {e}")

if __name__ == "__main__":
    simulate_historical_tampering_attack()
