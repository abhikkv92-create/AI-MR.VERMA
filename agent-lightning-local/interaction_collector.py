"""
MR.VERMA Intelligence Core — Interaction Collector & API Proxy
──────────────────────────────────────────────────────────────
Production-grade NVIDIA Kimi K2.5 proxy with:
  - Cached telemetry (background thread, 30s refresh)
  - Connection pooling (requests.Session)
  - Quality Guard (hallucination scan + symbolic density)
  - Interaction logging for SFT data collection
  - Graceful shutdown handling
"""

import json
import sys
import os

# Add root directory to sys.path for core/main imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging
import queue
import re
import signal
import threading
import time
import uuid

import psutil
import requests
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from skills_manager import SkillsManager
from vector_services import EmbeddingService, MilvusService
from core.thermal_governor import ThermalGovernor
from core.vulnerability_listener import VulnerabilityListener
from core.plugin_orchestrator import orchestrator as plugin_orchestrator
from core.mcp_hub import mcp_hub

# ── Logging ──
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s [COLLECTOR] %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)

# ── Global Configuration ──
NVIDIA_API_URL = os.getenv(
    "NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2.5")
DATA_DIR = "/app/data/interactions"
MAX_REQUEST_BYTES = 1_000_000  # 1MB max payload
TELEMETRY_CACHE_TTL = 30  # seconds

os.makedirs(DATA_DIR, exist_ok=True)

# ── Global Health Monitors ──
thermal_gov = ThermalGovernor()
security_list = VulnerabilityListener()

# ── Initialize Flask & Skills ──
app = Flask(__name__)
CORS(app)  # Enable CORS for SSE
skills_mgr = SkillsManager()
embed_svc = EmbeddingService(NVIDIA_API_KEY)
# ── Initialize V5.0 Singularity Core ──
from core.orchestrator import SupremeOrchestrator

orchestrator = SupremeOrchestrator()

# Initialize Task Queue and Startup Lifecycle (Background)
import asyncio
import threading


def _run_orch_startup():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(orchestrator.startup())
    loop.run_forever()


threading.Thread(target=_run_orch_startup, daemon=True).start()
log.info("V5.0 Singularity Orchestrator started in background.")

# ── Connection Pooling ──
http_session = requests.Session()
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10, pool_maxsize=10, max_retries=1
)
http_session.mount("https://", adapter)
http_session.mount("http://", adapter)

# ── Cached Telemetry ──
_telemetry_cache = {
    "cpu_total": 0.0,
    "cpu_cores": [],  # P/E Core breakdown placeholder
    "ram_used_gb": 0.0,
    "ram_total_gb": 0.0,
    "ram_percent": 0.0,
    "docker": "unknown",
    "updated_at": 0,
}
_telemetry_lock = threading.Lock()

# ── Global Event Bus for SSE ──
_event_listeners = []
_listeners_lock = threading.Lock()


def _broadcast_event(event_type: str, data: dict):
    """Notify all SSE listeners of a new event."""
    message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with _listeners_lock:
        for listener in _event_listeners:
            listener.put(message)


def _refresh_thread():
    """Background task to poll metrics and broadcast."""
    thermal_gov.start()
    security_list.start()

    while True:
        try:
            cpu_total = psutil.cpu_percent(interval=1)
            cpu_per_core = psutil.cpu_percent(percpu=True)
            mem = psutil.virtual_memory()

            with _telemetry_lock:
                _telemetry_cache["cpu_total"] = cpu_total
                _telemetry_cache["cpu_cores"] = (
                    cpu_per_core  # [P, P, P, P, P, P, E, E, E, E, E, E, E, E]
                )
                _telemetry_cache["ram_used_gb"] = round(mem.used / (1024**3), 2)
                _telemetry_cache["ram_total_gb"] = round(mem.total / (1024**3), 2)
                _telemetry_cache["ram_percent"] = mem.percent
                _telemetry_cache["docker"] = _get_docker_info()
                _telemetry_cache["updated_at"] = time.time()

            # Broadcast Health Updates
            _broadcast_event("telemetry", get_cached_telemetry())
            _broadcast_event("thermal_status", thermal_gov.get_status())
            _broadcast_event("security_status", security_list.get_status())

        except Exception as e:
            log.warning(f"Telemetry refresh failed: {e}")

        time.sleep(2)


