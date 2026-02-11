# 🧪 vibe-check-tdd - AI-Enforced Test Driven Development

> **Antigravity Skill** - Integrated with Agent Lightning for reward-based TDD verification.

- **Objective**: Enforce the RED-GREEN-REFACTOR cycle with automated trace rewards.
- **Logic**: Every test run posts its results to the Lightning Store. Failed tests result in `emit_reward(0.0)`, passed tests in `emit_reward(1.0)`.

## 🛠️ Usage Patterns

### 1. The Red Phase
Identify the missing functionality and write a test that fails.
```bash
python .agent/skills/tdd-workflow/scripts/test_runner.py --phase red
```

### 2. The Green Phase
Implement the minimum code needed to make the test pass.
```bash
python .agent/skills/tdd-workflow/scripts/test_runner.py --phase green
```

### 3. The Refactor Phase
Clean up the code while ensuring tests stay green.
```bash
python .agent/skills/tdd-workflow/scripts/test_runner.py --phase refactor
```

## ⚡ Agent Lightning Integration
The `tdd_logger.py` script automatically sends traces to `http://localhost:4747`.
- **Trace Key**: `tdd_cycle`
- **Metadata**: Phase name, test result, code coverage.
