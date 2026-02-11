---
description: Military-grade security sweep with red team simulation and infrastructure hardening.
---

# /secure-audit - Deep Security Review

$ARGUMENTS: [target_url | codebase_path]

## 🤖 Applied Agents: `security-auditor`, `penetration-tester`, `devops-engineer`

This workflow performs a military-grade security sweep of the application and infrastructure.

## 🛠️ Step-by-Step Execution

1.  **Attack Surface Mapping**
    - Agent: `security-auditor`
    - Action: Run `vulnerability-scanner`.
    - Output: List of exposed endpoints and dependencies.

2.  **Red Team Simulation**
    - Agent: `penetration-tester`
    - Action: Apply `red-team-tactics` skill.
    - Simulation: Attempt common exploits (SQLi, XSS, IDOR).

3.  **Infrastructure Hardening**
    - Agent: `devops-engineer`
    - Action: Review `docker-expert` and `server-management` configs.
    - Check: FW rules, secret management, CI/CD capability.

4.  **Verification Scan**
    - Agent: `security-auditor`
    - Action: Execute `security_scan.py` and `audit-website`.

---

## 🚦 Output Format

Produces a **Security Audit Report** with CVSS scores and remediation steps.
