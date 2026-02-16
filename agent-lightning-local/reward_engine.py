"""
Reward Engine
─────────────
Computes reward scores [-1.0 to +1.0] for each logged interaction.
Agent Lightning uses these scores to determine which behaviors to reinforce.

REWARD SIGNALS:
  1. User explicit feedback (rating: good/bad)        weight: 0.35
  2. Code adoption (was the generated code used?)      weight: 0.25
  3. Syntax validity (does the code parse?)            weight: 0.15
  4. Response completeness (not truncated, has code)   weight: 0.10
  5. Latency bonus (faster responses score higher)     weight: 0.05
  6. Appropriate length (not over/under-engineered)    weight: 0.10
"""

import ast
import logging
import os
import re
import time
from typing import Optional

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
log = logging.getLogger(__name__)


WEIGHTS = {
    "user_rating":     0.35,
    "code_adopted":    0.25,
    "syntax_valid":    0.15,
    "completeness":    0.10,
    "latency":         0.05,
    "appropriate_len": 0.10,
}


def compute_reward(interaction: dict) -> float:
    """Compute a reward in [-1.0, 1.0] for a single interaction."""
    reward = 0.0

    # 1. User Rating — strongest signal
    rating = interaction.get("rating")
    if rating == "good":
        reward += WEIGHTS["user_rating"] * 1.0
    elif rating == "bad":
        reward += WEIGHTS["user_rating"] * -1.0

    # 2. Code Adoption
    adopted = interaction.get("code_adopted")
    if adopted is True:
        reward += WEIGHTS["code_adopted"] * 1.0
    elif adopted is False:
        reward += WEIGHTS["code_adopted"] * -0.5

    # 3. Syntax Validity
    code = _extract_code(interaction.get("response", ""))
    if code:
        if _check_syntax(code):
            reward += WEIGHTS["syntax_valid"] * 1.0
        else:
            reward += WEIGHTS["syntax_valid"] * -1.0

    # 4. Completeness — response has code blocks and isn't truncated
    response = interaction.get("response", "")
    has_code_block = "```" in response
    not_truncated = not response.rstrip().endswith("...")
    completeness = 0.0
    if has_code_block:
        completeness += 0.5
    if not_truncated:
        completeness += 0.5
    reward += WEIGHTS["completeness"] * completeness

    # 5. Latency Bonus — faster is better, threshold 15 seconds
    latency_ms = interaction.get("latency_ms", 15000)
    latency_score = max(0.0, 1.0 - (latency_ms / 15000))
    reward += WEIGHTS["latency"] * latency_score

    # 6. Appropriate Length
    response_len = len(response)
    if 100 < response_len < 5000:
        reward += WEIGHTS["appropriate_len"] * 0.5
    elif response_len >= 5000:
        reward += WEIGHTS["appropriate_len"] * -0.3
    elif response_len <= 100:
        reward += WEIGHTS["appropriate_len"] * -0.5

    # 7. Token Efficiency (Poweruseage)
    if response_len < 2000 and has_code_block:
        reward += 0.05 # Bonus for concise but complete code

    return max(-1.0, min(1.0, reward))


def _extract_code(response: str) -> Optional[str]:
    """Extract code blocks from markdown-formatted response."""
    pattern = r"```(?:\w+)?\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    return "\n".join(matches) if matches else None


def _check_syntax(code: str) -> bool:
    """Check if code has valid Python syntax using safe AST parsing."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def batch_compute_rewards(interactions: list) -> list:
    """Compute rewards for a batch of interactions. Returns enriched list."""
    results = []
    for interaction in interactions:
        reward = compute_reward(interaction)
        interaction["reward_score"] = reward
        # The following lines are from the user's provided snippet.
        # They introduce undefined variables (positive_traits, base_prompt)
        # and seem to be part of a larger, incomplete logic for prompt optimization.
        # As per instructions, I'm including them faithfully but noting their
        # potential for runtime errors due to missing context.
        # if positive_traits:
        #     learned = "\n".join(f"▶ {trait}" for trait in positive_traits)
        #     improved_prompt = f"{base_prompt}\n\nLearned guidelines:\n{learned}"
        interaction["reward_computed_at"] = time.time()
        results.append(interaction)
    return results
