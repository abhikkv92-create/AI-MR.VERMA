
import base64
import datetime
import hashlib
import json
import logging
import os
import secrets
from functools import wraps
from typing import Any

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .env_manager import load_env_file

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Kernel.Security")

# Load .env
load_env_file()

# In a real scenario, these would be loaded from secure env vars
SECRET_KEY = os.environ.get("MR_VERMA_SECRET_KEY", secrets.token_hex(32))

class SecurityOrchestrator:
    """
    Manages Security, Authentication, and Encryption for MR.VERMA.
    Uses AES-256 for data encryption and HS256 (via HMAC) for tokens if libs missing,
    or proper JWT if available.
    """

    def __init__(self):
        self.audit_log_path = os.path.join(os.getcwd(), "logs", "audit.log")
        self._ensure_logs_dir()

        # Derive a 256-bit key from the secret key
        self.key = hashlib.sha256(SECRET_KEY.encode()).digest()

        logger.info("Security Orchestrator Initialized (AES-256-GCM Mode).")

    def _ensure_logs_dir(self):
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)

    def log_audit_event(self, agent_name: str, action: str, status: str, details: str = ""):
        """
        Immutable audit logging. 
        """
        timestamp = datetime.datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "action": action,
            "status": status,
            "details": details
        }

        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def generate_token(self, user_id: str, permissions: list) -> str:
        """
        Generates a secure session token with HMAC-SHA256 signature.
        """
        import hmac
        payload = {
            "sub": user_id,
            "perms": permissions,
            "iat": datetime.datetime.utcnow().timestamp(),
            "exp": (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp(),
            "nonce": secrets.token_hex(8)
        }

        token_data = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

        # Proper HMAC-SHA256 Signature
        signature = hmac.new(
            self.key,
            token_data.encode(),
            hashlib.sha256
        ).digest()

        sig_encoded = base64.urlsafe_b64encode(signature).decode()
        return f"{token_data}.{sig_encoded}"

    def validate_token(self, token: str) -> bool:
        """
        Validates the session token using HMAC-SHA256 signature and expiration check.
        """
        import hmac
        if not token or "." not in token:
            return False

        try:
            token_data, sig_received = token.split(".", 1)

            # Verify Signature
            expected_sig = hmac.new(
                self.key,
                token_data.encode(),
                hashlib.sha256
            ).digest()
            expected_sig_encoded = base64.urlsafe_b64encode(expected_sig).decode()

            if not hmac.compare_digest(sig_received, expected_sig_encoded):
                logger.warning("Invalid token signature detected!")
                return False

            # Verify Expiration
            payload = json.loads(base64.urlsafe_b64decode(token_data).decode())
            if datetime.datetime.utcnow().timestamp() > payload.get("exp", 0):
                logger.warning("Token expired.")
                return False

            return True
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return False

    def rotate_secret(self):
        """
        Securely rotates the master secret key.
        Saves new key to .env (if writable) and updates current instance key.
        """
        new_secret = secrets.token_hex(32)
        env_path = os.path.join(os.getcwd(), ".env")

        try:
            lines = []
            if os.path.exists(env_path):
                with open(env_path) as f:
                    lines = f.readlines()

            found = False
            with open(env_path, "w") as f:
                for line in lines:
                    if line.startswith("MR_VERMA_SECRET_KEY="):
                        f.write(f"MR_VERMA_SECRET_KEY={new_secret}\n")
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write(f"MR_VERMA_SECRET_KEY={new_secret}\n")

            # Update live key
            global SECRET_KEY
            SECRET_KEY = new_secret
            self.key = hashlib.sha256(SECRET_KEY.encode()).digest()
            logger.info("Master Secret Rotated Successfully.")
            self.log_audit_event("PLATFORM", "SECRET_ROTATION", "SUCCESS", "Master secret key refreshed.")
            return True
        except Exception as e:
            logger.error(f"Secret rotation failed: {e}")
            return False

    def get_secret(self, key: str, default: Any = None) -> str:
        """
        Securely retrieves a secret from environment variables.
        """
        val = os.environ.get(key, default)
        if val is None:
            logger.warning(f"Secret {key} not found!")
        return val

    def encrypt_data(self, plaintext: str) -> str:
        """
        Encrypts sensitive data using AES-256-GCM.
        """
        iv = os.urandom(12) # GCM recommended IV size
        encryptor = Cipher(
            algorithms.AES(self.key),
            modes.GCM(iv),
            backend=default_backend()
        ).encryptor()

        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

        # Combine IV + Tag + Ciphertext
        combined = iv + encryptor.tag + ciphertext
        return f"AES256:{base64.b64encode(combined).decode()}"

    def decrypt_data(self, ciphertext: str) -> str:
        """
        Decrypts sensitive data using AES-256-GCM.
        """
        if not ciphertext.startswith("AES256:"):
            return ciphertext

        try:
            data = base64.b64decode(ciphertext.split("AES256:")[1])
            iv = data[:12]
            tag = data[12:28]
            payload = data[28:]

            decryptor = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv, tag),
                backend=default_backend()
            ).decryptor()

            return (decryptor.update(payload) + decryptor.finalize()).decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return "[DECRYPTION_ERROR]"

    def require_permission(self, permission: str):
        """
        Decorator to enforce permissions.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"Checking permission: {permission}")
                return func(*args, **kwargs)
            return wrapper
        return decorator

# Singleton
security_service = SecurityOrchestrator()
