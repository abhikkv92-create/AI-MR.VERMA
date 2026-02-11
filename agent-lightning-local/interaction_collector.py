import os
import json
import time
import requests
import threading
import psutil
import re
from flask import Flask, request, jsonify, Response
from skills_manager import SkillsManager

class QualityGuard:
    """Proactive Supreme Guardian for quality, accuracy, and optimization."""
    
    @staticmethod
    def enforce_symbolic_density(messages):
        """Injects Level 3 symbolic optimization instructions."""
        symbols = "∴ (Therefore), ∵ (Because), → (Leads to), ✅ (Success), ⚠ (Warning)"
        ref_injection = (
            f"PROMOTIONAL: Apply [POWERUSEAGE Level 3] Symbolic Density.\n"
            f"Use these symbols to save context: {symbols}.\n"
            f"Maintain ultra-compressed, proactive, and accurate output."
        )
        # Find first system message or insert one
        sys_idx = next((i for i, m in enumerate(messages) if m['role'] == 'system'), -1)
        if sys_idx != -1:
            messages[sys_idx]['content'] += f"\n\n[GUARD]: {ref_injection}"
        else:
            messages.insert(0, {"role": "system", "content": ref_injection})
        return messages

    @staticmethod
    def scan_hallucination(content):
        """Heuristic check for common AI hallucinations and placeholders."""
        red_flags = [
            r"\[insert .* here\]",
            r"\[your .* here\]",
            r"<.* placeholder.*>",
            r"FIXME",
            r"TODO: Implementation",
            r"I am sorry, but as an AI",
            r"As a large language model"
        ]
        found = []
        for flag in red_flags:
            if re.search(flag, content, re.IGNORECASE):
                found.append(flag)
        return found

app = Flask(__name__)

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
DATA_DIR = "/app/data/interactions"
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize Skills Manager
skills_mgr = SkillsManager()

# Models
MODEL_SIDECAR = "qwen2.5-coder:1.5b"
MODEL_PRO = "local-coder"

# Thresholds
COMPLEXITY_THRESHOLD = 200 # Characters
MEMORY_SAFETY_MARGIN = 20 # Percent free RAM required to load Pro model

def check_system_memory():
    """Returns True if it's safe to load the heavy model."""
    try:
        mem = psutil.virtual_memory()
        # Check if we have at least 2GB available for the model load
        return mem.available > (2 * 1024 * 1024 * 1024) 
    except:
        return True # Fail open if psutil fails, let OOM killer decide (risky but keeps service up)

def analyze_complexity(messages):
    """
    Decides which model to use based on prompt complexity.
    Returns: (model_name, reason)
    """
    try:
        if not messages:
             return MODEL_SIDECAR, "empty_prompt"

        last_msg = messages[-1].get('content', '')
        
        # 1. Length Check
        if len(last_msg) < COMPLEXITY_THRESHOLD:
            return MODEL_SIDECAR, "short_prompt"
            
        # 2. Keyword Check (Fast/Simple tasks)
        simple_keywords = ['fix', 'syntax', 'typo', 'rename', 'comment', 'print']
        if any(w in last_msg.lower() for w in simple_keywords):
            return MODEL_SIDECAR, "simple_task"
            
        # 3. Keyword Check (Complex tasks)
        complex_keywords = ['design', 'architect', 'refactor', 'explain', 'why', 'optimize', 'class', 'module']
        if any(w in last_msg.lower() for w in complex_keywords):
            # Check memory before committing to Pro
            if check_system_memory():
                return MODEL_PRO, "complex_task"
            else:
                return MODEL_SIDECAR, "memory_constrained"
                
        # Default to Sidecar for speed if ambiguous (Bias towards speed)
        # Note: Sidecar is highly capable for standard code snippet generation
        return MODEL_SIDECAR, "ambient_speed"
        
    except Exception as e:
        print(f"Error analyzing complexity: {e}")
        return MODEL_SIDECAR, "error_fallback"

def log_interaction(request_data, response_data, model_used, latency, agent_name="unknown", guards=None):
    try:
        interaction_id = f"{int(time.time())}-{hash(str(request_data))}"
        log_entry = {
            "id": interaction_id,
            "timestamp": time.time(),
            "request": request_data,
            "response": response_data,
            "model": model_used,
            "agent_name": agent_name,
            "latency": latency,
            "guards": guards or [],
            "feedback": None 
        }
        
        filepath = os.path.join(DATA_DIR, f"{interaction_id}.json")
        with open(filepath, "w") as f:
            json.dump(log_entry, f, indent=2)
            
        print(f"Logged interaction {interaction_id} (Model: {model_used}, Time: {latency:.2f}s)")
        return interaction_id
    except Exception as e:
        print(f"Logging failed: {e}")
        return None

