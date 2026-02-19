#!/usr/bin/env python3
"""
🌐 MR.VERMA WEB DASHBOARD - Real-Time AI Visualization
════════════════════════════════════════════════════════

A beautiful web interface showing MR.VERMA's operations in real-time
Accessible at: http://localhost:8765

Features:
- Real-time WebSocket updates
- Visual process flows
- Simple English explanations
- Interactive demonstrations
- Mobile-friendly design
"""

import asyncio
import json
import random
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# Try to import Flask, install if needed
try:
    from flask import Flask, render_template_string, jsonify
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit

    FLASK_AVAILABLE = True
except ImportError:
    print("Installing Flask dependencies...")
    import os

    os.system("pip install flask flask-cors flask-socketio -q")
    from flask import Flask, render_template_string, jsonify
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit

    FLASK_AVAILABLE = True

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
system_state = {
    "status": "running",
    "current_task": "Waiting for input...",
    "stage": "idle",
    "confidence": 0.0,
    "thoughts": [],
    "agents": [],
    "metrics": {"api_calls": 0, "memory_usage": 0, "response_time": 0},
}

# HTML Template with modern design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 MR.VERMA - Live AI Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            color: white;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.3em;
            opacity: 0.9;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            margin-bottom: 15px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-active { background: #00ff88; }
        .status-idle { background: #ffaa00; }
        .status-thinking { background: #00ccff; }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .thought-box {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #00ccff;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }
        
        .thought-box .time {
            color: #ffaa00;
            font-size: 0.85em;
        }
        
        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00ccff);
            border-radius: 15px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .simple-explanation {
            background: linear-gradient(135deg, rgba(255,170,0,0.2), rgba(255,170,0,0.1));
            border: 2px solid #ffaa00;
            font-size: 1.1em;
            line-height: 1.6;
        }
        
        .flow-step {
            display: flex;
            align-items: center;
            margin: 15px 0;
            padding: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .flow-step.active {
            background: rgba(0,204,255,0.2);
            border: 2px solid #00ccff;
            transform: scale(1.02);
        }
        
        .step-number {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #00ccff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 15px;
            font-size: 1.2em;
        }
        
        .step-content h3 {
            margin-bottom: 5px;
        }
        
        .step-content p {
            opacity: 0.8;
            font-size: 0.9em;
        }
        
        .agent-tag {
            display: inline-block;
            padding: 5px 12px;
            background: rgba(0,255,136,0.2);
            border: 1px solid #00ff88;
            border-radius: 20px;
            margin: 5px;
            font-size: 0.85em;
        }
        
        .demo-controls {
            position: fixed;
            bottom: 30px;
            right: 30px;
            display: flex;
            gap: 10px;
        }
        
        button {
            padding: 15px 30px;
            background: #00ff88;
            color: #1e3c72;
            border: none;
            border-radius: 30px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,255,136,0.3);
        }
        
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0,255,136,0.4);
        }
        
        button.secondary {
            background: rgba(255,255,255,0.2);
            color: white;
        }
        
        .typing-indicator {
            display: flex;
            gap: 5px;
            padding: 10px;
        }
        
        .typing-indicator span {
            width: 10px;
            height: 10px;
            background: #00ccff;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typing {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 MR.VERMA AI Dashboard</h1>
            <p class="subtitle">Watch How Artificial Intelligence Works in Real-Time</p>
        </header>
        
        <div class="grid">
            <!-- Current Status -->
            <div class="card">
                <h2>
                    <span class="status-indicator status-active" id="statusLight"></span>
                    🔴 Live System Status
                </h2>
                <div id="statusContent">
                    <div class="metric">
                        <span>Current Task:</span>
                        <strong id="currentTask">Initializing...</strong>
                    </div>
                    <div class="metric">
                        <span>Processing Stage:</span>
                        <strong id="processingStage">Starting up</strong>
                    </div>
                    <div class="metric">
                        <span>Confidence Level:</span>
                        <div class="progress-bar">
                            <div class="progress-fill" id="confidenceBar" style="width: 0%">0%</div>
                        </div>
                    </div>
                    <div class="metric">
                        <span>Active Agents:</span>
                        <span id="activeAgents">None</span>
                    </div>
                </div>
            </div>
            
            <!-- Simple Explanation -->
            <div class="card simple-explanation">
                <h2>💡 What's Happening Now?</h2>
                <p id="simpleExplanation">
                    The AI is starting up and getting ready to help you. Think of it like 
                    a smart assistant waking up and preparing to answer your questions!
                </p>
            </div>
            
            <!-- AI Thinking Process -->
            <div class="card">
                <h2>🧠 AI Thinking Process</h2>
                <div id="thinkingProcess">
                    <div class="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
            
            <!-- Process Flow -->
            <div class="card">
                <h2>🔄 How AI Works</h2>
                <div id="processFlow">
                    <div class="flow-step" id="step1">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h3>🎯 Listen</h3>
                            <p>AI hears your question</p>
                        </div>
                    </div>
                    <div class="flow-step" id="step2">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h3>🧠 Understand</h3>
                            <p>Figures out what you need</p>
                        </div>
                    </div>
                    <div class="flow-step" id="step3">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h3>🔍 Research</h3>
                            <p>Searches its knowledge</p>
                        </div>
                    </div>
                    <div class="flow-step" id="step4">
                        <div class="step-number">4</div>
                        <div class="step-content">
                            <h3>✨ Create</h3>
                            <p>Builds your answer</p>
                        </div>
                    </div>
                    <div class="flow-step" id="step5">
                        <div class="step-number">5</div>
                        <div class="step-content">
                            <h3>💬 Respond</h3>
                            <p>Shares the answer</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- System Metrics -->
            <div class="card">
                <h2>📊 System Metrics</h2>
                <div class="metric">
                    <span>API Calls Made:</span>
                    <strong id="apiCalls">0</strong>
                </div>
                <div class="metric">
                    <span>Memory Usage:</span>
                    <strong id="memoryUsage">0 MB</strong>
                </div>
                <div class="metric">
                    <span>Response Time:</span>
                    <strong id="responseTime">0 ms</strong>
                </div>
                <div class="metric">
                    <span>Thoughts Processed:</span>
                    <strong id="thoughtsCount">0</strong>
                </div>
            </div>
            
            <!-- Active Agents -->
            <div class="card">
                <h2>🤖 Active AI Agents</h2>
                <div id="agentsList">
                    <p style="opacity: 0.7;">Waiting for task assignment...</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="demo-controls">
        <button onclick="startDemo()">▶️ Run Demo</button>
        <button class="secondary" onclick="resetDemo()">🔄 Reset</button>
    </div>
    
    <script>
        const socket = io();
        let demoRunning = false;
        
        // Stage descriptions in simple English
        const stageDescriptions = {
            "idle": "The AI is resting and ready for your next question, like a helpful friend waiting to chat!",
            "listening": "The AI is paying close attention to what you're saying, just like when you listen to a friend.",
            "understanding": "The AI is figuring out exactly what you need. It's like when you think about a question before answering.",
            "researching": "The AI is looking through its knowledge to find the best information, like searching in a library.",
            "thinking": "The AI is connecting different ideas together to create a great answer, like solving a puzzle.",
            "creating": "The AI is building your answer piece by piece, like writing a story or drawing a picture.",
            "checking": "The AI is double-checking its answer to make sure it's perfect, like proofreading homework.",
            "responding": "The AI is ready to share its answer with you! 🎉",
            "learning": "The AI is learning from this conversation to be even smarter next time! 🧠✨"
        };
        
        const stageEmojis = {
            "idle": "😴",
            "listening": "👂",
            "understanding": "🤔",
            "researching": "🔍",
            "thinking": "🧠",
            "creating": "✨",
            "checking": "🔍",
            "responding": "💬",
            "learning": "📚"
        };
        
        // Update UI when receiving data
        socket.on('status_update', (data) => {
            updateUI(data);
        });
        
        socket.on('thought', (data) => {
            addThought(data);
        });
        
        function updateUI(data) {
            document.getElementById('currentTask').textContent = data.current_task || 'Waiting...';
            document.getElementById('processingStage').textContent = 
                stageEmojis[data.stage] + ' ' + (data.stage || 'idle');
            
            // Update confidence bar
            const confidence = Math.round((data.confidence || 0) * 100);
            document.getElementById('confidenceBar').style.width = confidence + '%';
            document.getElementById('confidenceBar').textContent = confidence + '%';
            
            // Update agents
            const agentsDiv = document.getElementById('activeAgents');
            if (data.agents && data.agents.length > 0) {
                agentsDiv.innerHTML = data.agents.map(a => `<span class="agent-tag">${a}</span>`).join('');
            } else {
                agentsDiv.textContent = 'None active';
            }
            
            // Update simple explanation
            document.getElementById('simpleExplanation').textContent = 
                stageDescriptions[data.stage] || stageDescriptions['idle'];
            
            // Update metrics
            if (data.metrics) {
                document.getElementById('apiCalls').textContent = data.metrics.api_calls || 0;
                document.getElementById('memoryUsage').textContent = (data.metrics.memory_usage || 0) + ' MB';
                document.getElementById('responseTime').textContent = (data.metrics.response_time || 0) + ' ms';
            }
            
            // Highlight current step in flow
            highlightFlowStep(data.stage);
            
            // Update status light
            const statusLight = document.getElementById('statusLight');
            statusLight.className = 'status-indicator status-' + (data.stage === 'idle' ? 'idle' : 'active');
        }
        
        function highlightFlowStep(stage) {
            // Remove active class from all steps
            for (let i = 1; i <= 5; i++) {
                document.getElementById('step' + i).classList.remove('active');
            }
            
            // Map stages to steps
            const stageToStep = {
                'listening': 1,
                'understanding': 2,
                'researching': 3,
                'thinking': 3,
                'creating': 4,
                'checking': 4,
                'responding': 5
            };
            
            const stepNum = stageToStep[stage];
            if (stepNum) {
                document.getElementById('step' + stepNum).classList.add('active');
            }
        }
        
        function addThought(data) {
            const container = document.getElementById('thinkingProcess');
            const thoughtDiv = document.createElement('div');
            thoughtDiv.className = 'thought-box';
            thoughtDiv.innerHTML = `
                <span class="time">${data.time}</span> ${data.emoji} ${data.text}
            `;
            container.insertBefore(thoughtDiv, container.firstChild);
            
            // Keep only last 5 thoughts
            while (container.children.length > 5) {
                container.removeChild(container.lastChild);
            }
            
            document.getElementById('thoughtsCount').textContent = 
                parseInt(document.getElementById('thoughtsCount').textContent) + 1;
        }
        
        function startDemo() {
            if (demoRunning) return;
            demoRunning = true;
            socket.emit('start_demo');
        }
        
        function resetDemo() {
            demoRunning = false;
            socket.emit('reset_demo');
            document.getElementById('thinkingProcess').innerHTML = `
                <div class="typing-indicator"><span></span><span></span><span></span></div>
            `;
            document.getElementById('thoughtsCount').textContent = '0';
            for (let i = 1; i <= 5; i++) {
                document.getElementById('step' + i).classList.remove('active');
            }
        }
        
        // Start with a welcome message
        setTimeout(() => {
            addThought({
                time: new Date().toLocaleTimeString(),
                emoji: '🎉',
                text: 'MR.VERMA is ready! Click "Run Demo" to see how AI works.'
            });
        }, 1000);
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/status")
def api_status():
    """API endpoint for current status"""
    return jsonify(system_state)


@socketio.on("start_demo")
def handle_start_demo():
    """Run demonstration scenarios"""
    demo_thread = threading.Thread(target=run_demo_scenarios)
    demo_thread.daemon = True
    demo_thread.start()


def run_demo_scenarios():
    """Run AI demonstration scenarios"""
    scenarios = [
        {
            "task": "User asks: 'What's the weather?'",
            "stages": [
                ("listening", "Someone asked about the weather today", 0.3),
                ("understanding", "They want to know current weather conditions", 0.4),
                ("researching", "Looking up weather data for their location", 0.6),
                ("thinking", "Organizing temperature, conditions, and forecast", 0.8),
                ("responding", "It's sunny and 75°F - perfect day! ☀️", 0.95),
            ],
            "agents": ["Weather Agent"],
            "thoughts": [
                ("💭", "Detected weather-related query"),
                ("🌍", "Identified user's location"),
                ("🌤️", "Fetched current conditions"),
                ("📊", "Analyzed forecast data"),
                ("✅", "Generated friendly response"),
            ],
        },
        {
            "task": "User asks: 'Write Python code for factorial'",
            "stages": [
                ("listening", "User needs programming help", 0.4),
                ("understanding", "They want a factorial function in Python", 0.5),
                ("researching", "Checking best practices for recursive functions", 0.7),
                ("creating", "Writing code with error handling", 0.85),
                ("checking", "Testing code for edge cases", 0.9),
                ("responding", "Here's your factorial function! 🐍", 0.95),
            ],
            "agents": ["Code Agent", "Math Agent"],
            "thoughts": [
                ("💻", "Detected programming request"),
                ("🐍", "Language: Python confirmed"),
                ("🧮", "Algorithm: Factorial"),
                ("⚠️", "Added error handling for negatives"),
                ("📝", "Included docstring and comments"),
                ("✨", "Code is clean and efficient!"),
            ],
        },
        {
            "task": "AI Learning from interaction",
            "stages": [
                ("learning", "Saving conversation to memory", 0.8),
                ("learning", "Analyzing what worked well", 0.85),
                ("learning", "Updating knowledge base", 0.9),
                ("idle", "Knowledge updated! Getting smarter 🧠", 0.95),
            ],
            "agents": ["Learning Agent"],
            "thoughts": [
                ("💾", "Storing interaction data"),
                ("📊", "Calculating success metrics"),
                ("🧠", "Updating neural patterns"),
                ("✅", "Learning complete!"),
            ],
        },
    ]

    for scenario in scenarios:
        system_state["current_task"] = scenario["task"]
        system_state["agents"] = []

        for stage, description, confidence in scenario["stages"]:
            system_state["stage"] = stage
            system_state["confidence"] = confidence
            system_state["current_task"] = description

            if stage in ["researching", "creating", "checking"]:
                system_state["agents"] = scenario["agents"]
                system_state["metrics"]["api_calls"] += 1

            socketio.emit("status_update", system_state)

            # Emit thoughts for this stage
            for emoji, thought in scenario["thoughts"]:
                socketio.emit(
                    "thought",
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "emoji": emoji,
                        "text": thought,
                    },
                )
                time.sleep(0.3)

            time.sleep(1.5)

        time.sleep(2)  # Pause between scenarios

    # Reset to idle
    system_state["stage"] = "idle"
    system_state["current_task"] = "Ready for next question!"
    system_state["agents"] = []
    system_state["confidence"] = 0
    socketio.emit("status_update", system_state)


def main():
    """Start the web dashboard"""
    print("🌐 Starting MR.VERMA Web Dashboard...")
    print("📍 Open your browser and go to: http://localhost:8765")
    print("🛑 Press Ctrl+C to stop\n")

    try:
        socketio.run(app, host="0.0.0.0", port=8765, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")


if __name__ == "__main__":
    main()
