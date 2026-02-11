---
description: Documentation foundry for technical specs, plans, and user guides. Activates knowledge-expert.
---

# /docs-engine - Knowledge & Documentation Foundry

$ARGUMENTS: [doc_type]

## 🤖 Applied Agents: `knowledge-expert`, `documentation-writer`

This workflow transforms raw information into structured, high-quality documentation.

## 🛠️ Skills Activated
- **Creation:** `doc-coauthoring`, `writing-plans`, `documentation-templates`
- **Communication:** `internal-comms`, `brand-guidelines`, `email-sequence`
- **Marketing:** `free-tool-strategy`, `geo-fundamentals`, `seo-fundamentals`
- **Knowledge:** `knowledge-expert`, `synthesize`


## 📋 Step-by-Step Execution

1.  **Template Selection**
    - Agent: `knowledge-expert`
    - Action: Select appropriate template from `documentation-templates`.
    - Type: README, ADR, API Spec, User Guide, PRD.

2.  **Content Synthesis**
    - Agent: `knowledge-expert`
    - Action: Synthesize codebase info and user input using `doc-coauthoring`.
    - Tone: Apply `brand-guidelines`.

3.  **Structural Refinement**
    - Agent: `documentation-writer`
    - Action: Ensure clarity, formatting, and SEO (if public).
    - Check: Links, diagrams (`mermaid`), examples.

4.  **Knowledge Integration**
    - Action: Update project Knowledge Items (KIs) with new findings.

---

## 🚦 Output Format
Produces professional Markdown documentation artifacts.
