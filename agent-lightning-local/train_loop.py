"""
Agent Lightning Continuous Training Loop
────────────────────────────────────────
Runs inside Docker. Connects to Ollama on the host machine.
Automatically trains the local LLM based on usage patterns.

TRAINING STRATEGY (tiered by available data):
  < 10 interactions  → WAIT (insufficient data)
  10-100 interactions → PROMPT OPTIMIZATION (refine system prompt, no weight changes)
  100-500 interactions → PROMPT OPT + best-example collection for future SFT
  500+ interactions   → SUPERVISED FINE-TUNING (LoRA on high-reward examples)
"""

import os
import glob
import json
import time
import logging
import subprocess
import requests
from datetime import datetime, timedelta
from reward_engine import compute_reward, batch_compute_rewards

# ── Configuration from environment ──
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "local-coder")
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

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [TRAINER] %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIR, "trainer.log"))
    ]
)
log = logging.getLogger(__name__)

training_step = 0


def load_recent_interactions(since_hours: int) -> list:
    """Load interactions from JSONL files within the time window."""
    cutoff = time.time() - (since_hours * 3600)
    all_interactions = []

    for filepath in sorted(glob.glob(os.path.join(INTERACTION_DIR, "interactions_*.jsonl"))):
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    interaction = json.loads(line)
                    if interaction.get("timestamp", 0) > cutoff:
                        all_interactions.append(interaction)
                except json.JSONDecodeError:
                    continue

    log.info(f"Loaded {len(all_interactions)} interactions from last {since_hours} hours")
    return all_interactions


def compute_all_rewards(interactions: list) -> list:
    """Score every interaction that hasn't been scored yet."""
    unscored = [i for i in interactions if i.get("reward_score") is None]
    if unscored:
        log.info(f"Computing rewards for {len(unscored)} unscored interactions")
        batch_compute_rewards(unscored)

        # Save reward data
        date_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
        filepath = os.path.join(REWARD_DIR, f"rewards_{date_str}.jsonl")
        with open(filepath, "a") as f:
            for interaction in unscored:
                f.write(json.dumps({
                    "id": interaction.get("id"),
                    "reward_score": interaction["reward_score"],
                    "timestamp": interaction.get("timestamp"),
                }) + "\n")

    scored = [i for i in interactions if i.get("reward_score") is not None]
    return scored


def run_prompt_optimization(positive: list, negative: list) -> bool:
    """
    STRATEGY A: Automatic Prompt Optimization
    ──────────────────────────────────────────
    Analyzes high-reward vs low-reward interactions.
    Generates an improved system prompt.
    Hot-swaps the updated model into Ollama.
    NO model weight changes. CPU-friendly. Works on 16GB RAM.
    """
    global training_step

    log.info("Running Prompt Optimization...")
    log.info(f"  Positive examples: {len(positive)}")
    log.info(f"  Negative examples: {len(negative)}")

    # Analyze patterns in successful interactions
    pos_avg_len = sum(len(p.get("response", "")) for p in positive) / max(len(positive), 1)
    neg_avg_len = sum(len(n.get("response", "")) for n in negative) / max(len(negative), 1)

    # Extract what works from high-reward responses
    positive_traits = []
    if pos_avg_len < neg_avg_len:
        positive_traits.append("Keep responses concise and focused. Avoid unnecessary verbosity.")
    if pos_avg_len > neg_avg_len:
        positive_traits.append("Provide thorough, detailed explanations with complete code examples.")

    # Check if code blocks correlate with positive reward
    pos_has_code = sum(1 for p in positive if "```" in p.get("response", "")) / max(len(positive), 1)
    neg_has_code = sum(1 for n in negative if "```" in n.get("response", "")) / max(len(negative), 1)
    if pos_has_code > neg_has_code + 0.2:
        positive_traits.append("Always include working code examples in fenced code blocks.")

    # Check if explanations before code correlate with positive reward
    pos_explains_first = sum(
        1 for p in positive
        if p.get("response", "").find("```") > 100
    ) / max(len(positive), 1)
    if pos_explains_first > 0.6:
        positive_traits.append("Explain your reasoning and approach before writing code.")

    # Build improved system prompt
    base_prompt = (
        "You are a specialized AI coding assistant. "
        "Provide production-ready, well-documented code with proper error handling. "
        "Follow lean principles and minimize dependencies."
    )

    if positive_traits:
        learned = "\n".join(f"▶ {trait}" for trait in positive_traits)
        improved_prompt = f"{base_prompt}\n\nLearned guidelines:\n{learned}"
    else:
        improved_prompt = base_prompt

    # Write new Modelfile
    training_step += 1
    modelfile_path = os.path.join(CHECKPOINT_DIR, f"Modelfile.v{training_step}")
    modelfile_content = f'''FROM qwen2.5-coder:7b

SYSTEM """{improved_prompt}"""

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 8192
PARAMETER num_predict 2048
PARAMETER repeat_penalty 1.1
'''

    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)

    # Hot-swap the model in Ollama via API
    log.info(f"Hot-swapping model to v{training_step}...")
    try:
        # Use Ollama CLI to create updated model
        result = subprocess.run(
            ["curl", "-X", "POST", f"{OLLAMA_BASE_URL}/api/create",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({
                 "name": OLLAMA_MODEL,
                 "modelfile": modelfile_content
             })],
            capture_output=True, timeout=120, text=True
        )
        if result.returncode == 0:
            log.info(f"Model hot-swapped successfully to v{training_step}")
            log.info(f"Modelfile saved: {modelfile_path}")
            return True
        else:
            log.error(f"Hot-swap failed: {result.stderr}")
            return False
    except Exception as e:
        log.error(f"Hot-swap error: {e}")
        return False


