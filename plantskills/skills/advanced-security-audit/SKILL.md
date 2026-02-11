# 🔒 advanced-security-audit - Rigorous Production Security

> **Antigravity Skill** - Deep protection based on OWASP 2025 and Agentic Security.

- **Objective**: Automated exploit detection, secrets management, and dependency auditing.
- **Core Technology**: Integrated with `vulnerability-scanner`.

## 🛠️ Operational Protocol

### 1. Static Analysis
Run `security_scan.py` on every major code change.
```bash
python .agent/skills/vulnerability-scanner/scripts/security_scan.py .
```

### 2. Dynamic Secret Detection
Audits `.env` files and CI logs for leaked credentials.

### 3. Dependency Shield
Checks `uv.lock` or `package-lock.json` against known CVE databases.

## 🚦 Rule: Zero Criticals
No deployment workflow (`/deploy`) can proceed if a **Critical** or **High** severity issue is found.
