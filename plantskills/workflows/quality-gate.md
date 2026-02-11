---
description: Code quality enforcement and testing engine. Activates test-engineer and agent-perfectionist.
---

# /quality-gate - Code Quality & Testing Engine

$ARGUMENTS: [scope]

## 🤖 Applied Agents: `test-engineer`, `agent-perfectionist`

This workflow serves as the final checkpoint for code quality, testing, and standard enforcement.

## 🛠️ Skills Activated
- **Code hygiene:** `clean-code`, `code-review-excellence`, `simplify`
- **Testing:** `testing-patterns`, `e2e-testing-patterns`, `tdd-workflow`
- **Verification:** `lint-and-validate`, `verification-before-completion`

## 📋 Step-by-Step Execution

1.  **Code Review & Simplification**
    - Agent: `agent-perfectionist`
    - Action: Apply `simplify` to reduce complexity.
    - Check: Adherence to `clean-code` standards (naming, functions < 20 lines).

2.  **Test Coverage Assurance**
    - Agent: `test-engineer`
    - Action: Generate missing unit/E2E tests using `testing-patterns`.
    - Tool: `playwright-skill` for browser automation testing.

3.  **Automated Validation**
    - Script: `python .agent/scripts/lint_runner.py`
    - Script: `python .agent/scripts/test_runner.py`

4.  **Final Polish & Reward**
    - Action: Run `checklist.py`.
    - Gate: ALL PASS required.
    - **Learning Loop**:
      ```python
      # If checklist passes -> emit 1.0 reward
      emit_reward(1.0, {"source": "quality_gate", "score": "perfect"})
      ```


---

## 🚦 Output Format
Produces a **Quality Report** and refactored, tested code.
