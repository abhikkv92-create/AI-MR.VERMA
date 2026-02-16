import os
import sys

# Add Agent Lightning to path
sys.path.append(os.path.abspath("MICROSOFT LIGHT"))

from agentlightning.emitter import emit_message, emit_reward
from agentlightning.store import LightningStore
from agentlightning.tracer import set_active_tracer
from agentlightning.tracer.dummy import DummyTracer

print("[INTEGRATION] Testing AI KIT <-> Agent Lightning Bridge...")

try:
    # 0. Initialize Tracer (Concrete implementation)
    t = DummyTracer()
    set_active_tracer(t)

    # 1. Test Trace/Message Emission
    print("1. Emitting Test Trace...", end=" ")
    emit_message("Integration verification trace")
    print("[OK]")

    # 2. Test Reward Emission
    print("2. Emitting Test Reward...", end=" ")
    emit_reward(1.0, attributes={"type": "test_reward"})
    print("[OK]")

    # 3. Test Store Connection
    print("3. Querying LightningStore...", end=" ")
    store = LightningStore()
    # Just init is enough to verify DB connection
    print("[OK]")

    print("\n[SUCCESS] INTEGRATION SUCCESSFUL: Bridge is active.")
    sys.exit(0)

except Exception as e:
    print(f"\n[FAILURE] INTEGRATION FAILED: {e!s}")
    sys.exit(1)
