import requests
import time
from datetime import datetime

def simulate_dos_attack():
    """
    DENIAL-OF-SERVICE (DoS) FLOOD ATTACK SIMULATION

    Attack Vector: An attacker floods the server with a rapid burst 
    of data submissions to overwhelm it, potentially causing the 
    ZKP generation and blockchain transactions to bottleneck, 
    degrading service for legitimate users.

    What this tests: Whether the system can handle high-volume 
    traffic and has rate-limiting protections in place.
    """
    print("==================================================")
    print("🌊 DoS FLOOD ATTACKER INITIALIZED 🌊")
    print("==================================================")
    print("[*] Preparing to flood the server with rapid requests...")
    print("[*] Target: http://127.0.0.1:5000/data")
    print("[*] This tests system resilience under high traffic.\n")

    TOTAL_REQUESTS = 10
    successful = 0
    failed = 0
    rejected = 0
    response_times = []

    print(f"[!] LAUNCHING FLOOD — {TOTAL_REQUESTS} rapid requests...\n")

    start_time = time.time()

    for i in range(1, TOTAL_REQUESTS + 1):

        # Each request has a different timestamp and temperature
        flood_data = {
            "device_id": f"flood_device_{i}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": 50 + i
        }

        req_start = time.time()

        try:
            response = requests.post(
                "http://127.0.0.1:5000/data",
                json=flood_data,
                timeout=30
            )
            req_time = round(time.time() - req_start, 2)
            response_times.append(req_time)

            result = response.json()
            status = result.get("status")

            if status == "stored":
                successful += 1
                print(f"  [{i:02d}/{TOTAL_REQUESTS}] ⚠️  STORED  | {req_time}s | {flood_data['device_id']}")
            elif status == "rejected":
                rejected += 1
                print(f"  [{i:02d}/{TOTAL_REQUESTS}] 🛡️ REJECTED | {req_time}s | {flood_data['device_id']}")
            else:
                failed += 1
                print(f"  [{i:02d}/{TOTAL_REQUESTS}] ❓ {status} | {req_time}s")

        except requests.exceptions.Timeout:
            failed += 1
            print(f"  [{i:02d}/{TOTAL_REQUESTS}] ❌ TIMEOUT — Server unresponsive!")

        except Exception as e:
            failed += 1
            print(f"  [{i:02d}/{TOTAL_REQUESTS}] ❌ ERROR — {e}")

    total_time = round(time.time() - start_time, 2)
    avg_time = round(sum(response_times) / len(response_times), 2) if response_times else 0

    # SUMMARY
    print("\n" + "="*50)
    print("DoS FLOOD ATTACK SUMMARY")
    print("="*50)
    print(f"  Total Requests    : {TOTAL_REQUESTS}")
    print(f"  Stored (accepted) : {successful}")
    print(f"  Rejected          : {rejected}")
    print(f"  Failed/Timeout    : {failed}")
    print(f"  Total Time        : {total_time}s")
    print(f"  Avg Response Time : {avg_time}s")

    if successful == TOTAL_REQUESTS:
        print("\n  FINDING: The system accepted ALL flood requests.")
        print("  → No rate-limiting or throttling is in place.")
        print("  → The server processed every request including ZKP + Blockchain.")
        print("  → A rate-limiter (e.g., Flask-Limiter) is recommended.")
    elif failed > 0:
        print(f"\n  FINDING: {failed} requests failed under load.")
        print("  → The system struggled under high traffic volume.")
        print("  → The ZKP generation and blockchain transactions bottlenecked.")
    else:
        print("\n  The system handled the flood gracefully.")

    print("="*50)

if __name__ == "__main__":
    simulate_dos_attack()
