#!/usr/bin/env python3
"""
🎭 MR.VERMA LIVE DASHBOARD - For Non-Technical Audiences
═══════════════════════════════════════════════════════════

A beautiful, real-time visualization of MR.VERMA's AI system
showcasing how artificial intelligence works in simple terms.

Features:
- Real-time process visualization
- Simple English explanations
- Live system status
- Interactive demonstrations
"""

import os
import sys
import time
import json
import random
import threading
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.tree import Tree
    from rich.align import Align
    from rich.box import Box, DOUBLE, ROUNDED
    from rich.style import Style
    from rich.color import Color

    RICH_AVAILABLE = True
except ImportError:
    print("Installing rich...")
    os.system("pip install rich -q")
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.tree import Tree
    from rich.align import Align
    from rich.box import DOUBLE, ROUNDED

    RICH_AVAILABLE = True

console = Console()

# ═══════════════════════════════════════════════════════════════════════════════
# SYSTEM STATE & SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════


class SystemState:
    """Tracks the current state of MR.VERMA system"""

    def __init__(self):
        self.active = True
        self.current_task = "Initializing..."
        self.thought_process = []
        self.agents_active = []
        self.memory_usage = 0
        self.api_calls = 0
        self.confidence_score = 0.0
        self.processing_stage = "idle"
        self.user_question = ""
        self.ai_response = ""
        self.thinking_steps = []

    def add_thought(self, thought, emoji="💭"):
        """Add a thinking step with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.thought_process.append((timestamp, emoji, thought))
        if len(self.thought_process) > 20:
            self.thought_process.pop(0)

    def update_stage(self, stage, description=""):
        """Update current processing stage"""
        self.processing_stage = stage
        if description:
            self.add_thought(description, self._get_stage_emoji(stage))

    def _get_stage_emoji(self, stage):
        """Get emoji for processing stage"""
        emojis = {
            "idle": "😴",
            "listening": "👂",
            "understanding": "🤔",
            "researching": "🔍",
            "thinking": "🧠",
            "creating": "✨",
            "checking": "🔍",
            "responding": "💬",
            "learning": "📚",
        }
        return emojis.get(stage, "⚡")


system_state = SystemState()

# ═══════════════════════════════════════════════════════════════════════════════
# VISUAL COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


def create_banner():
    """Create beautiful ASCII banner"""
    banner_text = """
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   🤖  MR.VERMA - LIVE AI DEMONSTRATION  🤖                           ║
    ║                                                                       ║
    ║   "See How Artificial Intelligence Thinks & Works"                   ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """
    return Panel(
        Align.center(Text(banner_text, style="bold cyan")),
        box=DOUBLE,
        border_style="bright_blue",
    )


def create_simple_explanation():
    """Explain what MR.VERMA is doing in simple terms"""
    explanation = """
    [bold yellow]What you're seeing:[/bold yellow]
    
    This dashboard shows how MR.VERMA (an AI assistant) processes 
    your questions and creates responses - just like how your brain 
    thinks before speaking!
    
    [bold green]The Process:[/bold green]
    1. 🎯 [bold]Listens[/bold] - Hears your question
    2. 🧠 [bold]Understands[/bold] - Figures out what you need
    3. 🔍 [bold]Researches[/bold] - Looks up relevant information
    4. ✨ [bold]Creates[/bold] - Builds a helpful response
    5. 💬 [bold]Responds[/bold] - Shares the answer with you
    """
    return Panel(
        explanation, title="📖 Simple Explanation", border_style="green", box=ROUNDED
    )


def create_live_status():
    """Show live system status"""
    table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Activity", style="yellow")

    # Simulate various components
    components = [
        ("🎯 Main Brain", "✅ Active", system_state.processing_stage),
        (
            "🧠 Memory System",
            "✅ Ready",
            f"{len(system_state.thought_process)} thoughts",
        ),
        (
            "🤖 AI Agents",
            f"✅ {len(system_state.agents_active)} Active",
            ",".join(system_state.agents_active)
            if system_state.agents_active
            else "Standby",
        ),
        ("💾 Vector Memory", "✅ Connected", "Milvus Ready"),
        ("🌐 API Connection", "✅ Online", f"{system_state.api_calls} calls"),
        (
            "📊 Confidence",
            f"{'█' * int(system_state.confidence_score * 10)}{'░' * (10 - int(system_state.confidence_score * 10))}",
            f"{system_state.confidence_score * 100:.0f}% sure",
        ),
    ]

    for comp, status, activity in components:
        table.add_row(comp, status, activity)

    return Panel(
        table, title="🔴 Live System Status", border_style="bright_red", box=DOUBLE
    )


def create_thinking_process():
    """Show AI thinking process in real-time"""
    if not system_state.thought_process:
        content = "[dim]Waiting for input... The AI is ready to help you![/dim]"
    else:
        content = ""
        for timestamp, emoji, thought in reversed(system_state.thought_process[-10:]):
            content += f"[dim]{timestamp}[/dim] {emoji} {thought}\n"

    return Panel(
        content,
        title="🧠 AI Thinking Process (Real-Time)",
        border_style="bright_cyan",
        box=ROUNDED,
    )


def create_user_friendly_explanation():
    """Explain current action in very simple terms"""
    stage_descriptions = {
        "idle": "The AI is resting and waiting for your question, just like how you wait for someone to ask you something.",
        "listening": "The AI is paying attention to what you're saying, like when you listen to a friend.",
        "understanding": "The AI is figuring out what you really need. It's like when you read a question and think about what answer would help most.",
        "researching": "The AI is looking through its knowledge to find the best information for you, like searching in a library.",
        "thinking": "The AI is connecting different ideas together to form a good answer, like solving a puzzle.",
        "creating": "The AI is building your answer step by step, like writing a story or drawing a picture.",
        "checking": "The AI is reviewing its answer to make sure it's correct and helpful, like proofreading your homework.",
        "responding": "The AI is sharing the final answer with you! 🎉",
    }

    current_desc = stage_descriptions.get(
        system_state.processing_stage, "The AI is working on something important..."
    )

    return Panel(
        f"[bold yellow]Current Activity:[/bold yellow]\n\n"
        f"[bold]{current_desc}[/bold]\n\n"
        f"[dim]Think of it like:[/dim] When you ask a smart friend a question, "
        f"they listen, think about what they know, and then give you a helpful answer. "
        f"MR.VERMA does the same thing, just much faster! ⚡",
        title="💡 What's Happening Right Now?",
        border_style="bright_yellow",
        box=DOUBLE,
    )


def create_visual_flow():
    """Create visual flow diagram"""
    flow = """
    [bold]Your Question → AI Brain → Understanding → Memory → Creating → Answer[/bold]
    
    [green]Step 1:[/green] You ask something
         ↓
    [blue]Step 2:[/blue] AI figures out what you need
         ↓
    [yellow]Step 3:[/yellow] AI remembers similar things
         ↓
    [magenta]Step 4:[/magenta] AI creates a response
         ↓
    [cyan]Step 5:[/cyan] You get your answer!
    """
    return Panel(flow, title="🔄 How It Works", border_style="white", box=ROUNDED)


# ═══════════════════════════════════════════════════════════════════════════════
# DEMONSTRATION SCENARIOS
# ═══════════════════════════════════════════════════════════════════════════════


def demo_scenario_1_ask_question():
    """Demo: User asks a simple question"""
    console.print(
        "\n[bold green]═══════════════════════════════════════════════════[/bold green]"
    )
    console.print(
        "[bold green]  DEMONSTRATION 1: Asking a Simple Question[/bold green]"
    )
    console.print(
        "[bold green]═══════════════════════════════════════════════════[/bold green]\n"
    )

    system_state.user_question = "What's the weather like today?"
    system_state.update_stage("listening", "Someone asked about the weather")
    time.sleep(1)

    system_state.update_stage(
        "understanding", "I need to figure out what city they're asking about"
    )
    system_state.confidence_score = 0.3
    time.sleep(1.5)

    system_state.update_stage(
        "researching", "Looking up weather information for the location"
    )
    system_state.agents_active = ["Weather Agent"]
    system_state.api_calls += 1
    system_state.confidence_score = 0.6
    time.sleep(2)

    system_state.update_stage(
        "thinking", "Organizing the weather data into a clear answer"
    )
    system_state.confidence_score = 0.85
    time.sleep(1.5)

    system_state.update_stage("responding", "Ready to share the weather forecast!")
    system_state.ai_response = "It's sunny and 75°F today - perfect weather! ☀️"
    system_state.confidence_score = 0.95
    system_state.agents_active = []
    time.sleep(1)

    system_state.update_stage("idle", "Waiting for the next question")


def demo_scenario_2_code_help():
    """Demo: User needs code help"""
    console.print(
        "\n[bold blue]═══════════════════════════════════════════════════[/bold blue]"
    )
    console.print("[bold blue]  DEMONSTRATION 2: Writing Computer Code[/bold blue]")
    console.print(
        "[bold blue]═══════════════════════════════════════════════════[/bold blue]\n"
    )

    system_state.user_question = "Write a function to calculate factorial"
    system_state.update_stage("listening", "Someone needs help with programming")
    time.sleep(1)

    system_state.update_stage(
        "understanding", "They want a factorial function - that's math code!"
    )
    system_state.confidence_score = 0.4
    time.sleep(1.5)

    system_state.update_stage(
        "researching", "Checking best practices for factorial functions"
    )
    system_state.agents_active = ["Code Agent", "Math Agent"]
    system_state.api_calls += 1
    system_state.confidence_score = 0.7
    time.sleep(2)

    system_state.update_stage("creating", "Writing the Python code step by step")
    system_state.add_thought("Creating a function named 'factorial'")
    system_state.add_thought("Adding error handling for negative numbers")
    system_state.add_thought("Using recursion for elegant solution")
    system_state.confidence_score = 0.9
    time.sleep(2.5)

    system_state.update_stage("checking", "Reviewing code for bugs and clarity")
    system_state.confidence_score = 0.95
    time.sleep(1.5)

    system_state.update_stage("responding", "Code is ready to share!")
    system_state.ai_response = "Here's a factorial function with error handling..."
    system_state.agents_active = []
    time.sleep(1)

    system_state.update_stage("idle", "Ready for next request")


def demo_scenario_3_learning():
    """Demo: AI learning from interaction"""
    console.print(
        "\n[bold magenta]═══════════════════════════════════════════════════[/bold magenta]"
    )
    console.print(
        "[bold magenta]  DEMONSTRATION 3: AI Learning & Improving[/bold magenta]"
    )
    console.print(
        "[bold magenta]═══════════════════════════════════════════════════[/bold magenta]\n"
    )

    system_state.update_stage(
        "learning", "Learning from our conversation to get better!"
    )
    system_state.add_thought("Saving this interaction to memory")
    system_state.add_thought("Noting what worked well in my response")
    system_state.add_thought("Updating my knowledge for next time")
    system_state.memory_usage += 1
    time.sleep(3)

    system_state.update_stage("idle", "Knowledge updated! I'm getting smarter 🧠✨")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════


def generate_layout():
    """Generate the full dashboard layout"""
    layout = Layout()

    # Split into sections
    layout.split_column(
        Layout(name="header", size=10),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=5),
    )

    # Header with banner
    layout["header"].update(create_banner())

    # Main content area
    layout["main"].split_row(
        Layout(name="left", ratio=1), Layout(name="right", ratio=1)
    )

    # Left column
    layout["left"].split_column(
        Layout(name="explanation", ratio=1), Layout(name="flow", size=12)
    )
    layout["left"]["explanation"].update(create_simple_explanation())
    layout["left"]["flow"].update(create_visual_flow())

    # Right column
    layout["right"].split_column(
        Layout(name="status", ratio=1),
        Layout(name="thinking", ratio=1),
        Layout(name="friendly", size=10),
    )
    layout["right"]["status"].update(create_live_status())
    layout["right"]["thinking"].update(create_thinking_process())
    layout["right"]["friendly"].update(create_user_friendly_explanation())

    # Footer with instructions
    footer_text = """
    [bold green]Controls:[/bold green] Press [bold]Ctrl+C[/bold] to exit | 
    [bold yellow]Tip:[/bold yellow] Watch how the AI thinks through each step just like a human would!
    """
    layout["footer"].update(Panel(footer_text, border_style="bright_green"))

    return layout


def run_dashboard():
    """Main dashboard loop"""
    console.clear()

    console.print(create_banner())
    console.print("\n[bold cyan]Starting MR.VERMA Live Demonstration...[/bold cyan]\n")

    try:
        with Live(generate_layout(), refresh_per_second=2, screen=True) as live:
            # Run demos
            time.sleep(2)

            # Demo 1
            demo_scenario_1_ask_question()
            time.sleep(2)

            # Demo 2
            demo_scenario_2_code_help()
            time.sleep(2)

            # Demo 3
            demo_scenario_3_learning()
            time.sleep(2)

            # Continue showing idle state
            for _ in range(30):
                live.update(generate_layout())
                time.sleep(0.5)

    except KeyboardInterrupt:
        console.clear()
        console.print(
            "\n[bold green]Thank you for watching the MR.VERMA demonstration![/bold green]"
        )
        console.print("[dim]The AI system is still running in the background.[/dim]\n")


def main():
    """Entry point"""
    console.print(
        "[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/bold cyan]"
    )
    console.print(
        "[bold cyan]║                                                               ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]║   🤖  MR.VERMA - LIVE AI DEMONSTRATION FOR EVERYONE  🤖      ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]║                                                               ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]║   Watch how Artificial Intelligence thinks and works!         ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]║                                                               ║[/bold cyan]"
    )
    console.print(
        "[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/bold cyan]"
    )
    console.print()

    console.print("[bold yellow]What this demo shows:[/bold yellow]")
    console.print("  • How AI understands your questions")
    console.print("  • How AI searches its memory for answers")
    console.print("  • How AI creates responses step-by-step")
    console.print("  • How AI learns and improves")
    console.print()

    console.print("[bold green]Perfect for:[/bold green]")
    console.print("  • Non-technical audiences")
    console.print("  • Students learning about AI")
    console.print("  • Business stakeholders")
    console.print("  • Anyone curious about how AI works!")
    console.print()

    input("[bold cyan]Press Enter to start the live demonstration...[/bold cyan]")

    run_dashboard()


if __name__ == "__main__":
    main()
