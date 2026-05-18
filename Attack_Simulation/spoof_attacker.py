import requests
import time
from datetime import datetime

def simulate_spoofed_device_attack():
    """
    SPOOFED DEVICE / UNAUTHORIZED DEVICE ATTACK SIMULATION

    Attack Vector: An attacker deploys a rogue IoT device (or software) 
    that impersonates a legitimate sensor or introduces an entirely 
    unauthorized device into the network.

    What this tests: Whether the system validates device identity 
    and rejects data from unregistered/unknown sensors.
    """
    print("==================================================")
    print("👻 SPOOFED DEVICE ATTACKER INITIALIZED 👻")
    print("==================================================")
    print("[*] Deploying rogue IoT devices on the network...")
    print("[*] Attempting to inject data from unauthorized sensors...\n")

    # Define fake devices with malicious intent
    fake_devices = [
        {
            "name": "Impersonated Sensor",
            "data": {
                "device_id": "sensor_001",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": 55.55
            },
            "description": "Impersonating the real sensor_001 with fake temperature"
        },
        {
            "name": "Rogue Device",
            "data": {
                "device_id": "rogue_device_666",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": 42.0
            },
            "description": "Completely unauthorized device injecting data"
        },
        {
            "name": "Phantom Sensor",
            "data": {
                "device_id": "phantom_sensor_999",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": 99.99
            },
            "description": "Non-existent sensor sending dangerous high temperature reading"
        }
    ]

    results = []

    for i, device in enumerate(fake_devices, 1):

        print(f"[ATTACK {i}/3] {device['name']}")
        print(f"    Strategy    : {device['description']}")
        print(f"    Device ID   : {device['data']['device_id']}")
        print(f"    Temperature : {device['data']['temperature']}°C")

        try:
            response = requests.post(
                "http://127.0.0.1:5000/data",
                json=device["data"]
            )
            result = response.json()
            status = result.get("status")

            if status == "stored":
                print(f"    Result      : ⚠️  ACCEPTED — Unauthorized data was stored!")
                results.append(("ACCEPTED", device["name"]))
            elif status == "rejected":
                print(f"    Result      : ✅ REJECTED — System blocked the spoofed device!")
                results.append(("REJECTED", device["name"]))
            else:
                print(f"    Result      : {result}")
                results.append(("UNKNOWN", device["name"]))

        except Exception as e:
            print(f"    Error       : {e}")
            results.append(("ERROR", device["name"]))

        print()
        time.sleep(2)

    # SUMMARY
    print("="*50)
    print("SPOOFED DEVICE ATTACK SUMMARY")
    print("="*50)

    accepted = sum(1 for r in results if r[0] == "ACCEPTED")
    rejected = sum(1 for r in results if r[0] == "REJECTED")

    for status, name in results:
        icon = "⚠️" if status == "ACCEPTED" else "✅"
        print(f"  {icon} {name}: {status}")

    print(f"\n  Accepted: {accepted}/3 | Rejected: {rejected}/3")

    if accepted > 0:
        print("\n  FINDING: The system does not validate device identity.")
        print("  → Any device can inject data into the system.")
        print("  → A device registry or authentication mechanism is needed.")
    else:
        print("\n  The system successfully blocked all spoofed devices.")

    print("="*50)

if __name__ == "__main__":
    simulate_spoofed_device_attack()
