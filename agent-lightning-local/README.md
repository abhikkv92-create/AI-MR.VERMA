# Agent Lightning: Self-Improving Local LLM System

## Overview
This project implements an autonomous self-improving LLM system using **Ollama** (inference), **Agent Lightning** (training), and **Docker** (orchestration). The system continuously learns from interactions, optimizing its system prompt and fine-tuning the model based on reward signals.

## Architecture

1.  **Inference Engine**: Ollama serving `local-coder` (based on `qwen2.5-coder:7b`).
2.  **Interaction Proxy**: Intercepts all LLM traffic at port **8550**, logs data, and forwards to Ollama.
3.  **Reward Engine**: Scores interactions based on:
    -   User Feedback (Good/Bad)
    -   Code Adoption
    -   Syntax Validity
    -   Latency & Completeness
4.  **Training Loop**:
    -   **Prompt Optimization**: Updates system prompt based on positive examples (every 6 hours).
    -   **Supervised Fine-Tuning (SFT)**: Fine-tunes the model using LoRA when 500+ high-quality examples are collected.
5.  **Dashboard**: Visualizes training metrics at port **8551**.

## Prerequisites
-   Windows 10/11 with WSL 2
-   Docker Desktop
-   Ollama installed locally
-   16GB+ RAM

## Setup & Run

1.  **Install/Update Ollama**:
    Ensure Ollama is running and the model is available:
    ```bash
    ollama pull qwen2.5-coder:7b
    ollama create local-coder -f Modelfile.base
    ```

2.  **Start the System**:
    ```bash
    cd agent-lightning-local
    docker compose up -d --build
    ```

3.  **Verify**:
    Run the verification script:
    ```bash
    python verify_system.py
    ```

## Usage

### 1. Connect your App
Point your IDE or application's LLM endpoint to:
-   **URL**: `http://localhost:8550/v1/chat/completions` (instead of 11434)
-   **Model**: `local-coder`

### 2. Monitor
Open the dashboard at [http://localhost:8551](http://localhost:8551).

### 3. Provide Feedback
To improve the model, submit feedback for interactions:
```bash
# Get interaction ID from dashboard or logs
docker exec agl-collector python scripts/submit_feedback.py <INTERACTION_ID> <good|bad|adopted|rejected>
```

## Directory Structure
-   `data/interactions`: Logged request/response pairs.
-   `data/rewards`: Computed reward scores.
-   `data/sft_batches`: Collected training examples.
-   `checkpoints`: Saved model adapters and modelfiles.
-   `logs`: System logs.
