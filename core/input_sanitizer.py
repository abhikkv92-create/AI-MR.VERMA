import logging
import re

logger = logging.getLogger("Kernel.Security.Sanitizer")

class InputSanitizer:
    """
    Utility for sanitizing user inputs to protect the MR.VERMA system.
    Focuses on prompt injection, PII leakage, and malicious code snippets.
    """

    # Simple patterns for common prompt injection attempts
    INJECTION_PATTERNS = [
        r"(?i)ignore (all )?previous instructions",
        r"(?i)system (role|prompt|message)",
        r"(?i)you are now",
        r"(?i)forget everything",
        r"(?i)reveal (your )?secret"
    ]

    # Patterns for potentially sensitive data (PII)
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "api_key": r"(?i)nvapi-[a-zA-Z0-9]{64}",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    }

    @staticmethod
    def sanitize(text: str) -> str:
        """
        Main entry point for sanitation.
        """
        if not text:
            return ""

        sanitized = text

        # 1. Detect and Flag Prompt Injection
        for pattern in InputSanitizer.INJECTION_PATTERNS:
            if re.search(pattern, sanitized):
                logger.warning(f"Potential prompt injection detected: {pattern}")
                # We don't remove it, but we log it and could potentially block it in the Orchestrator

        # 2. Mask PII
        for label, pattern in InputSanitizer.PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[REDACTED_{label.upper()}]", sanitized)

        # 3. Basic cleanup (remove null bytes, etc.)
        sanitized = sanitized.replace("\0", "")

        return sanitized.strip()

    @staticmethod
    def is_dangerous(text: str) -> bool:
        """
        Heuristic check for dangerous commands or scripts.
        """
        dangerous_keywords = ["rm -rf", "format c:", "os.system(", "subprocess.run(", "eval("]
        for kw in dangerous_keywords:
            if kw in text.lower():
                return True
        return False

# Global instance
sanitizer = InputSanitizer()