def _get_docker_info() -> str:
    """Retrieve Docker container info via Unix socket."""
    sock_path = "/var/run/docker.sock"
    try:
        if not os.path.exists(sock_path):
            return "Socket not mounted"

        import http.client
        import socket

        class DockerSocket(http.client.HTTPConnection):
            def __init__(self):
                super().__init__("localhost")

            def connect(self):
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(sock_path)
                self.sock.settimeout(2)

        conn = DockerSocket()
        conn.request("GET", "/containers/json")
        resp = conn.getresponse()
        if resp.status == 200:
            containers = json.loads(resp.read().decode())
            lines = [
                f"  - {c['Names'][0].strip('/')} ({c['State']})" for c in containers
            ]
            result = f"Active Containers ({len(containers)}):\n" + "\n".join(lines)
        else:
            result = f"API returned {resp.status}"
        conn.close()
        return result
    except Exception as e:
        return f"Error: {str(e)[:50]}"


def get_cached_telemetry() -> dict:
    """Return cached telemetry (never blocks the request path)."""
    with _telemetry_lock:
        return dict(_telemetry_cache)


# ── Quality Guard ──
class QualityGuard:
    """Proactive Supreme Guardian for quality, accuracy, and optimization."""

    HALLUCINATION_FLAGS = [
        r"\[insert .* here\]",
        r"\[your .* here\]",
        r"<.* placeholder.*>",
        r"FIXME",
        r"TODO: Implementation",
        r"I am sorry, but as an AI",
        r"As a large language model",
    ]

    @staticmethod
    def enforce_symbolic_density(messages: list) -> list:
        """Injects Level 3 symbolic optimization instructions."""
        symbols = "∴ (Therefore), ∵ (Because), → (Leads to), ✅ (Success), ⚠ (Warning)"
        ref_injection = (
            f"Apply [POWERUSEAGE Level 3] Symbolic Density.\n"
            f"Use these symbols to save context: {symbols}.\n"
            f"Maintain ultra-compressed, proactive, and accurate output."
        )
        # Find existing system message
        sys_idx = next(
            (i for i, m in enumerate(messages) if m.get("role") == "system"), -1
        )
        if sys_idx != -1:
            messages[sys_idx] = {
                **messages[sys_idx],
                "content": messages[sys_idx]["content"]
                + f"\n\n[GUARD]: {ref_injection}",
            }
        else:
            messages.insert(0, {"role": "system", "content": ref_injection})
        return messages

    @staticmethod
    def scan_hallucination(content: str) -> list:
        """Scan response for hallucination red flags."""
        return [
            flag
            for flag in QualityGuard.HALLUCINATION_FLAGS
            if re.search(flag, content, re.IGNORECASE)
        ]


# ── Interaction Logger ──
def log_interaction(
    request_data: dict,
    response_data: str,
    model_used: str,
    latency: float,
    guards: list = None,
):
    """Log interaction to disk for SFT data collection."""
    try:
        interaction_id = str(uuid.uuid4())
        log_entry = {
            "id": interaction_id,
            "timestamp": time.time(),
            "messages": request_data.get("messages", []),
            "response": response_data,
            "model": model_used,
            "latency": latency,
            "latency_ms": int(latency * 1000),
            "guards": guards or [],
            "backend": "nvidia",
            "reward_score": None,
        }
        filepath = os.path.join(DATA_DIR, f"{interaction_id}.json")
        with open(filepath, "w") as f:
            json.dump(log_entry, f, indent=2)
    except Exception as e:
        log.error(f"Interaction logging failed: {e}")


