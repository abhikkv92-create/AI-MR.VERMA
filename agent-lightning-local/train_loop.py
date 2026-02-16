"""
Agent Lightning Continuous Training Loop (Data Collection Mode)
───────────────────────────────────────────────────────────────
Runs inside Docker.
Automatically collects high-quality interactions for future SFT.
NVIDIA MODE: Prompt Optimization (Ollama-dependent) is DISABLED.
"""

import glob
import json
import logging
import os
import signal
import time
from datetime import datetime, timezone

from reward_engine import batch_compute_rewards

# ── Configuration ──
TRAINING_INTERVAL = int(os.environ.get("TRAINING_INTERVAL_HOURS", "6"))
MIN_SAMPLES = int(os.environ.get("MIN_SAMPLES_FOR_TRAINING", "10"))
POS_THRESHOLD = float(os.environ.get("REWARD_THRESHOLD_POSITIVE", "0.3"))
NEG_THRESHOLD = float(os.environ.get("REWARD_THRESHOLD_NEGATIVE", "-0.3"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

INTERACTION_DIR = "/app/data/interactions"
SFT_DIR = "/app/data/sft_batches"
REWARD_DIR = "/app/data/rewards"
CHECKPOINT_DIR = "/app/checkpoints"
LOG_DIR = "/app/logs"
TRIGGER_SIGNAL = "/app/data/trigger_train.signal"
SFT_SIGNAL = "/app/data/trigger_sft.signal"

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s [TRAINER] %(levelname)s %(message)s")
log = logging.getLogger(__name__)

training_step = 0
_shutdown_requested = False


def _handle_signal(signum, frame):
    """Graceful shutdown handler."""
    global _shutdown_requested
    log.info(f"Received signal {signum}, shutting down after current cycle...")
    _shutdown_requested = True


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def load_recent_interactions(since_hours: int) -> list:
    """Load interactions from individual JSON files (collector format)."""
    cutoff = time.time() - (since_hours * 3600)
    all_interactions = []

    # Read individual JSON files written by collector
    for filepath in sorted(glob.glob(os.path.join(INTERACTION_DIR, "*.json"))):
        try:
            with open(filepath) as f:
                interaction = json.load(f)
                if interaction.get("timestamp", 0) > cutoff:
                    all_interactions.append(interaction)
        except (json.JSONDecodeError, OSError) as e:
            log.warning(f"Skipped corrupt file {filepath}: {e}")
            continue

    log.info(f"Loaded {len(all_interactions)} interactions from last {since_hours} hours")
    return all_interactions


def compute_all_rewards(interactions: list) -> list:
    """Compute reward scores for unscored interactions."""
    unscored = [i for i in interactions if i.get("reward_score") is None]
    if unscored:
        log.info(f"Computing rewards for {len(unscored)} interactions")
        batch_compute_rewards(unscored)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M")
        os.makedirs(REWARD_DIR, exist_ok=True)
        with open(os.path.join(REWARD_DIR, f"rewards_{date_str}.jsonl"), "a") as f:
            for i in unscored:
                f.write(json.dumps({"id": i.get("id"), "reward_score": i["reward_score"], "timestamp": i.get("timestamp")}) + "\n")
    return [i for i in interactions if i.get("reward_score") is not None]


def collect_sft_data(high_reward_examples: list) -> str:
    """Collect top-performing interactions as SFT training data."""
    global training_step
    sft_examples = []
    for ex in high_reward_examples:
        user_msg = next((m.get("content", "") for m in ex.get("messages", []) if m.get("role") == "user"), "")
        if user_msg and ex.get("response"):
            sft_examples.append({
                "instruction": user_msg,
                "input": "",
                "output": ex["response"],
                "reward": ex.get("reward_score", 0)
            })

    if not sft_examples:
        return ""

    os.makedirs(SFT_DIR, exist_ok=True)
    filepath = os.path.join(SFT_DIR, f"sft_batch_{training_step}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json")
    with open(filepath, "w") as f:
        json.dump(sft_examples, f, indent=2)
    log.info(f"SFT batch saved: {len(sft_examples)} examples → {filepath}")
    return filepath


def run_training_cycle():
    """Execute one training cycle: load → score → collect SFT data."""
    global training_step
    log.info("=" * 60 + f"\nTRAINING CYCLE START — {datetime.now(timezone.utc).isoformat()}Z\n" + "=" * 60)

    interactions = load_recent_interactions(since_hours=TRAINING_INTERVAL * 2)
    if len(interactions) < MIN_SAMPLES:
        log.info(f"Insufficient data: {len(interactions)}/{MIN_SAMPLES}. Skipping.")
        return

    scored = compute_all_rewards(interactions)
    high_reward = [i for i in scored if i.get("reward_score", 0) > POS_THRESHOLD]

    # Strategy B: Collect SFT Data
    top_n = sorted(scored, key=lambda x: x.get("reward_score", 0), reverse=True)[:max(10, len(scored) // 4)]
    sft_path = collect_sft_data(top_n)

    # Log run
    training_step += 1
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "training_history.jsonl"), "a") as f:
        f.write(json.dumps({
            "step": training_step,
            "timestamp": time.time(),
            "interactions_scored": len(scored),
            "high_reward": len(high_reward),
            "sft_batch_path": sft_path
        }) + "\n")

    log.info(f"TRAINING CYCLE COMPLETE — step {training_step}")


def main():
    log.info("╔══════════════════════════════════════════════════════════╗")
    log.info("║  AGENT LIGHTNING — CONTINUOUS DATA COLLECTION (NVIDIA)  ║")
    log.info("╚══════════════════════════════════════════════════════════╝")

    run_training_cycle()

    while not _shutdown_requested:
        # Check triggers every 10s for 1 hour
        for _ in range(360):
            if _shutdown_requested:
                break
            if os.path.exists(TRIGGER_SIGNAL):
                log.info("Prompt Optimization Triggered -> IGNORED (NVIDIA Mode)")
                try:
                    os.remove(TRIGGER_SIGNAL)
                except OSError:
                    pass
            if os.path.exists(SFT_SIGNAL):
                log.info("SFT Triggered -> Running localized fine-tuning...")
                try:
                    os.remove(SFT_SIGNAL)
                    import subprocess
                    subprocess.run(["python", "sft_trainer.py"], check=True)
                except Exception as e:
                    log.error(f"SFT run failed: {e}")
            time.sleep(10)

        if _shutdown_requested:
            break
        try:
            run_training_cycle()
        except Exception as e:
            log.error(f"Scheduled cycle failed: {e}")

    log.info("Trainer shut down gracefully.")


if __name__ == "__main__":
    main()
