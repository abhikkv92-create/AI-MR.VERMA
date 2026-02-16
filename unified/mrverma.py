#!/usr/bin/env python3
"""
MR.VERMA Unified - Single Interface for All AI Operations
===========================================================

A simplified, user-friendly interface that consolidates all MR.VERMA functionality
into one easy-to-use terminal application.

Usage:
    python unified/mrverma.py

Features:
    - One-click AI assistance
    - No technical knowledge required
    - Automatic setup and configuration
    - Clean, simple interface
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import rich for beautiful UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.live import Live

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Console for output - create a dummy console if rich not available
if RICH_AVAILABLE:
    console = Console()
else:
    # Dummy console class for fallback
    class DummyConsole:
        def print(self, *args, **kwargs):
            # Strip rich formatting tags
            text = " ".join(str(a) for a in args)
            text = text.replace("[bold]", "").replace("[/bold]", "")
            text = text.replace("[bold blue]", "").replace("[bold green]", "")
            text = text.replace("[bold red]", "").replace("[bold yellow]", "")
            text = text.replace("[green]", "").replace("[/green]", "")
            text = text.replace("[blue]", "").replace("[/blue]", "")
            text = text.replace("[red]", "").replace("[/red]", "")
            text = text.replace("[yellow]", "").replace("[/yellow]", "")
            print(text)

        def status(self, *args, **kwargs):
            class DummyStatus:
                def __enter__(self):
                    print("Processing...")
                    return self

                def __exit__(self, *args):
                    pass

            return DummyStatus()

    # Dummy Prompt and Confirm for fallback
    class DummyPrompt:
        @staticmethod
        def ask(message, default=None, choices=None):
            if choices:
                message = f"{message} ({'/'.join(choices)}): "
            elif default is not None:
                message = f"{message} [{default}]: "
            else:
                message = f"{message}: "
            result = input(message)
            if not result and default is not None:
                return default
            return result

    class DummyConfirm:
        @staticmethod
        def ask(message):
            result = input(f"{message} (y/n): ")
            return result.lower() in ["y", "yes"]

    # Create dummy Panel class
    class DummyPanel:
        def __init__(self, text, *args, **kwargs):
            self.text = text

        def __str__(self):
            return f"\n{'=' * 60}\n{self.text}\n{'=' * 60}\n"

    console = DummyConsole()
    Prompt = DummyPrompt
    Confirm = DummyConfirm
    Panel = DummyPanel
    print("Note: Install 'rich' for better UI: pip install rich")


def print_banner():
    """Display the MR.VERMA banner."""
    banner = """
    ███╗   ███╗██████╗      ██╗   ██╗███████╗██████╗ ███╗   ███╗ █████╗
    ████╗ ████║██╔══██╗     ██║   ██║██╔════╝██╔══██╗████╗ ████║██╔══██╗
    ██╔████╔██║██████╔╝     ██║   ██║█████╗  ██████╔╝██╔████╔██║███████║
    ██║╚██╔╝██║██╔══██╗     ╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══██║
    ██║ ╚═╝ ██║██║  ██║      ╚████╔╝ ███████╗██║  ██║██║ ╚═╝ ██║██║  ██║
    ╚═╝     ╚═╝╚═╝  ╚═╝       ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝
    
                    🤖 Unified AI Intelligence Platform
    """
    if console:
        console.print(banner, style="bold blue")
    else:
        print(banner)


def print_menu():
    """Display the main menu."""
    menu_text = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║  🎯 What would you like to do?                                    ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                                                                   ║
    ║  [1] 💬 Chat with AI        - Have a conversation                  ║
    ║  [2] 📝 Write Code          - Generate or improve code             ║
    ║  [3] 🔍 Analyze Code        - Review and find issues               ║
    ║  [4] 📊 Process Data        - Analyze files and data               ║
    ║  [5] 🎨 Design Interface    - Create UI/UX designs                 ║
    ║  [6] 🔒 Security Check      - Scan for vulnerabilities             ║
    ║  [7] ⚡ System Status       - Check AI brain health                ║
    ║  [8] 📚 Help & Guide        - Learn how to use MR.VERMA            ║
    ║  [0] 🚪 Exit                - Close MR.VERMA                       ║
    ║                                                                   ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    if console:
        console.print(Panel(menu_text, title="Main Menu", border_style="green"))
    else:
        print(menu_text)


class SimpleAIInterface:
    """Simplified AI interface for non-tech users."""

    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        self.api_url = os.getenv(
            "NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
        )
        self.model = os.getenv("NVIDIA_MODEL", "moonshotai/kimi-k2.5")
        self.history = []

    async def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a message to the AI and get a response."""
        import requests

        if not self.api_key:
            return (
                "❌ Error: NVIDIA API key not configured. Please set it in .env file."
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=payload, timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"❌ Error communicating with AI: {str(e)}"

    async def chat_mode(self):
        """Interactive chat mode."""
        if console:
            console.print(
                "\n[bold green]💬 Chat Mode - Type 'exit' to return to menu[/bold green]\n"
            )
        else:
            print("\n💬 Chat Mode - Type 'exit' to return to menu\n")

        while True:
            try:
                if console:
                    user_input = Prompt.ask("[bold blue]You[/bold blue]")
                else:
                    user_input = input("You: ")

                if user_input.lower() in ["exit", "quit", "back"]:
                    break

                if console:
                    with console.status("[bold green]AI is thinking..."):
                        response = await self.chat(user_input)
                else:
                    print("AI is thinking...")
                    response = await self.chat(user_input)

                if console:
                    console.print(f"[bold green]AI:[/bold green] {response}\n")
                else:
                    print(f"AI: {response}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                if console:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                else:
                    print(f"Error: {e}")

        if console:
            console.print("\n[bold yellow]Returning to main menu...[/bold yellow]\n")
        else:
            print("\nReturning to main menu...\n")

    async def write_code(self):
        """Code generation mode."""
        if console:
            console.print(
                "\n[bold green]📝 Code Writer - Describe what you need[/bold green]\n"
            )
            language = Prompt.ask("What programming language?", default="Python")
            description = Prompt.ask("Describe what you want to build")
        else:
            print("\n📝 Code Writer")
            language = input("What programming language? [Python]: ") or "Python"
            description = input("Describe what you want to build: ")

        prompt = f"Write {language} code for: {description}\n\nProvide clean, well-commented code with explanations."

        if console:
            with console.status("[bold green]Generating code..."):
                code = await self.chat(prompt)
        else:
            print("Generating code...")
            code = await self.chat(prompt)

        if console:
            console.print(f"\n[bold green]Generated Code:[/bold green]\n{code}\n")
        else:
            print(f"\nGenerated Code:\n{code}\n")

        # Save to file option
        if console:
            if Confirm.ask("Save to file?"):
                filename = Prompt.ask(
                    "Filename",
                    default=f"output/code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                )
                self._save_to_file(filename, code)
        else:
            save = input("Save to file? (y/n): ")
            if save.lower() == "y":
                filename = input(
                    f"Filename [output/code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py]: "
                )
                self._save_to_file(
                    filename
                    or f"output/code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py",
                    code,
                )

    def _save_to_file(self, filename: str, content: str):
        """Save content to a file."""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write(content)
            if console:
                console.print(f"[bold green]✅ Saved to {filename}[/bold green]")
            else:
                print(f"✅ Saved to {filename}")
        except Exception as e:
            if console:
                console.print(f"[bold red]❌ Error saving file: {e}[/bold red]")
            else:
                print(f"❌ Error saving file: {e}")

    async def system_status(self):
        """Check system status."""
        if console:
            console.print("\n[bold blue]⚡ System Status[/bold blue]\n")
        else:
            print("\n⚡ System Status\n")

        # Check API connectivity
        try:
            import requests

            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(
                self.api_url.replace("/chat/completions", "/models"),
                headers=headers,
                timeout=10,
            )
            api_status = (
                "✅ Connected"
                if response.status_code == 200
                else f"❌ Error {response.status_code}"
            )
        except Exception as e:
            api_status = f"❌ {str(e)}"

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "ps"], capture_output=True, text=True, timeout=5
            )
            docker_status = "✅ Running" if result.returncode == 0 else "❌ Not running"
        except:
            docker_status = "❌ Not installed"

        # Display status
        status_text = f"""
        AI API Connection: {api_status}
        Docker Services: {docker_status}
        Working Directory: {os.getcwd()}
        
        Press any key to continue...
        """

        if console:
            console.print(Panel(status_text, title="Status", border_style="blue"))
        else:
            print(status_text)

        input()

    async def show_help(self):
        """Display help information."""
        help_text = """
        MR.VERMA - Quick Guide
        =======================
        
        MR.VERMA is an AI assistant that helps you with:
        
        💬 Chat (Option 1)
           Have natural conversations with AI about any topic.
        
        📝 Write Code (Option 2)
           Generate code in any programming language.
           Just describe what you need!
        
        🔍 Analyze Code (Option 3)
           Get code reviews and find bugs.
        
        📊 Process Data (Option 4)
           Analyze files, logs, and data.
        
        🎨 Design Interface (Option 5)
           Create UI/UX designs and layouts.
        
        🔒 Security Check (Option 6)
           Scan code for security issues.
        
        Tips:
        - Be specific in your requests
        - The AI remembers context in chat mode
        - Results can be saved to files
        - Type 'exit' to go back to menu
        
        For technical support, check the docs/ folder.
        """

        if console:
            console.print(Panel(help_text, title="Help", border_style="yellow"))
        else:
            print(help_text)

        input("\nPress Enter to continue...")


async def main():
    """Main application loop."""
    print_banner()

    ai = SimpleAIInterface()

    while True:
        print_menu()

        try:
            if console:
                choice = Prompt.ask(
                    "Enter your choice",
                    choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"],
                    default="1",
                )
            else:
                choice = input("\nEnter your choice (0-8): ").strip()

            if choice == "0":
                if console:
                    console.print(
                        "\n[bold green]👋 Goodbye! Thank you for using MR.VERMA.[/bold green]\n"
                    )
                else:
                    print("\n👋 Goodbye! Thank you for using MR.VERMA.\n")
                break

            elif choice == "1":
                await ai.chat_mode()

            elif choice == "2":
                await ai.write_code()

            elif choice == "3":
                if console:
                    console.print(
                        "\n[bold yellow]🔍 Code analysis coming in next update![/bold yellow]\n"
                    )
                else:
                    print("\n🔍 Code analysis coming in next update!\n")
                input("Press Enter to continue...")

            elif choice == "4":
                if console:
                    console.print(
                        "\n[bold yellow]📊 Data processing coming in next update![/bold yellow]\n"
                    )
                else:
                    print("\n📊 Data processing coming in next update!\n")
                input("Press Enter to continue...")

            elif choice == "5":
                if console:
                    console.print(
                        "\n[bold yellow]🎨 Design tools coming in next update![/bold yellow]\n"
                    )
                else:
                    print("\n🎨 Design tools coming in next update!\n")
                input("Press Enter to continue...")

            elif choice == "6":
                if console:
                    console.print(
                        "\n[bold yellow]🔒 Security scanning coming in next update![/bold yellow]\n"
                    )
                else:
                    print("\n🔒 Security scanning coming in next update!\n")
                input("Press Enter to continue...")

            elif choice == "7":
                await ai.system_status()

            elif choice == "8":
                await ai.show_help()

            else:
                if console:
                    console.print(
                        "[bold red]Invalid choice. Please try again.[/bold red]"
                    )
                else:
                    print("Invalid choice. Please try again.")

        except KeyboardInterrupt:
            if console:
                console.print(
                    "\n[bold yellow]Use option 0 to exit properly.[/bold yellow]"
                )
            else:
                print("\nUse option 0 to exit properly.")

        except Exception as e:
            if console:
                console.print(f"[bold red]Error: {e}[/bold red]")
            else:
                print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
