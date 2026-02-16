
import logging
import os
import shutil
import time

logger = logging.getLogger("Kernel.Maintenance")

class MaintenanceManager:
    """
    Manages system hygiene: Log rotation and Temp file cleanup.
    """

    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.logs_dir = os.path.join(root_dir, "logs")

    def rotate_logs(self, max_size_mb: int = 5, backup_count: int = 3):
        """
        Rotates logs larger than max_size_mb.
        """
        logger.info("Starting Log Rotation...")
        count = 0

        if not os.path.exists(self.logs_dir):
            return 0

        for file in os.listdir(self.logs_dir):
            if file.endswith(".log") or file.endswith(".json"):
                path = os.path.join(self.logs_dir, file)
                try:
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    if size_mb > max_size_mb:
                        # Rotate
                        timestamp = int(time.time())
                        backup_path = f"{path}.{timestamp}.bak"
                        shutil.move(path, backup_path)
                        logger.info(f"Rotated {file} ({size_mb:.2f}MB) -> {backup_path}")

                        # Create empty new file
                        open(path, "w").close()
                        count += 1

                        # Cleanup old backups (not implemented in this simplified version)
                except Exception as e:
                    logger.error(f"Error rotating {file}: {e}")

        return count

    def clean_temp_files(self, max_age_hours: int = 24):
        """
        Deletes .tmp files older than max_age_hours.
        Also targets known large garbage files like '0.tmp'.
        """
        logger.info("Starting Temp File Cleanup...")
        count = 0
        deleted_size_mb = 0

        cutoff = time.time() - (max_age_hours * 3600)

        for root, _, files in os.walk(self.root_dir):
            if "node_modules" in root or ".git" in root:
                continue

            for file in files:
                if file.endswith(".tmp") or file.endswith(".wal") or file == "0.tmp":
                    path = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(path)
                        size_mb = os.path.getsize(path) / (1024 * 1024)

                        # Aggressive cleanup for the known 64MB files
                        if size_mb > 50 or mtime < cutoff:
                            os.remove(path)
                            logger.info(f"Deleted {path} ({size_mb:.2f}MB)")
                            count += 1
                            deleted_size_mb += size_mb
                    except Exception as e:
                        logger.error(f"Error deleting {path}: {e}")

        return count, deleted_size_mb

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    mgr = MaintenanceManager(os.getcwd())
    mgr.rotate_logs()
    mgr.clean_temp_files()