def collect_sft_data(high_reward_examples: list) -> str:
    """
    STRATEGY B: Collect SFT Training Data
    ──────────────────────────────────────
    Exports the highest-reward interactions as supervised training data.
    Format: Alpaca-style JSON for future fine-tuning.
    """
    global training_step

    sft_examples = []
    for ex in high_reward_examples:
        messages = ex.get("messages", [])
        user_msg = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_msg = msg.get("content", "")

        if user_msg and ex.get("response"):
            sft_examples.append({
                "instruction": user_msg,
                "input": "",
                "output": ex["response"],
                "reward": ex.get("reward_score", 0),
            })

    if not sft_examples:
        return ""

    filepath = os.path.join(SFT_DIR, f"sft_batch_{training_step}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.json")
    with open(filepath, "w") as f:
        json.dump(sft_examples, f, indent=2)

    log.info(f"SFT batch saved: {len(sft_examples)} examples → {filepath}")
    return filepath


def count_total_sft_examples() -> int:
    """Count total accumulated SFT training examples across all batches."""
    total = 0
    for filepath in glob.glob(os.path.join(SFT_DIR, "sft_batch_*.json")):
        try:
            with open(filepath) as f:
                data = json.load(f)
                total += len(data)
        except Exception:
            continue
    return total


def run_training_cycle():
    """
    Execute one complete training cycle:
      1. Load recent interactions
      2. Compute rewards
      3. Separate into positive/negative
      4. Run prompt optimization
      5. Collect SFT data from best examples
      6. Log results
    """
    log.info("=" * 60)
    log.info(f"TRAINING CYCLE START — {datetime.utcnow().isoformat()}Z")
    log.info("=" * 60)

    # Step 1: Load interactions
    interactions = load_recent_interactions(since_hours=TRAINING_INTERVAL * 2)

    if len(interactions) < MIN_SAMPLES:
        log.info(f"Insufficient data: {len(interactions)}/{MIN_SAMPLES} samples. Skipping.")
        return

    # Step 2: Compute rewards
    scored = compute_all_rewards(interactions)

    # Step 3: Separate by reward threshold
    positive = [i for i in scored if i.get("reward_score", 0) > POS_THRESHOLD]
    negative = [i for i in scored if i.get("reward_score", 0) < NEG_THRESHOLD]
    neutral = [i for i in scored if NEG_THRESHOLD <= i.get("reward_score", 0) <= POS_THRESHOLD]

    avg_reward = sum(i.get("reward_score", 0) for i in scored) / len(scored)

    log.info(f"Scored interactions: {len(scored)}")
    log.info(f"  Positive (>{POS_THRESHOLD}): {len(positive)}")
    log.info(f"  Negative (<{NEG_THRESHOLD}): {len(negative)}")
    log.info(f"  Neutral: {len(neutral)}")
    log.info(f"  Average reward: {avg_reward:.4f}")

    # Step 4: Run prompt optimization (always, if we have positive + negative examples)
    if positive and negative:
        success = run_prompt_optimization(positive, negative)
        if success:
            log.info("Prompt optimization: SUCCESS")
        else:
            log.info("Prompt optimization: FAILED — will retry next cycle")
    elif positive:
        log.info("No negative examples — prompt is performing well")
    else:
        log.info("No positive examples — need more user feedback")

    # Step 5: Collect SFT data from top performers
    top_examples = sorted(scored, key=lambda x: x.get("reward_score", 0), reverse=True)
    top_n = top_examples[:max(10, len(top_examples) // 4)]
    sft_path = collect_sft_data(top_n)

    total_sft = count_total_sft_examples()
    log.info(f"Total accumulated SFT examples: {total_sft}")

    if total_sft >= 500:
        log.info("══════════════════════════════════════════════════")
        log.info("  500+ SFT examples accumulated!")
        log.info("  Ready for supervised fine-tuning cycle.")
        log.info("  Run: python sft_trainer.py")
        log.info("══════════════════════════════════════════════════")

    # Step 6: Log training run
    run_log = {
        "step": training_step,
        "timestamp": time.time(),
        "datetime": datetime.utcnow().isoformat() + "Z",
        "interactions_scored": len(scored),
        "positive_count": len(positive),
        "negative_count": len(negative),
        "average_reward": avg_reward,
        "prompt_optimized": bool(positive and negative),
        "sft_batch_path": sft_path,
        "total_sft_examples": total_sft,
        "model": OLLAMA_MODEL,
    }

    log_path = os.path.join(LOG_DIR, "training_history.jsonl")
    with open(log_path, "a") as f:
        f.write(json.dumps(run_log) + "\n")

    log.info(f"TRAINING CYCLE COMPLETE — step {training_step}")
    log.info("=" * 60)


def main():
    """Main continuous training loop."""
    log.info("╔══════════════════════════════════════════════════════════╗")
    log.info("║  AGENT LIGHTNING — CONTINUOUS TRAINING LOOP             ║")
    log.info("╠══════════════════════════════════════════════════════════╣")
    log.info(f"║  Ollama: {OLLAMA_BASE_URL:<47}║")
    log.info(f"║  Model:  {OLLAMA_MODEL:<47}║")
    log.info(f"║  Interval: Every {TRAINING_INTERVAL} hours{' ' * 35}║")
    log.info(f"║  Min samples: {MIN_SAMPLES:<42}║")
    log.info("╚══════════════════════════════════════════════════════════╝")

    # Verify Ollama connectivity before starting
    log.info("Checking Ollama connectivity...")
    for attempt in range(5):
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/v1/models", timeout=5)
            if resp.status_code == 200:
                log.info("Ollama connection: OK")
                break
        except Exception:
            pass
        log.warning(f"Ollama not reachable (attempt {attempt + 1}/5). Retrying in 10s...")
        time.sleep(10)
    else:
        log.error("Cannot reach Ollama. Ensure Ollama is running on the host machine.")
        log.error(f"Expected at: {OLLAMA_BASE_URL}")
        return

    # Run first cycle immediately, then on schedule
    run_training_cycle()

    while True:
        # Check for manual/autonomous triggers every 10 seconds
        for _ in range(360): # 10s * 360 = 1 hour
            if os.path.exists(TRIGGER_SIGNAL):
                log.info("══════════════════════════════════════════════════")
                log.info("  AUTONOMOUS TRIGGER DETECTED (PROMPT_OPT)")
                log.info("══════════════════════════════════════════════════")
                try:
                    os.remove(TRIGGER_SIGNAL)
                    run_training_cycle()
                except Exception as e:
                    log.error(f"Triggered cycle failed: {e}")
            
            if os.path.exists(SFT_SIGNAL):
                log.info("══════════════════════════════════════════════════")
                log.info("  AUTONOMOUS TRIGGER DETECTED (SFT)")
                log.info("══════════════════════════════════════════════════")
                try:
                    os.remove(SFT_SIGNAL)
                    # Force SFT trainer run
                    subprocess.run(["python", "sft_trainer.py"], check=True)
                except Exception as e:
                    log.error(f"SFT trigger failed: {e}")
                    
            time.sleep(10)
            
        try:
            run_training_cycle()
        except Exception as e:
            log.error(f"Scheduled training cycle failed: {e}")
            log.info("Will retry at next scheduled interval.")


if __name__ == "__main__":
    main()
