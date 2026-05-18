import requests
import time
from datetime import datetime

def simulate_replay_attack():
    """
    REPLAY ATTACK SIMULATION
    
    Attack Vector: An attacker intercepts a legitimate data transmission 
    between an IoT sensor and the server, then re-sends the exact same 
    data packet multiple times.
    
    What this tests: Whether the system can detect and reject 
    duplicate/replayed data submissions.
    """
    print("==================================================")
    print("🔁 REPLAY ATTACKER INITIALIZED 🔁")
    print("==================================================")
    print("[*] Simulating interception of a legitimate IoT transmission...")
    print("[*] Capturing a valid data packet...\n")

    # STEP 1: Send a legitimate data packet (simulating a real sensor)
    legitimate_data = {
        "device_id": "sensor_001",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperature": 45.0
    }

    print(f"[*] Original Packet Captured:")
    print(f"    Device ID    : {legitimate_data['device_id']}")
    print(f"    Timestamp    : {legitimate_data['timestamp']}")
    print(f"    Temperature  : {legitimate_data['temperature']}°C")

    try:
        response = requests.post(
            "http://127.0.0.1:5000/data",
            json=legitimate_data
        )
        print(f"\n[*] Original transmission result: {response.json()}")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        return

    # STEP 2: Replay the EXACT same packet multiple times
    print("\n" + "-"*50)
    print("[!] LAUNCHING REPLAY ATTACK...")
    print("[!] Re-transmitting the captured packet 3 times...\n")

    for i in range(1, 4):

        print(f"[REPLAY #{i}] Sending captured packet...")

        time.sleep(2)

        try:
            response = requests.post(
                "http://127.0.0.1:5000/data",
                json=legitimate_data
            )
            result = response.json()
            status = result.get("status")

            if status == "stored":
                print(f"[REPLAY #{i}] ⚠️  ACCEPTED — The system stored the replayed data!")
            elif status == "rejected":
                print(f"[REPLAY #{i}] ✅ REJECTED — The system detected the replay!")
            else:
                print(f"[REPLAY #{i}] Result: {result}")

        except Exception as e:
            print(f"[REPLAY #{i}] Error: {e}")

    # SUMMARY
    print("\n" + "="*50)
    print("REPLAY ATTACK SUMMARY")
    print("="*50)
    print("If the system ACCEPTED the replayed packets:")
    print("  → The system is vulnerable to replay attacks.")
    print("  → Duplicate data was stored in Blockchain & MongoDB.")
    print("  → A nonce or timestamp-based deduplication is needed.\n")
    print("If the system REJECTED the replayed packets:")
    print("  → The system successfully defended against replay attacks.")
    print("="*50)

if __name__ == "__main__":
    simulate_replay_attack()
