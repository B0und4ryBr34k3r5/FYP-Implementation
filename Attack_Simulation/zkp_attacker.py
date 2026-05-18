import json
import os
from web3 import Web3

def simulate_smart_contract_rejection():
    """
    ZKP FAKE PROOF ATTACK SIMULATION

    Attack Vector: An attacker bypasses the Flask server entirely and connects 
    directly to the blockchain network. The attacker then submits fabricated 
    (garbage) cryptographic proof values to the Groth16Verifier smart contract, 
    attempting to trick the system into accepting invalid data.

    What this tests: Whether the Groth16 ZKP cryptographic verification 
    on the smart contract can detect and reject forged proofs.
    """
    print("==================================================")
    print("SMART CONTRACT (ZKP) ATTACKER INITIALIZED")
    print("==================================================")
    print("[*] Bypassing Flask API...")
    print("[*] Connecting directly to the Blockchain Network (Hardhat)...")

    # Connect to local Blockchain
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
    if not w3.is_connected():
        print("Could not connect to Blockchain. Is Hardhat running?")
        return
        
    print("[*] Connection successful.")

    # Load Verifier Contract
    # Navigate up one level from Attack_Simulation/ to the project root
    project_root = os.path.join(os.path.dirname(__file__), "..")

    try:
        addresses_path = os.path.join(project_root, "Blockchain", "addresses.json")
        with open(addresses_path) as f:
            addresses = json.load(f)
            verifier_address = addresses["verifier"]

        verifier_abi_path = os.path.join(
            project_root, "Blockchain", "artifacts", "contracts",
            "Verifier.sol", "Groth16Verifier.json"
        )
        with open(verifier_abi_path) as f:
            verifier_abi = json.load(f)["abi"]
            
        verifier_contract = w3.eth.contract(address=verifier_address, abi=verifier_abi)
        
    except Exception as e:
        print("Could not load Verifier Contract:", e)
        return

    print(f"[*] Connected to Verifier Smart Contract at: {verifier_address}")
    
    # ---------------------------------------------------------
    # THE ATTACK: Submitting a tampered payload with fake math
    # ---------------------------------------------------------
    fake_temp = 999
    print(f"\n[!] INJECTING MALICIOUS PAYLOAD: {fake_temp} degrees C")
    print("[!] Generating fake cryptographic proof (Garbage Math)...")
    
    # Fake/Garbage Proof Data
    fake_pi_a = [123456789, 987654321]
    fake_pi_b = [[111, 222], [333, 444]]
    fake_pi_c = [555, 666]
    fake_public_signals = [fake_temp]

    print("[*] Submitting to Smart Contract for Verification...")
    
    # The Smart Contract executes the complex ZKP math entirely on-chain
    try:
        is_valid = verifier_contract.functions.verifyProof(
            fake_pi_a, 
            fake_pi_b, 
            fake_pi_c, 
            fake_public_signals
        ).call()
        
        if is_valid:
            print("ATTACK SUCCESSFUL: The smart contract accepted the fake proof! (THIS SHOULD NOT HAPPEN)")
        else:
            print("\nSYSTEM DEFENDED: The Smart Contract cryptography FAILED the math check!")
            print("Result: false")
            print("The transaction is instantly REJECTED before it can reach the ledger.")
            
    except Exception as e:
        print("\nSYSTEM DEFENDED: The Smart Contract completely reverted the transaction!")
        print(f"Reason: {e}")

    print("==================================================")

if __name__ == "__main__":
    simulate_smart_contract_rejection()
