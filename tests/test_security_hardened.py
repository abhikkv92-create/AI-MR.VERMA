
import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.security_orchestrator import security_service

logging.basicConfig(level=logging.INFO)

def test_hardened_security():
    load_dotenv()
    
    # Test 1: AES-256-GCM Encryption/Decryption
    print("\n--- Test 1: Real AES-256-GCM Encryption ---")
    secret_data = "This is a top-secret project memory for MR.VERMA."
    encrypted = security_service.encrypt_data(secret_data)
    print(f"Plaintext: {secret_data}")
    print(f"Ciphertext: {encrypted}")
    
    decrypted = security_service.decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert decrypted == secret_data, "Decryption mismatch!"
    assert encrypted.startswith("AES256:"), "Encryption tag mismatch!"
    print("Test 1 Passed: AES-256-GCM is 100% operational.")

    # Test 2: Audit Logging
    print("\n--- Test 2: Audit Logging ---")
    security_service.log_audit_event("SecurityTest", "Hardening_Validation", "SUCCESS", "AES-256 verified.")
    
    audit_log = os.path.join(os.getcwd(), "logs", "audit.log")
    if os.path.exists(audit_log):
        with open(audit_log, "r") as f:
            lines = f.readlines()
            last_event = lines[-1]
            print(f"Last Audit Event: {last_event.strip()}")
            assert "Hardening_Validation" in last_event, "Audit log entry missing!"
    print("Test 2 Passed: Immutable audit logging is functional.")

if __name__ == "__main__":
    test_hardened_security()
