#!/usr/bin/env python3
"""
🚀 MR.VERMA FULL SYSTEM LAUNCHER
════════════════════════════════

Launches:
1. Docker services (if available)
2. Web Dashboard (http://localhost:8765)
3. Terminal Dashboard
4. Live demonstrations

Usage: python launch_full_system.py
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path


def print_banner():
    """Print launch banner"""
    print(r"""
===================================================================

   [ROBOT]  MR.VERMA - FULL SYSTEM LAUNCH  [ROBOT]

   Starting all services for end-to-end demonstration

===================================================================
""")


def start_docker():
    """Start Docker services"""
    print("[DOCKER] Starting Docker services...")
    try:
        result = subprocess.run(
            ["docker-compose", "-f", "docker/docker-compose.yml", "up", "-d"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print("[OK] Docker services started successfully")
            return True
        else:
            print(f"[WARN]  Docker warning: {result.stderr[:200]}")
            print("   Continuing without Docker...")
            return False
    except Exception as e:
        print(f"[WARN]  Could not start Docker: {e}")
        print("   Continuing in standalone mode...")
        return False


def start_web_dashboard():
    """Start web dashboard"""
    print("\n🌐 Starting Web Dashboard...")
    print("   [URL] URL: http://localhost:8765")

    def run_web():
        os.system("python dashboard_web.py")

    thread = threading.Thread(target=run_web, daemon=True)
    thread.start()
    time.sleep(2)
    print("[OK] Web Dashboard started")


def start_terminal_dashboard():
    """Start terminal dashboard"""
    print("\n[TERM]  Starting Terminal Dashboard...")
    print("   This will show live AI thinking process\n")
    time.sleep(1)

    # Run terminal dashboard in main thread
    os.system("python dashboard_live.py")


def main():
    """Main launcher"""
    print_banner()

    # Check Python version
    if sys.version_info < (3, 9):
        print("[ERROR] Error: Python 3.9+ required")
        sys.exit(1)

    print("[LIST] Launch Plan:")
    print("   1. Start Docker services (optional)")
    print("   2. Start Web Dashboard (http://localhost:8765)")
    print("   3. Start Terminal Dashboard (live demonstration)")
    print("   4. Run end-to-end tests\n")

    print("Auto-starting in 3 seconds...")
    time.sleep(3)
    print()

    # Step 1: Docker (optional)
    docker_running = start_docker()

    # Step 2: Web Dashboard
    start_web_dashboard()

    # Step 3: Terminal Dashboard (this blocks)
    try:
        start_terminal_dashboard()
    except KeyboardInterrupt:
        print("\n\n[BYE] Shutting down MR.VERMA...")
        if docker_running:
            print("[DOCKER] Stopping Docker services...")
            os.system("docker-compose -f docker/docker-compose.yml down")
        print("[OK] System stopped. Goodbye!")


if __name__ == "__main__":
    main()
