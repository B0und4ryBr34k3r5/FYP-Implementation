import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv

def simulate_database_attack():
    """
    DATABASE TAMPERING ATTACK SIMULATION

    Attack Vector: An attacker gains direct access to the MongoDB database 
    (e.g., through a stolen connection string or insider threat) and modifies 
    stored sensor records directly, bypassing the API and all security checks.

    What this tests: Whether the system's cross-verification mechanism 
    (comparing DB hash vs Blockchain hash) can detect post-storage tampering.
    """
    print("==================================================")
    print("DATABASE TAMPERING ATTACKER INITIALIZED")
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
        print("[*] Searching for the most recent sensor reading...")
        
        # Get the most recent document
        latest_doc = collection.find_one(sort=[("_id", -1)])
        
        if not latest_doc:
            print("No data found in the database. Start the iot_simulator.py first!")
            return
            
        original_temp = latest_doc.get("temperature")
        device_id = latest_doc.get("device_id")
        timestamp = latest_doc.get("timestamp")
        
        print(f"[*] Found Target Data: {device_id} at {timestamp}")
        print(f"[*] Original Temperature: {original_temp}°C")
        
        # Malicious modification
        fake_temp = 253.99
        print(f"\n[!] INJECTING MALICIOUS PAYLOAD...")
        print(f"[!] Changing temperature to {fake_temp}°C...")
        
        # Update the document in MongoDB without updating the hash!
        # This is the crux of the attack: modifying data in DB without reflecting it 
        # in the immutable blockchain record. The cross-verification logic should catch this.
        collection.update_one(
            {"_id": latest_doc["_id"]},
            {"$set": {"temperature": fake_temp}}
        )
        
        print("\nATTACK SUCCESSFUL!")
        print("The database has been silently modified.")
        print("Check your Digital Twin Dashboard. The cross-verification should detect this anomaly immediately!")
        print("==================================================")
        
    except Exception as e:
        print(f"Failed to execute attack: {e}")

if __name__ == "__main__":
    simulate_database_attack()