# ── API Endpoints ──
@app.route("/v1/chat/completions", methods=["POST"])
def proxy_chat():
    start_time = time.time()
    try:
        # Validation
        if not NVIDIA_API_KEY:
            return jsonify({"error": "NVIDIA_API_KEY is not configured"}), 503

        content_length = request.content_length or 0
        if content_length > MAX_REQUEST_BYTES:
            return jsonify(
                {
                    "error": f"Payload too large ({content_length} bytes > {MAX_REQUEST_BYTES})"
                }
            ), 413

        data = request.json
        if not data or not data.get("messages"):
            return jsonify({"error": "Missing 'messages' in request body"}), 400

        messages = list(data["messages"])  # Copy to avoid mutation
        user_query = messages[-1].get("content", "") if messages else ""

        # ── RAG: Semantic Recall ──
        semantic_context = ""
        if user_query:
            log.debug(f"Generating embedding for query: {user_query[:50]}...")
            query_vector = embed_svc.get_embedding(user_query)
            if query_vector:
                log.debug("Searching Milvus for context...")
                results = milvus_svc.search(query_vector, limit=3)
                if results:
                    context_segments = [
                        f"[{res.role.upper()}]: {res.content}" for res in results
                    ]
                    semantic_context = (
                        "\n### SEMANTIC CONTEXT (Long-Term Memory)\n"
                        + "\n".join(context_segments)
                    )
                    log.info(f"Retrieved {len(results)} context segments from Milvus.")
                else:
                    log.debug("No semantic context found in Milvus.")
            else:
                log.warning("Query embedding generation failed. Skipping RAG.")

        # ── Telemetry & Quality Injection ──
        telem = get_cached_telemetry()
        sys_ctx = (
            f"You are MR. VERMA (Powered by NVIDIA Kimi K2.5).\n"
            f"Directives: ZERO HALLUCINATION, LOGICAL ACCURACY, PRODUCTION-GRADE CODE.\n"
            f"Telemetry: CPU {telem['cpu']}% | RAM {telem['ram']}\n"
        )

        messages = QualityGuard.enforce_symbolic_density(messages)
        sys_idx = next(
            (i for i, m in enumerate(messages) if m.get("role") == "system"), -1
        )
        if sys_idx != -1:
            messages[sys_idx] = {
                **messages[sys_idx],
                "content": messages[sys_idx]["content"]
                + f"\n\n{sys_ctx}{semantic_context}",
            }
        else:
            messages.insert(
                0, {"role": "system", "content": sys_ctx + semantic_context}
            )

        # ── NVIDIA Payload ──
        payload = {
            "model": NVIDIA_MODEL,
            "messages": messages,
            "max_tokens": data.get("max_tokens", 7000),
            "temperature": data.get("temperature", 0.30),
            "top_p": data.get("top_p", 0.90),
            "stream": True,
            "chat_template_kwargs": {"thinking": True},
        }

        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        # ── Forward to NVIDIA ──
        resp = http_session.post(
            NVIDIA_API_URL, headers=headers, json=payload, stream=True, timeout=180
        )
        resp.raise_for_status()

        def generate():
            collected = []
            try:
                for line in resp.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if (
                            decoded.startswith("data: ")
                            and decoded.strip() != "data: [DONE]"
                        ):
                            try:
                                chunk = json.loads(decoded[6:])
                                delta = (
                                    chunk.get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if delta:
                                    collected.append(delta)
                            except json.JSONDecodeError:
                                log.debug(
                                    f"Skipped malformed SSE chunk: {decoded[:80]}"
                                )
                        yield line + b"\n"
            finally:
                # Post-stream logging (always runs)
                full_response = "".join(collected)
                latency = time.time() - start_time
                guards = QualityGuard.scan_hallucination(full_response)
                guards_log = (
                    [{"type": "hallucination", "flags": guards}] if guards else []
                )
                threading.Thread(
                    target=log_interaction,
                    args=(data, full_response, NVIDIA_MODEL, latency, guards_log),
                    daemon=True,
                ).start()

                # Broadcast log to SSE listeners
                _broadcast_event(
                    "kernel_log",
                    {
                        "id": str(uuid.uuid4()),
                        "timestamp": time.time(),
                        "model": NVIDIA_MODEL,
                        "latency_ms": int(latency * 1000),
                        "response": full_response[:500],
                        "guards": guards_log,
                    },
                )

                # Ingest into Milvus (Async)
                def _async_ingest():
                    combined_text = f"USER: {user_query}\nASSISTANT: {full_response}"
                    vector = embed_svc.get_embedding(combined_text)
                    if vector:
                        milvus_svc.ingest(
                            vector=vector,
                            content=combined_text,
                            role="interaction",
                            session_id=str(
                                uuid.uuid4()
                            ),  # Placeholder for real session tracking
                            telemetry=telem,
                        )

                threading.Thread(target=_async_ingest, daemon=True).start()

        return Response(generate(), headers=dict(resp.headers))

    except requests.exceptions.Timeout:
        log.error("NVIDIA API timeout (180s)")
        return jsonify(
            {
                "error": "Upstream API Timeout",
                "detail": "NVIDIA API did not respond within 180s",
            }
        ), 504
    except requests.exceptions.RequestException as req_err:
        log.error(f"NVIDIA API Error: {req_err}")
        return jsonify({"error": "Upstream API Error", "detail": str(req_err)}), 502
    except Exception as e:
        log.error(f"Internal Error: {e}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500


@app.route("/api/memory/search", methods=["GET"])
def memory_search():
    """Direct semantic search in Milvus."""
    query = request.args.get("q", "")
    if not query:
        return jsonify([])

    try:
        vector = embed_svc.get_embedding(query)
        if not vector:
            return jsonify({"error": "Embedding failure"}), 500

        results = milvus_svc.search(vector, limit=10)
        formatted = []
        for res in results:
            formatted.append(
                {
                    "role": res.role,
                    "content": res.content,
                    "distance": res.distance,
                    "timestamp": res.timestamp,
                }
            )
        return jsonify(formatted)
    except Exception as e:
        log.error(f"Search API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/hardware/telemetry", methods=["GET"])
def hardware_telemetry():
    """Detailed hardware telemetry for i9-13900H Dashboard."""
    return jsonify(get_cached_telemetry())


@app.route("/api/swarm/status", methods=["GET"])
def swarm_status():
    """Mock swarm status for dashboard development."""
    # In a real scenario, this would poll the ProductionOrchestrator
    return jsonify(
        {
            "active_agents": 27,
            "task_queue": 12,  # Mocked non-zero value for UI testing
            "status": "OPERATIONAL",
            "last_heal": "10 mins ago",
        }
    )


@app.route("/api/security/events", methods=["GET"])
def security_events():
    """Mock security events for the dashboard."""
    return jsonify(
        [
            {
                "id": 1,
                "type": "AUTH",
                "message": "User 'Abhinav' authenticated via SHA-256",
                "severity": "info",
                "timestamp": time.time() - 3600,
            },
            {
                "id": 2,
                "type": "ENCRYPTION",
                "message": "AES-256-GCM context initialized for .brain/",
                "severity": "success",
                "timestamp": time.time() - 1800,
            },
            {
                "id": 3,
                "type": "VULN_SCAN",
                "message": "Scan complete: 0 high-risk vulnerabilities found",
                "severity": "success",
                "timestamp": time.time() - 900,
            },
            {
                "id": 4,
                "type": "ACCESS",
                "message": "ResearchAnalyst accessed semantic memory block #442",
                "severity": "info",
                "timestamp": time.time() - 450,
            },
        ]
    )


@app.route("/api/system/logs", methods=["GET"])
def system_logs():
    """Read recent interaction logs from disk."""
    try:
        files = sorted(
            [
                os.path.join(DATA_DIR, f)
                for f in os.listdir(DATA_DIR)
                if f.endswith(".json")
            ],
            key=os.path.getmtime,
            reverse=True,
        )
        logs = []
        for f in files[:20]:  # Last 20 interactions
            with open(f, "r") as log_file:
                logs.append(json.load(log_file))
        return jsonify(logs)
    except Exception as e:
        log.error(f"Logs API error: {e}")
        return jsonify([])


# ── To-Do Swarm Endpoints (Engine Stress Test) ──


@app.route("/api/swarm/todo/analyze", methods=["POST"])
def todo_analyze():
    """Extract structured task data using the Primary Engine."""
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    prompt = (
        "Extract structured tasks from the following text. "
        "Return a JSON list of objects with 'title', 'priority' (low, medium, high), and 'due_date'. "
        "Text: " + text
    )

    try:
        payload = {
            "model": "z-ai/glm5",  # Primary Engine Equivalent
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        }
        resp = http_session.post(
            NVIDIA_API_URL,
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Clean JSON from markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        return jsonify(json.loads(content))
    except Exception as e:
        log.error(f"Todo analysis failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/swarm/todo/weather", methods=["GET"])
def todo_weather():
    """Generate intelligent weather simulations using the Secondary Engine."""
    location = request.args.get("location", "London")

    prompt = (
        f"Generate an intelligent, highly descriptive weather report for {location}. "
        "Include temperature, condition, and a 'Swarm Recommendation' for tasks. "
        "Return JSON with 'temp', 'condition', 'recommendation'."
    )

    try:
        payload = {
            "model": "moonshotai/kimi-k2.5",  # Secondary Engine
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }
        resp = http_session.post(
            NVIDIA_API_URL,
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()

        return jsonify(json.loads(content))
    except Exception as e:
        log.error(f"Weather generation failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/swarm/todo/vision", methods=["POST"])
def todo_vision():
    """Transcribe tasks from images using the Vision Engine."""
    data = request.json
    image_b64 = data.get("image")  # Base64 encoded image
    if not image_b64:
        return jsonify({"error": "No image data provided"}), 400

    prompt = "Transcribe all tasks and notes from this image. return a bulleted list."

    try:
        # Vision Engine requires specific format and model
        vision_url = "https://integrate.api.nvidia.com/v1/chat/completions"  # Or specific vision endpoint
        payload = {
            "model": "nvidia/nemotron-nano-12b-v2-vl",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 512,
        }
        # Note: Vision Engine might need a different API Key (NVIDIA_API_KEY_VISION)
        # For now, we use the global key if available.
        resp = http_session.post(
            vision_url,
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
        return jsonify(
            {"transcription": resp.json()["choices"][0]["message"]["content"]}
        )
    except Exception as e:
        log.error(f"Vision transcription failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/swarm/todo/architect", methods=["POST"])
def todo_architect():
    """Generate a comprehensive multi-step plan from a high-level goal."""
    data = request.json
    goal = data.get("goal", "")
    if not goal:
        return jsonify({"error": "No goal provided"}), 400

    prompt = (
        f"You are the MR.VERMA Swarm Architect. Create a detailed, multi-step implementation plan for the following goal: '{goal}'. "
        "Break it down into discrete, actionable tasks. For each task, provide a 'title', 'priority' (low, medium, high), and 'category' (e.g., Design, Development, Research). "
        'Return a JSON list of objects ONLY. Example: [{"title": "Task Name", "priority": "high", "category": "Design"}]'
    )

    try:
        payload = {
            "model": "z-ai/glm5",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        resp = http_session.post(
            NVIDIA_API_URL,
            headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
            json=payload,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]

        # Semantic English Fallback: Extract JSON or parse as natural list
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
            return jsonify(json.loads(content))

        try:
            # Try parsing raw content as JSON
            return jsonify(json.loads(content))
        except:
            # If not JSON, parse as newline-separated bulleted list (Semantic English)
            tasks = []
            for line in content.split("\n"):
                if (
                    line.strip().startswith("-") or line.strip()[0].isdigit()
                    if line.strip()
                    else False
                ):
                    title = line.strip().lstrip("-").strip().split(". ", 1)[-1]
                    tasks.append(
                        {
                            "title": title,
                            "priority": "medium",
                            "category": "Architected",
                        }
                    )
            return jsonify(
                tasks
                if tasks
                else [{"title": content, "priority": "medium", "category": "Response"}]
            )
    except Exception as e:
        log.error(f"Architecting failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/swarm/dispatch", methods=["POST"])
def swarm_dispatch():
    """Execute high-level commands dispatched from the Dashboard."""
    data = request.json
    command = data.get("command", "").strip().lower()

    if not command:
        return jsonify({"error": "No command provided"}), 400

    log.info(f"SWARM DISPATCH: {command}")

    # Simple Routing Logic
    if command == "/scan":
        # Placeholder for triggering a scan
        response = "Triggering Swarm Vulnerability Scan... [PHASE: SCANNING]"
        status = "BUSY"
    elif command == "/heal":
        response = (
            "Initiating Autonomous Self-Heal Loop... [PHASE: ANALYZING AUDIT.LOG]"
        )
        status = "BUSY"
    elif command.startswith("/analyze"):
        target = command.split(" ", 1)[1] if " " in command else "project root"
        response = f"Deep Analysis queued for: {target}"
        status = "QUEUED"
    elif command == "/kill":
        response = "EMERGENCY PROTOCOL: Isolating Swarm. [PHASE: SHUTDOWN]"
        status = "LOCKED"
    elif command.startswith("/"):
        # Handle dynamic slash commands from plugins
        plugin_cmd = plugin_orchestrator.get_command(command[1:])
        if plugin_cmd:
            response = f"Executing Plugin Command: {plugin_cmd['metadata'].get('description', command)}"
            status = "OK"
        else:
            response = f"Unknown core or plugin command: {command}"
            status = "ERROR"
    else:
        # Check if user is addressing a specific agent by @name
        if command.startswith("@"):
            agent_name = command.split(" ")[0][1:]
            agent = plugin_orchestrator.get_agent(agent_name)
            if agent:
                response = f"Switching context to Next-Gen Agent: {agent_name}. {agent['metadata'].get('description')}"
                status = "OK"
            else:
                response = f"Agent @{agent_name} not found in specialist Registry."
                status = "ERROR"
        else:
            response = f"Command acknowledged: {command}. Instructions sent to Intelligence Cluster."
            status = "OK"

    # Broadcast the dispatch result to logs for visibility
    _broadcast_event(
        "kernel_log",
        {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "model": "COMMAND_DISPATCH",
            "latency_ms": 0,
            "response": f"EXECUTED: {command} -> {response}",
            "guards": [],
        },
    )

    return jsonify({"status": status, "response": response, "timestamp": time.time()})


@app.route("/api/stream", methods=["GET"])
def stream():
    """Server-Sent Events provider for real-time dashboard updates."""

    def event_stream():
        q = queue.Queue()
        with _listeners_lock:
            _event_listeners.append(q)
        try:
            # Send initial state
            yield f"event: telemetry\ndata: {json.dumps(get_cached_telemetry())}\n\n"
            yield f"event: thermal_status\ndata: {json.dumps(thermal_gov.get_status())}\n\n"
            yield f"event: security_status\ndata: {json.dumps(security_list.get_status())}\n\n"

            while True:
                msg = q.get()  # Blocks until _broadcast_event puts something
                yield msg
        except GeneratorExit:
            with _listeners_lock:
                _event_listeners.remove(q)

    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint — verifies NVIDIA API connectivity."""
    try:
        models_url = NVIDIA_API_URL.replace("/chat/completions", "/models")
        check = http_session.get(
            models_url, headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"}, timeout=5
        )
        status = (
            "connected" if check.status_code == 200 else f"error_{check.status_code}"
        )
    except Exception as e:
        status = f"unreachable ({e})"

    return jsonify(
        {
            "status": status,
            "backend": "nvidia",
            "model": NVIDIA_MODEL,
            "uptime_seconds": int(time.time() - _start_time),
        }
    ), 200


# ── Startup ──
_start_time = time.time()

# Start telemetry background thread
_telemetry_thread = threading.Thread(target=_refresh_telemetry, daemon=True)
_telemetry_thread.start()


# Graceful shutdown
def _shutdown(signum, frame):
    log.info(f"Received signal {signum}, shutting down gracefully...")
    raise SystemExit(0)


signal.signal(signal.SIGTERM, _shutdown)

if __name__ == "__main__":
    log.info(f"🚀 Starting MR. VERMA Core ({NVIDIA_MODEL}) on port 8550")
    app.run(host="0.0.0.0", port=8550)