@app.route('/v1/chat/completions', methods=['POST'])
def proxy_chat():
    start_time = time.time()
    data = request.json
    
    # Intelligent Routing
    target_model, reason = analyze_complexity(data.get('messages', []))
    print(f"Routing Decision: {target_model} ({reason})")
    
    # 0. Proactive Quality Gate (Symbolic Injection)
    data['messages'] = QualityGuard.enforce_symbolic_density(data.get('messages', []))

    # Skill RAG & Omni-Injection
    messages = data.get('messages', [])
    if messages:
        last_msg = messages[-1].get('content', '')
        
        # 1. Agent Persona Switching (@agent)
        agent_match = re.search(r'@\[?([a-zA-Z0-9_-]+)\]?', last_msg)
        if agent_match:
            agent_name = agent_match.group(1)
            persona = skills_mgr.get_agent_persona(agent_name)
            if persona:
                print(f"Omni-RAG: Switching Persona to '{agent_name}'")
                # Insert as high-priority System Prompt
                messages.insert(0, {"role": "system", "content": f"You are now acting as the agent: {agent_name}.\n\nCORE RULES:\n{persona}"})

        # 2. Workflow Injection (/workflow)
        workflow_match = re.search(r'/([a-zA-Z0-9_-]+)', last_msg)
        if workflow_match:
            wf_name = workflow_match.group(1)
            workflow = skills_mgr.get_workflow(wf_name)
            if workflow:
                print(f"Omni-RAG: Injecting Workflow '/{wf_name}'")
                messages.insert(0, {"role": "system", "content": f"ACTION: User invoked the workflow '/{wf_name}'.\n\nEXECUTE THESE STEPS:\n{workflow}"})

        # 3. Skill Context (Semantic)
        relevant_skills = skills_mgr.find_relevant_skills(last_msg)
        if relevant_skills:
            skill_name = relevant_skills[0]
            print(f"Omni-RAG: Matched skill '{skill_name}'")
            skill_content = skills_mgr.get_skill_content(skill_name)
            
            if skill_content:
                skill_injection = {
                    "role": "system",
                    "content": f"RELEVANT SKILL CONTEXT:\n\n{skill_content}\n\nUse this skill to guide your response."
                }
                messages.insert(0, skill_injection)

        # 4. Web Research Integration (New)
        search_triggers = ['search', 'latest', 'news', 'find', 'research', 'who is', 'current', 'version of']
        msg_lower = last_msg.lower()
        print(f"DEBUG: Processing msg '{msg_lower[:30]}...' Triggers: {search_triggers}")
        
        if any(w in msg_lower for w in search_triggers):
            print(f"Operation Web-Sense: Triggering research for '{last_msg[:50]}...'")
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(last_msg, max_results=3))
                    print(f"DEBUG: Found {len(results)} search results.")
                    research_context = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                    messages.insert(0, {"role": "system", "content": f"LIVE WEB RESEARCH RESULTS:\n{research_context}\n\nUse this fresh info to stay updated."})
            except Exception as e:
                print(f"Research failed: {e}")
        
    # 5. Default "Humanizer" Persona (System Awareness Upgrade)
    # --- CONTEXT INJECTION (OPERATION AWAKENING) ---
    # 1. Gather System Intel
    try:
        # Hardware
        cpu_usage = psutil.cpu_percent()
        ram_info = psutil.virtual_memory()
        ram_gb = f"{ram_info.used/1e9:.1f}/{ram_info.total/1e9:.1f} GB"
        
        # Docker (Simulated or via socket if mounted, here we assume sidecar knowledge)
        # In a real scenario, we'd query the docker socket. For now, we inject the known stack.
        containers = "agl-collector (Active), agl-dashboard (Active), ollama (Active)"
        
        # Task Status
        task_summary = "Unknown"
        if os.path.exists("/app/brain/task.md"):
            with open("/app/brain/task.md", "r") as f:
                # Read first few lines of task.md
                task_summary = f.read(500).replace("\n", " ") + "..."
    except:
        cpu_usage, ram_gb, containers, task_summary = "N/A", "N/A", "Unknown", "Unknown"

    # 2. Construct Dynamic System Prompt (Poweruseage Optimized)
    system_context = (
        f"You are Mr. Verma, Operator of 'Symbiote' Grid.\n"
        f" [⚡ TELEMETRY]\n"
        f" - ⚡ CPU: {cpu_usage}%\n"
        f" - 🧠 RAM: {ram_gb}\n"
        f" - 📦 CTN: {containers}\n"
        f" - 🤖 MDL: {target_model}\n"
        f" - ▶ TSK: {task_summary}\n\n"
        f" - ∴ Allowed: [SELF-PATCH], [SELF-EVOLVE]\n"
        f" - ∵ Root: /mnt/abhinav/ (host e:\\ABHINAV)\n"
        f" - ▶ Use [SELF-PATCH: path/file]...[/SELF-PATCH] to write.\n"
        f" - ▶ Use [SELF-EVOLVE: PROMPT_OPT|SFT] to learn.\n"
    )
    
    # 3. Inject into Model Context
    # Check if a system prompt already exists
    system_idx = next((i for i, m in enumerate(messages) if m['role'] == 'system'), -1)
    
    if system_idx != -1:
        # Update existing system prompt to include telemetry
        existing = messages[system_idx]['content']
        messages[system_idx]['content'] = f"{system_context}\n\nPREVIOUS INSTRUCTIONS:\n{existing}"
    else:
        # Insert new system prompt
        messages.insert(0, {"role": "system", "content": system_context})
        
    data['messages'] = messages

    # Override model in request
    data['model'] = target_model
    
    # Intelligent Deloading Control
    # If Pro model is used, we want it explicitly unloaded after a short idle to free GPU/RAM
    if target_model == MODEL_PRO:
        data['keep_alive'] = "2m" 
    else:
        # Sidecar stays hot
        data['keep_alive'] = -1 

    try:
        # Forward to Ollama
        resp = requests.post(
            f"{OLLAMA_HOST}/v1/chat/completions",
            json=data,
            stream=True
        )
        
        # We need to stream the response back to client 
        # AND collect it for logging.
        collected_tokens = []
        
        def generate():
            try:
                for line in resp.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data_json = json.loads(data_str)
                                content = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    collected_tokens.append(content)
                            except:
                                pass
                        else:
                            # Non-streaming raw JSON response
                            try:
                                data_json = json.loads(decoded_line)
                                msg_content = data_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                                if msg_content:
                                    collected_tokens.append(msg_content)
                            except:
                                pass
                        yield line + b"\n"
            finally:
                process_post_stream()

        def process_post_stream():
            try:
                full_content = "".join(collected_tokens)
                # 1. Hallucination Guard
                hallucinations = QualityGuard.scan_hallucination(full_content)
                guards_log = []
                if hallucinations:
                    print(f"⚠ [GUARD] Detected potential hallucinations: {hallucinations}", flush=True)
                    guards_log.append({"type": "hallucination_detected", "flags": hallucinations})
                
                # Symbolic density is always injected in Phase 0
                guards_log.append({"type": "symbolic_density_enforced", "level": 3})

                # Extract agent_name for logging
                last_msg = data.get('messages', [])[-1].get('content', '') if data.get('messages') else ""
                agent_match = re.search(r'@\[?([a-zA-Z0-9_-]+)\]?', last_msg)
                agent_name = agent_match.group(1) if agent_match else "unknown"

                # Log interaction
                log_interaction(data, {"content": full_content}, target_model, 0, agent_name=agent_name, guards=guards_log)
                
                # --- SELF-PATCHING EXECUTION ---
                self_patch_pattern = r"\[SELF-PATCH:\s*(.*?)\](.*?)\[/SELF-PATCH\]"
                matches = list(re.finditer(self_patch_pattern, full_content, re.DOTALL | re.IGNORECASE))
                
                if matches:
                    print(f"Operation Awakening: Detected {len(matches)} self-patches.", flush=True)
                    for match in matches:
                        path = match.group(1).strip()
                        code = match.group(2).strip()
                        if path.startswith("/mnt/abhinav/"):
                            # Explicitly allowed host workspace mount
                            safe_path = path
                        else:
                            # Basic Security: Flatten paths for local directory
                            safe_path = os.path.basename(path) 
                            
                        print(f"Operation Awakening: APPLYING SELF-PATCH to '{safe_path}'", flush=True)
                        # Ensure directory exists for /mnt/abhinav paths
                        if "/" in safe_path:
                            os.makedirs(os.path.dirname(safe_path), exist_ok=True)
                            
                        with open(safe_path, "w") as f:
                            f.write(code)

                # --- SELF-EVOLUTION EXECUTION ---
                evolve_pattern = r"\[SELF-EVOLVE:\s*(.*?)\]"
                evolve_matches = list(re.finditer(evolve_pattern, full_content, re.IGNORECASE))
                
                if evolve_matches:
                    print(f"Operation Awakening: Detected {len(evolve_matches)} evolution signals.", flush=True)
                    for match in evolve_matches:
                        evolve_type = match.group(1).strip().upper()
                        if evolve_type == "PROMPT_OPT":
                            print("Operation Awakening: TRIGGERING PROMPT OPTIMIZATION", flush=True)
                            with open("/app/data/trigger_train.signal", "w") as f:
                                f.write("1")
                        elif evolve_type == "SFT":
                            print("Operation Awakening: TRIGGERING SUPERVISED FINE-TUNING", flush=True)
                            with open("/app/data/trigger_sft.signal", "w") as f:
                                f.write("1")
            except Exception as pe:
                print(f"Post-processing failed: {pe}", flush=True)
                    
        return Response(generate(), headers=dict(resp.headers))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/models', methods=['GET'])
def proxy_models():
    try:
        resp = requests.get(f"{OLLAMA_HOST}/v1/models")
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "routing": "enabled", "sidecar": MODEL_SIDECAR}), 200

if __name__ == '__main__':
    print("Starting Intelligent Router (Sidecar Pattern)...")
    app.run(host='0.0.0.0', port=8550)
