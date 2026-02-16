
import logging
import os

logger = logging.getLogger("Kernel.EnvManager")

def load_env_file(filepath: str = ".env"):
    """
    Loads environment variables from a .env file into os.environ.
    Does not overwrite existing environment variables.
    """
    if not os.path.exists(filepath):
        logger.warning(f"No {filepath} file found. Assuming secrets are in environment.")
        return

    logger.info(f"Loading secrets from {filepath}...")
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    if key not in os.environ:
                        os.environ[key] = value
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")

    # Load Secondary AI Key
    if "NVIDIA_API_KEY_SECONDARY" not in os.environ and os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                if line.startswith("NVIDIA_API_KEY_SECONDARY="):
                    os.environ["NVIDIA_API_KEY_SECONDARY"] = line.split("=", 1)[1].strip()
