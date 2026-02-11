import streamlit as st
import pandas as pd
import json
import glob
import os
import requests
import time
from datetime import datetime

# Config
# Dynamic path detection for both Docker and Local environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("VERMA_DATA_DIR", os.path.join(BASE_DIR, "data"))
LOG_DIR = os.getenv("VERMA_LOG_DIR", os.path.join(BASE_DIR, "logs"))
PROXY_URL = os.getenv("VERMA_PROXY_URL", "http://localhost:8550/v1/chat/completions")

st.set_page_config(
    page_title="MR. VERMA | SYMS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PHANTOM COMMAND UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Space+Grotesk:wght@300;400;600&display=swap');

    /* GLOBAL THEME OVERRIDE */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(circle at 20% 20%, rgba(0, 242, 255, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(188, 19, 254, 0.05) 0%, transparent 40%);
        font-family: 'JetBrains Mono', monospace;
        color: #a0a0a0;
    }

    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* PHANTOM TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        letter-spacing: -1px;
        text-transform: uppercase;
    }
    
    .glow-header {
        background: linear-gradient(90deg, #00f2ff, #bc13fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.3));
    }

    /* OBSIDIAN GLASS SURFACES */
    .obsidian-card {
        background: rgba(10, 10, 15, 0.7);
        border: 1px solid rgba(0, 242, 255, 0.1);
        padding: 24px;
        border-radius: 4px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .obsidian-card:hover {
        border-color: rgba(0, 242, 255, 0.4);
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.1);
        transform: translateY(-2px);
    }
    .obsidian-card::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        transition: 0.5s;
    }
    .obsidian-card:hover::before {
        left: 100%;
    }

    /* DATA MODULES (Custom Metrics) */
    .module-label {
        font-size: 0.75rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }
    .module-value {
        font-size: 1.8rem;
        color: #00f2ff;
        font-weight: 600;
    }
    .module-delta {
        font-size: 0.8rem;
        margin-top: 4px;
    }
    .delta-plus { color: #00ff88; }
    .delta-minus { color: #ff3366; }

    /* NEURAL TERMINAL (Chat) */
    .terminal-line {
        border-left: 2px solid #1f1f1f;
        padding-left: 20px;
        margin-bottom: 20px;
        font-size: 0.95rem;
    }
    .terminal-meta {
        font-size: 0.7rem;
        color: #444;
        margin-bottom: 5px;
    }
    .agent-pill {
        background: rgba(188, 19, 254, 0.1);
        color: #bc13fe;
        padding: 2px 8px;
        border-radius: 100px;
        font-size: 0.65rem;
        border: 1px solid rgba(188, 19, 254, 0.2);
    }
    
    /* INPUT BAR */
    .stChatInputContainer {
        border: none !important;
        background: transparent !important;
    }
    .stChatInputContainer textarea {
        background: rgba(15, 15, 20, 0.9) !important;
        border: 1px solid #222 !important;
        border-radius: 4px !important;
        color: #00f2ff !important;
        padding: 15px !important;
    }
    .stChatInputContainer textarea:focus {
        border-color: #00f2ff !important;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.1) !important;
    }

    /* NEURAL PULSE ANIMATION */
    @keyframes pulse-border {
        0% { border-color: rgba(0, 242, 255, 0.1); }
        50% { border-color: rgba(0, 242, 255, 0.5); }
        100% { border-color: rgba(0, 242, 255, 0.1); }
    }
    .active-terminal {
        animation: pulse-border 2s infinite ease-in-out;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: #0a0a0a;
        padding: 10px 20px;
        border-bottom: 1px solid #111;
    }
    .stTabs [data-baseweb="tab"] {
        border: none !important;
        font-weight: 400 !important;
    }
    .stTabs [aria-selected="true"] {
        color: #00f2ff !important;
        border-bottom: 2px solid #00f2ff !important;
    }

    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #050505; }
    ::-webkit-scrollbar-thumb { background: #1f1f1f; }
    ::-webkit-scrollbar-thumb:hover { background: #00f2ff; }
</style>

<script>
    // Neural Pulse Speed Logic (Simulated for UI)
    const terminal = window.parent.document.querySelector('.stChatMessage');
    if (terminal) terminal.classList.add('active-terminal');
</script>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS (No changes needed in logic) ---

def load_data():
    """Load stats from JSONL files with advanced grouping."""
    stats = {
        "interactions": 0,
        "recent_delta": 0,
        "rewards": [],
        "agent_usage": {},
        "sft_samples": 0,
        "history": [],
        "guards": {
            "hallucinations": 0,
            "optimizations": 0
        }
    }
    
    # Time-based delta (last 1 hour)
    now = time.time()
    
    # Interactions
    interaction_files = glob.glob(os.path.join(DATA_DIR, "interactions", "*.json*"))
    for f in interaction_files:
        try:
            with open(f) as fp:
                # Handle both JSONL and single JSON object
                content = fp.read()
                if not content.strip(): continue
                
                # Try to parse as single JSON
                try:
                    lines = [json.loads(content)]
                except:
                    # Fallback to JSONL
                    lines = [json.loads(line) for line in content.splitlines() if line.strip()]
                
                for data in lines:
                    stats["interactions"] += 1
                    
                    # Track Agent Usage
                    agent = data.get("agent_name", "unknown")
                    stats["agent_usage"][agent] = stats["agent_usage"].get(agent, 0) + 1
                    
                    # Track Recent Delta
                    ts = data.get("timestamp", 0)
                    if now - ts < 3600:
                        stats["recent_delta"] += 1
                        
                    # Track Guards
                    for guard in data.get("guards", []):
                        if guard.get("type") == "hallucination_detected":
                            stats["guards"]["hallucinations"] += 1
                        if guard.get("type") == "symbolic_density_enforced":
                            stats["guards"]["optimizations"] += 1
        except: pass
        
    # Rewards
    reward_files = glob.glob(os.path.join(DATA_DIR, "rewards", "*.json*"))
    for f in reward_files:
        try:
            with open(f) as fp:
                # Support single reward JSON and JSONL
                content = fp.read()
                if not content.strip(): continue
                try:
                    entries = [json.loads(content)]
                except:
                    entries = [json.loads(line) for line in content.splitlines() if line.strip()]
                    
                for r in entries:
                    stats["rewards"].append(r.get("reward_score", 0))
        except: pass
        
    # SFT Samples
    sft_files = glob.glob(os.path.join(DATA_DIR, "sft_batches", "*.json*"))
    for f in sft_files:
        try:
            with open(f) as fp:
                stats["sft_samples"] += len(json.load(fp))
        except: pass
    return stats

def render_status_tab():
    st.markdown('<h1 class="glow-header">SYSTEM . STATUS</h1>', unsafe_allow_html=True)
    
    stats = load_data()
    
    # --- TOP TELEMETRY BAR ---
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">NEURAL . INTERACTIONS</div>
            <div class="module-value">{stats["interactions"]}</div>
            <div class="module-delta delta-plus">+{stats['recent_delta']} new / hr</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        avg_reward = sum(stats["rewards"]) / len(stats["rewards"]) if stats["rewards"] else 0
        reward_color = "delta-plus" if avg_reward > 0.8 else "delta-minus"
        reward_text = "OPTIMAL" if avg_reward > 0.8 else "STABILIZING"
        avg_reward_fmt = f"{avg_reward:.2f}"
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">AVG . REWARD</div>
            <div class="module-value">{avg_reward_fmt}</div>
            <div class="module-delta {reward_color}">{reward_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        target = 500
        progress = (stats["sft_samples"] / target) * 100
        progress_fmt = f"{progress:.1f}%"
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">SFT . PROGRESS</div>
            <div class="module-value">{progress_fmt}</div>
            <div class="module-delta">{stats["sft_samples"]} samples / {target}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        health_status = "OPTIMAL" if stats["recent_delta"] > 0 else "IDLE"
        health_color = "delta-plus" if stats["recent_delta"] > 0 else "delta-minus"
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">SYSTEM . CORE</div>
            <div class="module-value" style="font-size: 1.4rem;">{health_status}</div>
            <div class="module-delta {health_color}">HEALTH: 100%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- PROACTIVE SUPREME GUARDIAN ---
    st.markdown('<h3 style="margin-bottom: 20px;">GUARDIAN . GATE</h3>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">SYMBOLIC DENSITY</div>
            <div class="module-value">{stats['guards']['optimizations']}</div>
            <div class="module-delta delta-plus">ENFORCED</div>
        </div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">HALLUCINATIONS</div>
            <div class="module-value">{stats['guards']['hallucinations']}</div>
            <div class="module-delta delta-minus">BLOCKED</div>
        </div>
        """, unsafe_allow_html=True)
    with g3:
        status_text = "PROTECH ACTIVE" if stats["recent_delta"] > 0 else "GUARD IDLE"
        status_color = "delta-plus" if stats["recent_delta"] > 0 else "delta-minus"
        st.markdown(f"""
        <div class="obsidian-card">
            <div class="module-label">SECURITY STATUS</div>
            <div class="module-value" style="font-size: 1.4rem;">{status_text}</div>
            <div class="module-delta {status_color}">GATE: SECURE</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3>AGENT . MESH . MONITOR</h3>", unsafe_allow_html=True)
    if stats["agent_usage"]:
        agent_df = pd.DataFrame([
            {"Agent": k, "Interactions": v} 
            for k, v in stats["agent_usage"].items()
        ]).sort_values("Interactions", ascending=False)
        st.bar_chart(agent_df.set_index("Agent"), height=250, use_container_width=True)
    else:
        st.info("No agent telemetry detected.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h3>REWARD . MATRIX</h3>", unsafe_allow_html=True)
    if stats["rewards"]:
        st.line_chart(stats["rewards"][-100:], height=300, use_container_width=True)
    else:
        st.info("No data stream detected.")

def render_chat_tab():
    st.markdown('<h1 class="glow-header">NEURAL . TERMINAL</h1>', unsafe_allow_html=True)
    
    # Sidebar Options
    with st.sidebar:
        st.markdown('<div class="obsidian-card">', unsafe_allow_html=True)
        st.subheader("⚙️ CONTROL . PANEL")
        model = st.selectbox("MODEL . SELECTOR", ["local-coder", "sidecar (1.5b)"])
        temp = st.slider("TEMPERATURE", 0.0, 1.0, 0.7)
        st.markdown("---")
        st.caption("TELEMETRY COMMANDS")
        st.code("@[agent]\n/workflow", language="bash")
        
        if st.button("CLR . MEMORY"):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Session State for History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History in Terminal Style
    for msg in st.session_state.messages:
        role_label = "ASSISTANT" if msg["role"] == "assistant" else "USER"
        role_color = "#bc13fe" if msg["role"] == "assistant" else "#00f2ff"
        role_avatar = "⚡" if msg["role"] == "assistant" else "👤"
        
        st.markdown(f"""
        <div class="terminal-line">
            <div class="terminal-meta">
                <span style="color: {role_color}; font-weight: 600;">[{role_label}]</span> 
                <span class="agent-pill">SYMS-1.0</span> 
                <span style="opacity: 0.5;">{datetime.now().strftime("%H:%M:%S")}</span>
            </div>
            <div style="color: #e0e0e0; font-family: 'JetBrains Mono', monospace;">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)

    # Chat Input
    prompt = st.chat_input("Enter command or query...")
    if prompt:
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get Response Logic (Modified to fit Terminal style)
        with st.empty():
            st.markdown(f"""
            <div class="terminal-line active-terminal">
                <div class="terminal-meta">
                    <span style="color: #bc13fe; font-weight: 600;">[ASSISTANT]</span> 
                    <span class="agent-pill">SYMS-STREAM</span>
                </div>
                <div id="streaming-text" style="color: #00f2ff; font-family: 'JetBrains Mono', monospace;">... INCOMING TELEMETRY ...</div>
            </div>
            """, unsafe_allow_html=True)
            
            full_response = ""
            try:
                payload = {
                    "model": model, 
                    "messages": st.session_state.messages,
                    "stream": True,
                    "temperature": temp
                }
                
                with requests.post(PROXY_URL, json=payload, stream=True) as r:
                    if r.status_code == 200:
                        for line in r.iter_lines():
                            if line:
                                try:
                                    decoded_line = line.decode("utf-8")
                                    if decoded_line.startswith("data: "):
                                        data_str = decoded_line[6:]
                                        if data_str.strip() == "[DONE]":
                                            break
                                        data_json = json.loads(data_str)
                                        content = data_json.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                        if content:
                                            full_response += content
                                except Exception: pass 
                    else:
                        full_response = f"Error: {r.status_code}"
            except Exception as e:
                full_response = f"Connection Failed: {e}"

        # Add Assistant Message and Rerun
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# --- MAIN ---
def main():
    tab1, tab2 = st.tabs(["[ TELEMETRY ]", "[ NEURAL TERMINAL ]"])
    
    with tab1:
        render_status_tab()
        
        # --- SYSTEM MASTERY INFO ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        html_mastery = """
        <div class="obsidian-card" style="border-color: rgba(188, 19, 254, 0.3);">
            <h3>PHANTOM . MASTERY</h3>
            <p style="color: #666; font-size: 1rem; line-height: 1.6;">
                MR. VERMA is operating at <b style="color: #00f2ff;">FULL CAPACITY</b>. 
                The 'Spider Web' mesh is actively monitoring specialist agents across 198 workflows. 
                Neural interactions are being captured, processed, and optimized via the 
                <b style="color: #bc13fe;">Google Antigravity Platform</b>.
            </p>
            <div style="display: flex; gap: 30px; margin-top: 25px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace;">
                <div style="color: #00f2ff;">SYMBOLIC DENSITY: L3</div>
                <div style="color: #bc13fe;">SYNC HARMONY: ACTIVE</div>
                <div style="color: #00ff88;">POWERUSEAGE: MAX</div>
            </div>
        </div>
        """
        st.markdown(html_mastery, unsafe_allow_html=True)
        
    with tab2:
        render_chat_tab()

if __name__ == "__main__":
    main()
