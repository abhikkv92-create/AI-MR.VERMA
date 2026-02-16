# AGENTS.md - Symbiote Grid Context

This project, **Mr. Verma (Agent Lightning Local)**, is an autonomous AI grid integrated with local LLMs and self-improvement capabilities.

## Operating Principles
- **Autonomous Patching**: The system can write code to its own filesystem using `[SELF-PATCH]` tags.
- **Self-Evolution**: A trigger system allows the LLM to initiate its own training cycles.
- **System Awareness**: Real-time telemetry (CPU, RAM, Docker) is injected into every interaction.
- **Web-Sense**: Integrated DuckDuckGo search for real-time RAG.

## Project Structure
- `interaction_collector.py`: The core proxy and patching engine.
- `train_loop.py`: The autonomous training orchestrator.
- `sft_trainer.py`: LoRA fine-tuning logic.
- `docker-compose.yml`: Multi-service orchestration (Collector, Trainer, Dashboard).

## Coding Standards
- Python 3.11+
- Async/Streaming response handling
- permissive Docker volume mounts for host agency
- JSON-based configuration management
